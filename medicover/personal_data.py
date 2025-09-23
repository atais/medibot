from pydantic import BaseModel
from typing import Optional
from requests import Session
from ._constants import API

class PersonalData(BaseModel):
    mrn: int
    firstName: str
    homeClinicId: str

def personal_data(session: Session) -> PersonalData:
    response = session.get(f"{API}/personal-data/api/personal")
    response.raise_for_status()
    data = response.json()
    return PersonalData(**data)
