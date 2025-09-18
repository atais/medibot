from typing import Optional, List

from pydantic import BaseModel
from requests import Session

from ._constants import API


class IdName(BaseModel):
    id: str
    name: str


class IdValue(BaseModel):
    id: str
    value: str


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


class SearchParams(BaseModel):
    specialty_ids: list[int]
    doctor_ids: Optional[list[int]] = None
    clinic_ids: Optional[list[int]] = None
    start_time: str
    page: int = 1
    page_size: int = 5000
    region_ids: int = 204
    slot_search_type: str = "Standard"
    is_overbooking_search_disabled: bool = False


def get_slots(
        session: Session,
        specialty_ids: list[int],
        start_time: str,
        clinic_ids: list[int] = None,
        doctor_ids: list[int] = None,
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
    if clinic_ids is not None:
        params.extend([("ClinicIds", x) for x in clinic_ids])
    if doctor_ids is not None:
        params.extend([("DoctorIds", x) for x in doctor_ids])
    response = session.get(f"{API}/appointments/api/v2/search-appointments/slots", params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    result = [Appointment(**item) for item in items]
    return result


class Specialty(BaseModel):
    id: str
    value: str
    type: str
    kind: str


class FiltersResponse(BaseModel):
    specialties: list[Specialty]
    clinics: list[IdValue]
    doctors: list[IdValue]
    regions: list[IdValue]


def get_filters(
        session: Session,
        specialty_ids: list[int],
        region_ids: int = 204,
        slot_search_type: str = "Standard",
) -> FiltersResponse:
    params = []
    params.append(("RegionIds", region_ids))
    params.append(("SlotSearchType", slot_search_type))
    params.extend([("SpecialtyIds", x) for x in specialty_ids])
    response = session.get(f"{API}/appointments/api/v2/search-appointments/filters", params=params)
    response.raise_for_status()
    data = FiltersResponse(**response.json())
    return data
