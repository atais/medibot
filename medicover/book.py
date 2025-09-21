from typing import Optional

from pydantic import BaseModel
from requests import Session

from ._constants import API


class BookingResponse(BaseModel):
    appointmentId: int

class Response(BaseModel):
    status: str
    message: Optional[str] = None
    errorDetails: Optional[str] = None

def book(session: Session, booking_string: str, old_id: Optional[str] = None):
    if old_id:
        url = f"{API}/appointments/api/v2/person-appointments/reschedule-appointment"
        payload = {
            "oldAppointmentString": old_id,
            "bookingString": booking_string
        }
        response = session.post(url, json=payload)
        response.raise_for_status()
        return Response(**response.json())
    else:
        url = f"{API}/appointments/api/v2/search-appointments/book-appointment"
        payload = {
            "metadata": {
                "appointmentSource": "Direct"
            },
            "bookingString": booking_string
        }
        response = session.post(url, json=payload)
        response.raise_for_status()
        booking_json = response.json()
        return BookingResponse(**booking_json)


def delete(session: Session, aid: str) -> None:
    url = f"{API}/appointments/api/v2/person-appointments/appointments/{aid}"
    response = session.delete(url)
    response.raise_for_status()
