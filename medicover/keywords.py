from pydantic import BaseModel
from typing import List, Optional
from requests import Session
from ._constants import API

class Location(BaseModel):
    id: str
    value: str

class KeywordsResponse(BaseModel):
    regions: List[Location]

class Keyword(BaseModel):
    variant: str
    id: str
    value: str
    groupType: str
    hasShortPath: bool
    selectionPath: str

class KeywordsListResponse(BaseModel):
    keywords: list[Keyword]


def get_locations(session: Session) -> KeywordsResponse:
    response = session.get(f"{API}/service-selector-configurator-os/api/keywords")
    response.raise_for_status()
    data = response.json()
    return KeywordsResponse(**data)


def get_keywords(session: Session) -> KeywordsListResponse:
    response = session.get(f"{API}/service-selector-configurator-os/api/keywords")
    response.raise_for_status()
    data = response.json()
    return KeywordsListResponse(keywords=data.get("keywords", []))


def get_keyword_details(session: Session, keyword_id: str, region_id: str, mode: str = "sections") -> dict:
    if mode == "sections":
        url = f"{API}/service-selector-configurator-os/api/keywords/{keyword_id}/sections?regionId={region_id}"
    elif mode == "triage":
        url = f"{API}/service-selector-configurator-os/api/keywords/{keyword_id}/triage/flat?regionId={region_id}"
    else:
        raise ValueError("mode must be 'sections' or 'triage'")
    response = session.get(url)
    response.raise_for_status()
    return response.json()
