from fastapi import HTTPException
from typing import List
from sqlalchemy import select
from config.db import conn
from models.survey import surveys
from models.section import sections
from models.question import questions
from models.options import options
from models.question_type import question_types
from schemas.survey import Survey, SurveyStructuration


def get_all_surveys():
    stmt = select(
        surveys.c.id_survey,
        surveys.c.survey_name,
        surveys.c.creation_date,
        surveys.c.survey_state,
        surveys.c.configuration_date,
    ).order_by(surveys.c.id_survey.asc())

    result = conn.execute(stmt).fetchall()
    return [dict(row._mapping) for row in result]


def get_all_question_types():
    stmt = select(question_types).order_by(question_types.c.id_question_type.asc())
    result = conn.execute(stmt).fetchall()

    return [dict(row._mapping) for row in result]


def get_survey_by_id(id: int):
    stmt = select(surveys).where(surveys.c.id_survey == id)

    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Survey not found")

    return dict(result._mapping)


def get_structuration(id: int):
    j = sections.outerjoin(
        questions, sections.c.id_section == questions.c.id_section
    ).outerjoin(options, questions.c.id_question == options.c.id_question)

    stmt = (
        select(
            sections.c.id_section,
            sections.c.section_name,
            questions.c.id_question,
            questions.c.question_name,
            questions.c.id_question_type,
            options.c.id_option,
            options.c.option_name,
        )
        .select_from(j)
        .where(sections.c.id_survey == id)
        .order_by(sections.c.id_section.asc())
    )

    result = conn.execute(stmt).fetchall()

    if not result:
        return []

    structuration_dict = {}

    for row in result:
        section_id = row.id_section

        if section_id not in structuration_dict:
            structuration_dict[section_id] = {
                "id_section": section_id,
                "section_name": row.section_name,
                "section_questions": [],
            }

        if not row.id_question:
            continue

        section_questions = structuration_dict[section_id]["section_questions"]

        existing_question = next(
            (q for q in section_questions if q["id_question"] == row.id_question), None
        )

        if not existing_question:
            question_data = {
                "id_question": row.id_question,
                "question_name": row.question_name,
                "id_question_type": row.id_question_type,
                "options": [],
            }
            section_questions.append(question_data)
        else:
            question_data = existing_question

        if row.id_option and row.option_name:
            question_data["options"].append(
                {
                    "id_option": row.id_option,
                    "option_name": row.option_name,
                }
            )

    return list(structuration_dict.values())


def create_survey(survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

    stmt = surveys.insert().values(new_survey).returning(surveys)
    result = conn.execute(stmt).fetchone()

    conn.commit()

    return dict(result._mapping)


def save_structuration_changes(
    id: int, survey_structuration: List[SurveyStructuration]
):
    existing_structuration = get_structuration(id)

    # CASO 1: insertar todo si no existe estructura previa
    if len(existing_structuration) == 0:
        for section in survey_structuration:
            new_section = {"section_name": section.section_name, "id_survey": id}
            section_stmt = (
                sections.insert().values(new_section).returning(sections.c.id_section)
            )
            section_result = conn.execute(section_stmt).fetchone()
            section_id = section_result.id_section

            for question in section.section_questions:
                new_question = {
                    "question_name": question.question_name,
                    "id_question_type": question.id_question_type,
                    "id_section": section_id,
                }
                question_stmt = (
                    questions.insert()
                    .values(new_question)
                    .returning(questions.c.id_question)
                )
                question_result = conn.execute(question_stmt).fetchone()
                question_id = question_result.id_question

                # insertar opciones (si las trae)
                for opt in getattr(question, "options", []):
                    new_opt = {"option_name": getattr(opt, "option_name", None)}
                    # asociar id_question al insert
                    new_opt["id_question"] = question_id
                    conn.execute(options.insert().values(new_opt))

        conn.commit()
        return get_structuration(id)

    # CASO 2: ya existe estructura → actualizar/eliminar/insertar según corresponda
    else:
        # ids existentes en BD
        existing_section_ids = [
            (
                section["id_section"]
                if isinstance(section, dict)
                else getattr(section, "id_section", None)
            )
            for section in existing_structuration
        ]

        # ids que vienen en el payload (solo los que tienen id != 0 / None)
        new_section_ids = [
            section.id_section
            for section in survey_structuration
            if getattr(section, "id_section", None) not in (None, 0)
        ]

        # secciones a borrar
        sections_to_delete = set(existing_section_ids) - set(new_section_ids)

        if sections_to_delete:
            # eliminar opciones y preguntas relacionadas podría ser necesario si no hay FKs con cascade
            # eliminar preguntas relacionadas
            delete_questions_for_sections = questions.delete().where(
                questions.c.id_section.in_(sections_to_delete)
            )
            conn.execute(delete_questions_for_sections)
            # eliminar secciones
            delete_sec_stmt = sections.delete().where(
                sections.c.id_section.in_(sections_to_delete)
            )
            conn.execute(delete_sec_stmt)
            conn.commit()

        # Recorremos todas las secciones recibidas: insertar nuevas o actualizar existentes
        for section in survey_structuration:
            # obtener/crear section_id
            incoming_sec_id = getattr(section, "id_section", 0) or 0

            if (
                incoming_sec_id in (0, None)
                or incoming_sec_id not in existing_section_ids
            ):
                # insertar nueva sección
                new_section = {"section_name": section.section_name, "id_survey": id}
                section_stmt = (
                    sections.insert()
                    .values(new_section)
                    .returning(sections.c.id_section)
                )
                section_result = conn.execute(section_stmt).fetchone()
                section_id = section_result.id_section
            else:
                # actualizar sección existente
                section_id = incoming_sec_id
                update_sec_stmt = (
                    sections.update()
                    .where(sections.c.id_section == section_id)
                    .values(section_name=section.section_name)
                )
                conn.execute(update_sec_stmt)

            # -----------------------------
            # PREGUNTAS: obtener existentes en BD para esta sección
            existing_questions_stmt = select(questions).where(
                questions.c.id_section == section_id
            )
            existing_questions = conn.execute(existing_questions_stmt).fetchall()
            existing_question_ids = [q.id_question for q in existing_questions]

            # ids de preguntas que vienen en payload (no considerar 0/None como existentes)
            new_question_ids = [
                q.id_question
                for q in section.section_questions
                if getattr(q, "id_question", None) not in (None, 0)
            ]

            # preguntas a borrar (las que están en BD pero no vienen en payload)
            questions_to_delete = set(existing_question_ids) - set(new_question_ids)
            if questions_to_delete:
                # primero eliminar opciones de esas preguntas (si no hay cascade)
                delete_opts_for_q = options.delete().where(
                    options.c.id_question.in_(questions_to_delete)
                )
                conn.execute(delete_opts_for_q)
                # eliminar preguntas
                delete_q_stmt = questions.delete().where(
                    questions.c.id_question.in_(questions_to_delete)
                )
                conn.execute(delete_q_stmt)

            # Insertar o actualizar preguntas recibidas
            for question in section.section_questions:
                incoming_q_id = getattr(question, "id_question", 0) or 0

                if (
                    incoming_q_id in (0, None)
                    or incoming_q_id not in existing_question_ids
                ):
                    # insertar nueva pregunta
                    new_question = {
                        "question_name": question.question_name,
                        "id_question_type": question.id_question_type,
                        "id_section": section_id,
                    }
                    question_stmt = (
                        questions.insert()
                        .values(new_question)
                        .returning(questions.c.id_question)
                    )
                    q_result = conn.execute(question_stmt).fetchone()
                    question_id = q_result.id_question
                else:
                    # actualizar pregunta existente
                    question_id = incoming_q_id
                    update_q_stmt = (
                        questions.update()
                        .where(questions.c.id_question == question_id)
                        .values(
                            question_name=question.question_name,
                            id_question_type=question.id_question_type,
                        )
                    )
                    conn.execute(update_q_stmt)

                # -----------------------------
                # OPCIONES: aqui estaba el fallo que señalaste — ahora manejamos opciones para preguntas EXISTENTES
                # obtener opciones existentes en BD para la pregunta actual
                existing_opts_stmt = select(options).where(
                    options.c.id_question == question_id
                )
                existing_opts = conn.execute(existing_opts_stmt).fetchall()
                existing_opt_ids = [o.id_option for o in existing_opts]

                # ids de opciones que vienen en payload (no considerar 0/None como existentes)
                new_opt_ids = [
                    opt.id_option
                    for opt in getattr(question, "options", [])
                    if getattr(opt, "id_option", None) not in (None, 0)
                ]

                # opciones a borrar: las que están en BD pero no vienen en el payload
                opts_to_delete = set(existing_opt_ids) - set(new_opt_ids)
                if opts_to_delete:
                    delete_opt_stmt = options.delete().where(
                        options.c.id_option.in_(opts_to_delete)
                    )
                    conn.execute(delete_opt_stmt)

                # ahora insertar o actualizar cada opción que viene en el payload
                for opt in getattr(question, "options", []):
                    incoming_opt_id = getattr(opt, "id_option", 0) or 0

                    if (
                        incoming_opt_id in (0, None)
                        or incoming_opt_id not in existing_opt_ids
                    ):
                        # insertar nueva opción y asociarla a la pregunta actual
                        new_opt = {
                            "option_name": getattr(opt, "option_name", None),
                            "id_question": question_id,
                        }
                        conn.execute(options.insert().values(new_opt))
                    else:
                        # actualizar opción existente
                        update_opt_stmt = (
                            options.update()
                            .where(options.c.id_option == incoming_opt_id)
                            .values(option_name=getattr(opt, "option_name", None))
                        )
                        conn.execute(update_opt_stmt)

        # confirmar todos los cambios
        conn.commit()
        return get_structuration(id)


def update_survey(id: int, survey: Survey):
    new_survey = survey.model_dump()

    stmt = (
        surveys.update()
        .where(surveys.c.id_survey == id)
        .values(new_survey)
        .returning(surveys)
    )

    result = conn.execute(stmt).fetchone()
    conn.commit()

    if not result:
        raise HTTPException(status_code=404, detail="Survey not found")

    return dict(result._mapping)


def change_survey_state(id: int):
    stmt = select(surveys).where(surveys.c.id_survey == id)
    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Survey not found")

    new_state = 0 if result.survey_state == 1 else 1

    update_stmt = (
        surveys.update()
        .where(surveys.c.id_survey == id)
        .values(survey_state=new_state)
        .returning(surveys)
    )

    updated = conn.execute(update_stmt).fetchone()
    conn.commit()

    return updated.survey_state


def delete_survey_by_id(id: int):
    stmt = surveys.delete().where(surveys.c.id_survey == id).returning(surveys)
    result = conn.execute(stmt).fetchone()
    conn.commit()

    if not result:
        raise HTTPException(status_code=404, detail="Survey not found")

    return result.id_survey
