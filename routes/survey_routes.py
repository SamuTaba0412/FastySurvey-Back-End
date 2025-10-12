from fastapi import APIRouter
from schemas.survey import Survey
from controllers.survey_controller import (
    get_all_surveys,
    get_survey_by_id,
    create_survey,
    update_survey,
    change_survey_state
)

survey = APIRouter(prefix="/surveys", tags=["Surveys"])


@survey.get("/")
def get_surveys():
    return get_all_surveys()


@survey.get("/{id}")
def get_survey(id: int):
    return get_survey_by_id(id)


@survey.post("/")
def post_survey(survey: Survey):
    return create_survey(survey)


@survey.put("/{id}")
def put_survey(id: int, survey: Survey):
    return update_survey(id, survey)


@survey.put("/state/{id}")
def put_state_survey(id: int):
    return change_survey_state(id)
