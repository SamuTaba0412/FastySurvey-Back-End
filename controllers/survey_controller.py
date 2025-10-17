from fastapi import HTTPException
from sqlalchemy import select
from config.db import conn
from models.survey import surveys
from models.section import sections
from models.question import questions
from models.options import options
from schemas.survey import Survey


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
    j = sections.join(
        questions, sections.c.id_section == questions.c.id_section
    ).join(
        options, questions.c.id_question == options.c.id_question
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

    structuration_dict = {}
    for row in result:
        section_id = row.id_section

        if section_id not in structuration_dict:
            structuration_dict[section_id] = {
                "sectionName": row.section_name,
                "sectionQuestions": []
            }

        question_data = {
            "questionDescription": row.question_description,
            "questionType": row.question_type
        }

        if getattr(row, "option_description", None):
            existing_question = next(
                (q for q in structuration_dict[section_id]["sectionQuestions"] 
                if q["questionDescription"] == row.question_description),
                None
            )

            if existing_question:
                existing_question.setdefault("options", []).append(row.option_description)
            else:
                question_data["options"] = [row.option_description]
                structuration_dict[section_id]["sectionQuestions"].append(question_data)
        else:
            structuration_dict[section_id]["sectionQuestions"].append(question_data)

    return list(structuration_dict.values())


def create_survey(survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

    stmt = surveys.insert().values(new_survey).returning(surveys)
    result = conn.execute(stmt).fetchone()

    conn.commit()

    return dict(result._mapping)


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