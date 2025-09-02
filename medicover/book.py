from typing import Optional

from pydantic import BaseModel, Field
from requests import Session

from .constants import API

class Metadata(BaseModel):
    appointmentSource: str = "Direct"

class Booking(BaseModel):
    bookingString: str
    reportingId: Optional[str] = None
    metadata: Metadata = Field(default_factory=Metadata)

class BookingResponse(BaseModel):
    appointmentId: int

def book(session: Session, booking_string: str) -> BookingResponse:
    url = f"{API}/appointments/api/v2/search-appointments/book-appointment"
    booking = Booking(bookingString=booking_string)
    response = session.post(url, json=booking.model_dump())
    response.raise_for_status()
    booking_json = response.json()
    return BookingResponse(**booking_json)