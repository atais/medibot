import requests
from requests import Session
from dataclasses import dataclass


api = "https://api-gateway-online24.medicover.pl"
login = "https://login-online24.medicover.pl/"

@dataclass
class Profile:
    mrn: int
    name: str
    surname: str
    isChild: bool
    accessLevel: str
    sourceSystem: str
    isMain: bool

def me( session: Session) -> Profile:
    url = f"{login}api/v4/available-profiles/me"
    response = session.get(url)
    response.raise_for_status()
    profiles_json = response.json()
    return Profile(**profiles_json[0])

def search_appointments(
        session: Session,
        page: int,
        page_size: int,
        region_ids: int,
        slot_search_type: str,
        specialty_ids: list[int],
        start_time: str,
        is_overbooking_search_disabled: bool
) -> requests.Response:
    params = []
    params.append(("Page", page))
    params.append(("PageSize", page_size))
    params.append(("RegionIds", region_ids))
    params.append(("SlotSearchType", slot_search_type))
    params.extend([("SpecialtyIds", x) for x in specialty_ids])
    params.append(("StartTime", start_time))
    params.append(("isOverbookingSearchDisabled", is_overbooking_search_disabled))

    return session.get(f"{api}/appointments/api/v2/search-appointments/slots", params=params)

