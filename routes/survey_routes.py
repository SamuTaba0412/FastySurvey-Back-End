from fastapi import APIRouter
from controllers.survey_controller import get_all_surveys

survey = APIRouter(prefix="/surveys", tags=["Surveys"])

@survey.get("/")
def get_surveys():
    return get_all_surveys()