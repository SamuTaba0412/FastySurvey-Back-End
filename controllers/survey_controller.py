from fastapi import HTTPException
from typing import List
from sqlalchemy import select
from config.db import conn
from models.survey import surveys
from models.section import sections
from models.question import questions
from models.options import options
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


def get_survey_by_id(id: int):
    stmt = select(surveys).where(surveys.c.id_survey == id)

    result = conn.execute(stmt).fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Survey not found")

    return dict(result._mapping)


def get_structuration(id: int):
    j = (
        sections
        .outerjoin(questions, sections.c.id_section == questions.c.id_section)
        .outerjoin(options, questions.c.id_question == options.c.id_question)
    )

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
            (q for q in section_questions if q["id_question"] == row.id_question),
            None
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
            question_data["options"].append({
                "id_option": row.id_option,
                "option_name": row.option_name,
            })

    return list(structuration_dict.values())


def create_survey(survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

    stmt = surveys.insert().values(new_survey).returning(surveys)
    result = conn.execute(stmt).fetchone()

    conn.commit()

    return dict(result._mapping)


def save_structuration_changes(id: int, survey_structuration: List[SurveyStructuration]):
    existing_structuration = get_structuration(id)

    if len(existing_structuration) == 0:
        for section in survey_structuration:
            new_section = {
                "section_name": section.section_name,
                "id_survey": id
            }

            section_stmt = sections.insert().values(new_section).returning(sections.c.id_section)
            section_result = conn.execute(section_stmt).fetchone()

            for question in section.section_questions:
                new_question = {
                    "question_name": question.question_name,
                    "id_question_type": question.id_question_type,
                    "id_section": section_result.id_section
                }

                question_stmt = questions.insert().values(new_question).returning(questions.c.id_question)
                question_result = conn.execute(question_stmt).fetchone()

                if question.options:
                    for option in question.options:
                        new_option = {
                            "option_name": option.option_name,
                            "id_question": question_result.id_question
                        }

                        option_stmt = options.insert().values(new_option).returning(options.c.id_option)
                        conn.execute(option_stmt).fetchone()

        conn.commit()

        new_structuration = get_structuration(id)
        return new_structuration

    return existing_structuration


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
