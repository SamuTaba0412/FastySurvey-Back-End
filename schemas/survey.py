from typing import Optional, Text
from pydantic import BaseModel
from datetime import date

class Survey(BaseModel):
    survey_name: str
    creation_date: date
    configuration_date: Optional[date] = None
    survey_state: Optional[int] = 1
    introductory_text: Optional[Text] = None
    terms_conditions: Optional[Text] = None