from typing import Optional
from pydantic import BaseModel
from datetime import date

class Role(BaseModel):
    role_name: str
    creation_date: date
    role_state: Optional[int] = 1
    update_date: Optional[date] = None