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
    return dict(result._mapping)


def create_survey(survey: Survey):
    new_survey = survey.model_dump(exclude_none=True)

    stmt = surveys.insert().values(new_survey).returning(surveys)
    result = conn.execute(stmt).fetchone()

    return dict(result._mapping)
