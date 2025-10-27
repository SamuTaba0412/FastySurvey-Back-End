from fastapi import APIRouter
from typing import List
from schemas.survey import Survey, SurveyStructuration
from controllers.survey_controller import (
    get_all_surveys,
    get_survey_by_id,
    get_structuration,
    save_structuration_changes,
    create_survey,
    update_survey,
    change_survey_state,
    delete_survey_by_id,
)

survey = APIRouter(prefix="/surveys", tags=["Surveys"])


@survey.get("/")
def get_surveys():
    return get_all_surveys()


@survey.get("/{id}")
def get_survey(id: int):
    return get_survey_by_id(id)


@survey.get("/structuration/{id}")
def get_survey_structuration(id: int):
    return get_structuration(id)


@survey.post("/")
def post_survey(survey: Survey):
    return create_survey(survey)


@survey.put("/structuration/{id}")
def put_survey_structuration(id: int, survey_structuration: List[SurveyStructuration]):
    return save_structuration_changes(id, survey_structuration)


@survey.put("/{id}")
def put_survey(id: int, survey: Survey):
    return update_survey(id, survey)


@survey.put("/state/{id}")
def put_state_survey(id: int):
    return change_survey_state(id)


@survey.delete("/{id}")
def delete_survey(id: int):
    return delete_survey_by_id(id)
