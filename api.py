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

    return session.get(f"{_h}/appointments/api/v2/search-appointments/slots", params=params)

# appointments/api/v2/search-appointments/slots?Page=1&PageSize=5000&RegionIds=204&SlotSearchType=Standard&SpecialtyIds=163&StartTime=2025-08-29&isOverbookingSearchDisabled=false
# appointments/api/v2/search-appointments/slots?Page=1&PageSize=5000&RegionIds=204&SlotSearchType=Standard&SpecialtyIds=70770&StartTime=2025-08-29&isOverbookingSearchDisabled=false