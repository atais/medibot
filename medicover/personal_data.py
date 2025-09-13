from pydantic import BaseModel
from typing import Optional
from requests import Session
from ._constants import API

class Address(BaseModel):
    town: Optional[str]
    postCode: Optional[str]
    street: Optional[str]
    houseNumber: Optional[str]
    apartmentNumber: Optional[str]

class PersonalData(BaseModel):
    mrn: int
    firstName: str
    lastName: str
    birthDate: str
    gender: Optional[str]
    homeClinicName: Optional[str]
    homeClinicId: Optional[str]
    personalIdentityNumber: Optional[str]
    homePhoneNumber: Optional[str]
    workPhoneNumber: Optional[str]
    mobilePhoneNumber: Optional[str]
    mobilePrefixValue: Optional[str]
    email: Optional[str]
    residenceAddress: Optional[Address]
    correspondenceAddress: Optional[Address]
    smsNotifyAcceptance: Optional[bool]
    mailNotifyAcceptance: Optional[bool]
    passportNumber: Optional[str]
    motherPersonalIdentityNumber: Optional[str]
    incapacitated: Optional[bool]
    isChild: Optional[bool]
    isVip: Optional[bool]
    refunds: Optional[bool]
    termGuarantee: Optional[bool]
    mobilePrefixCountryId: Optional[str]
    isFirstTimeDentalVisit: Optional[bool]
    dentalSurveyActive: Optional[bool]
    personId: Optional[int]
    isUserPozOnly: Optional[bool]

def personal_data(session: Session) -> PersonalData:
    response = session.get(f"{API}/personal-data/api/personal")
    response.raise_for_status()
    data = response.json()
    return PersonalData(**data)
