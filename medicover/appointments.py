from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel
from requests import Session

from ._constants import API


def _get_slot_search_type(speciality_id: int) -> str:
    if speciality_id == 519:
        return "DiagnosticProcedure"
    else:
        return "Standard"


class IdName(BaseModel):
    id: str
    name: str


class IdValue(BaseModel):
    id: str
    value: str


class Appointment(BaseModel):
    appointmentDate: datetime
    clinic: IdName
    doctor: Optional[IdName]
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
    region_ids: int
    specialty_ids: list[int]
    doctor_ids: Optional[list[int]] = None
    clinic_ids: Optional[list[int]] = None
    previous_id: Optional[str] = None
    start_time: str
    end_time: Optional[str] = None
    start_hour: Optional[int] = None
    end_hour: Optional[int] = None
    page: int = 1
    page_size: int = 5000
    is_overbooking_search_disabled: bool = False


def get_slots(
        session: Session,
        sp: SearchParams
) -> list[Appointment]:
    params = []
    params.append(("Page", sp.page))
    params.append(("PageSize", sp.page_size))
    params.append(("RegionIds", sp.region_ids))
    params.append(("SlotSearchType", _get_slot_search_type(sp.specialty_ids[0])))
    params.extend([("SpecialtyIds", x) for x in sp.specialty_ids])
    params.append(("StartTime", sp.start_time))
    params.append(("isOverbookingSearchDisabled", sp.is_overbooking_search_disabled))
    params.extend([("ClinicIds", x) for x in sp.clinic_ids or []])
    params.extend([("DoctorIds", x) for x in sp.doctor_ids or []])

    response = session.get(f"{API}/appointments/api/v2/search-appointments/slots", params=params)
    response.raise_for_status()
    items = response.json().get("items", [])
    result = [Appointment(**item) for item in items]

    if sp.end_time:
        end_time_dt = datetime.strptime(sp.end_time, "%Y-%m-%d")
        result = [r for r in result if r.appointmentDate.date() <= end_time_dt.date()]

    if sp.start_hour:
        result = [r for r in result if r.appointmentDate.hour >= sp.start_hour]

    if sp.end_hour:
        result = [r for r in result if r.appointmentDate.hour < sp.end_hour]

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
) -> FiltersResponse:
    params = []
    params.append(("RegionIds", region_ids))
    params.append(("SlotSearchType", _get_slot_search_type(specialty_ids[0])))
    params.extend([("SpecialtyIds", x) for x in specialty_ids])
    response = session.get(f"{API}/appointments/api/v2/search-appointments/filters", params=params)
    response.raise_for_status()
    data = FiltersResponse(**response.json())
    return data


class PersonAppointment(BaseModel):
    id: str
    clinic: IdName
    doctor: IdName
    region: IdName
    specialty: IdName
    visitType: str
    date: str
    state: str
    payment: Optional[str] = None


class PersonAppointmentsResponse(BaseModel):
    items: list[PersonAppointment]


def get_person_appointments(
        session: Session,
        appointment_state: str = "Planned",
        page: int = 1,
        page_size: int = 10
) -> PersonAppointmentsResponse:
    params = [
        ("AppointmentState", appointment_state),
        ("Page", page),
        ("PageSize", page_size)
    ]
    response = session.get(f"{API}/appointments/api/v2/person-appointments/appointments", params=params)
    response.raise_for_status()
    data = PersonAppointmentsResponse(**response.json())
    return data
