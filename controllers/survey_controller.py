from fastapi import HTTPException
from sqlalchemy import select
from config.db import conn
from models.survey import surveys
from schemas.survey import Survey


def get_all_surveys():
    stmt = select(
        surveys.c.id_survey,
        surveys.c.survey_name,
        surveys.c.creation_date,
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


def create_survey(survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

    stmt = surveys.insert().values(new_survey).returning(surveys)
    result = conn.execute(stmt).fetchone()

    conn.commit()

    return dict(result._mapping)


def update_survey(id: int, survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

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