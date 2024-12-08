import requests
from requests import Session

_h = "https://api-gateway-online24.medicover.pl"


def initial_filters(
        session: Session,
        region_id: int
) -> requests.Response:
    params = [("RegionId", region_id)]
    return session.get(f"{_h}/service-selector-configurator/api/search-appointments/filters", params=params)


def search_appointments(
        session: Session,
        page: int,
        page_size: int,
        service_type: str,
        slot_search_type: int,
        start_time: str,
        visit_type: str,
        region_ids: int,
        specialty_ids: list[int],
) -> requests.Response:
    params = []
    params.append(("Page", page))
    params.append(("PageSize", page_size))
    params.append(("RegionIds", region_ids))
    params.append(("ServiceType", service_type))
    params.append(("SlotSearchType", slot_search_type))
    params.extend([("SpecialtyIds", x) for x in specialty_ids])
    params.append(("StartTime", start_time))
    params.append(("VisitType", visit_type))

    return session.get(f"{_h}/appointments/api/search-appointments/slots", params=params)
