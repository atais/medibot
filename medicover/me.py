from pydantic import BaseModel
from requests import Session

from .constants import LOGIN


class Profile(BaseModel):
    mrn: int
    name: str
    surname: str
    isChild: bool
    accessLevel: str
    sourceSystem: str
    isMain: bool


def me(session: Session) -> Profile:
    url = f"{LOGIN}/api/v4/available-profiles/me"
    response = session.get(url)
    response.raise_for_status()
    profiles_json = response.json()
    return Profile(**profiles_json[0])
