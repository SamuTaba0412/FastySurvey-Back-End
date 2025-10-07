from typing import List, Optional
from pydantic import BaseModel
from datetime import date

class User(BaseModel):
    names: str
    last_names: str
    identification_type: str
    identification: str
    email: str
    creation_date: date
    update_date: Optional[date] = None
    user_state: Optional[int] = 1
    id_role: int