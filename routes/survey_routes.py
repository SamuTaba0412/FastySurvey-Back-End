from fastapi import APIRouter
from schemas.survey import Survey
from controllers.survey_controller import get_all_surveys, get_survey_by_id, create_survey

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