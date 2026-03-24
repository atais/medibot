from ._constants import API, LOGIN, ONLINE24
from .appointments import get_slots, get_filters, get_person_appointments
from .auth import login, refresh
from .book import book, delete
from .personal_data import personal_data
from .referrals import get_referrals

__all__ = [
    "API",
    "LOGIN",
    "ONLINE24",
    "get_slots",
    "get_filters",
    "get_person_appointments",
    "login",
    "refresh",
    "book",
    "delete",
    "personal_data",
    "get_referrals",
]
