import requests
from requests import Session
from pydantic import BaseModel
from typing import Optional, List

api = "https://api-gateway-online24.medicover.pl"
login = "https://login-online24.medicover.pl/"


class Profile(BaseModel):
    mrn: int
    name: str
    surname: str
    isChild: bool
    accessLevel: str
    sourceSystem: str
    isMain: bool


def me(session: Session) -> Profile:
    url = f"{login}api/v4/available-profiles/me"
    response = session.get(url)
    response.raise_for_status()
    profiles_json = response.json()
    return Profile(**profiles_json[0])


class IdName(BaseModel):
    id: str
    name: str


class Appointment(BaseModel):
    appointmentDate: str
    clinic: IdName
    doctor: IdName
    doctorLanguages: List[IdName]
    specialty: IdName
    visitType: str
    bookingString: str
    isOverbooking: bool
    isOpticsAvailable: bool
    isPharmaAvailable: bool
    sysSpecialtyConsultationTypeId: str
    visitOrigin: str
    serviceId: Optional[str]


def search(
        session: Session,
        specialty_ids: list[int],
        start_time: str,
        page: int = 1,
        page_size: int = 5000,
        region_ids: int = 204,
        slot_search_type: str = "Standard",
        is_overbooking_search_disabled: bool = False
) -> list[Appointment]:
    params = []
    params.append(("Page", page))
    params.append(("PageSize", page_size))
    params.append(("RegionIds", region_ids))
    params.append(("SlotSearchType", slot_search_type))
    params.extend([("SpecialtyIds", x) for x in specialty_ids])
    params.append(("StartTime", start_time))
    params.append(("isOverbookingSearchDisabled", is_overbooking_search_disabled))

    response = session.get(f"{api}/appointments/api/v2/search-appointments/slots", params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    print(items)
    appointments = [Appointment(**item) for item in items]
    return appointments
