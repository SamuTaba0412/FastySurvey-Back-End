from fastapi import APIRouter
from controllers.survey_controller import get_all_surveys, get_survey_by_id

survey = APIRouter(prefix="/surveys", tags=["Surveys"])

@survey.get("/")
def get_surveys():
    return get_all_surveys()

@survey.get("/{id}")
def get_survey(id: int):
    return get_survey_by_id(id)