from typing import List, Optional, Text
from pydantic import BaseModel
from datetime import date

class Survey(BaseModel):
    survey_name: str
    creation_date: date
    configuration_date: Optional[date] = None
    survey_state: Optional[int] = 1
    introductory_text: Optional[Text] = None
    terms_conditions: Optional[Text] = None

class Option(BaseModel):
    id_option: Optional[int] = None
    option_name: str
    id_question: Optional[int] = None

class Question(BaseModel):
    id_question: Optional[int] = None
    question_name: str
    id_question_type: int
    options: Optional[List[Option]] = None
    id_section: Optional[int] = None

class SurveyStructuration(BaseModel):
    id_section: Optional[int] = None
    section_name: str
    section_questions: List[Question]