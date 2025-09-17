from typing import List, Optional

from pydantic import BaseModel
from requests import Session

from ._constants import API


class IdName(BaseModel):
    id: str
    name: str

class ServicePart(BaseModel):
    hasResult: bool
    isDone: bool
    executionDate: Optional[str]
    serviceStatus: str


class ServiceItem(BaseModel):
    service: IdName
    canMakeAnAppointment: bool
    isAnyServiceStatusClassifiedAsDone: bool
    serviceSpecialty: Optional[str]
    makeAnAppointmentMessage: Optional[str]
    serviceParts: List[ServicePart]


class ReferralItem(BaseModel):
    id: str
    issueDate: str
    expirationDate: str
    referralType: str
    referralStatus: str
    doctor: IdName
    specialty: Optional[IdName]
    canMakeAnAppointment: bool
    regionId: str
    isUrgent: bool
    isNew: bool
    hasAnyResult: bool
    services: List[ServiceItem]
    referralNumber: int
    canDownloadReferral: bool


class ReferralsResponse(BaseModel):
    page: int
    pageSize: int
    count: int
    items: List[ReferralItem]


# --- API call function ---
def get_referrals(
        session: Session,
        page: int = 1,
        page_size: int = 10,
        referral_statuses: List[str] = ["Arranged", "Requested", "PartlyRealized"]
) -> ReferralsResponse:
    url = f"{API}/referrals/api/referrals"
    params = {
        "page": page,
        "pageSize": page_size,
    }
    for status in referral_statuses:
        params.setdefault("referralStatuses", []).append(status)
    response = session.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return ReferralsResponse(**data)
