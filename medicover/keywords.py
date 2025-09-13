from pydantic import BaseModel
from typing import List, Optional
from requests import Session
from ._constants import API

class Location(BaseModel):
    id: str
    value: str

class KeywordsResponse(BaseModel):
    homeLocation: Location
    regions: List[Location]


def get_locations(session: Session) -> KeywordsResponse:
    response = session.get(f"{API}/service-selector-configurator-os/api/keywords")
    response.raise_for_status()
    data = response.json()
    return KeywordsResponse(**data)
