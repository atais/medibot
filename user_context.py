import logging
import uuid
from typing import Callable, Optional, List, Set

import requests
from fake_useragent import UserAgent
from pydantic import BaseModel
from requests.adapters import HTTPAdapter

import medicover
from medicover.personal_data import PersonalData

_default_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-PL;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class CookieInfo(BaseModel):
    name: str
    value: str
    domain: Optional[str] = None
    path: str = "/"
    secure: bool = False
    expires: Optional[int] = None


class UserData(BaseModel):
    username: str
    password: str
    user_agent: str = UserAgent().random
    device_id: str = str(uuid.uuid4())
    bearer_token: str = ""
    refresh_token: str = ""
    fcm_token: Set[str] = set()
    profile: Optional[PersonalData] = None
    cookie_jar: List[CookieInfo] = []


class UserContext(HTTPAdapter):
    def __init__(
            self,
            data: UserData,
            on_update: Optional[Callable[['UserContext'], None]] = None,
            *args,
            **kwargs
    ):
        self.data = data
        self.on_update = on_update

        self.session = requests.Session()
        self.session.headers.update(_default_headers)
        self.session.mount('https://', self)
        self.session.mount('http://', self)
        self.session.headers["User-Agent"] = self.data.user_agent
        self.session.headers["authorization"] = "Bearer " + self.data.bearer_token

        # Restore each cookie
        for cookie in self.data.cookie_jar:
            self.session.cookies.set(
                name=cookie.name,
                value=cookie.value,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure,
                expires=cookie.expires
            )

        super().__init__(*args, **kwargs)

    @classmethod
    def init(cls,
             username: str,
             password: str,
             on_update: Optional[Callable[['UserContext'], None]] = None,
             *args,
             **kwargs
             ):
        user_data = UserData(username=username, password=password)
        return cls(data=user_data, on_update=on_update, *args, **kwargs)

    def _login(self) -> None:
        logging.info(f"Logging in {self.data.username}")
        at, rt = medicover.login(self.data.username, self.data.password, self.data.device_id, self.session)
        self.data.bearer_token = at
        self.data.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.data.bearer_token
        if self.on_update:
            self.on_update(self)

    def _refresh(self) -> None:
        logging.info(f"Keep alive {self.data.username}")
        at, rt = medicover.refresh(self.data.refresh_token, self.session)
        self.data.bearer_token = at
        self.data.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.data.bearer_token
        if self.on_update:
            self.on_update(self)

    def send(self, request, **kwargs):
        response = super().send(request, **kwargs)

        if response.status_code == 401:
            try:
                if self.data.bearer_token != "":
                    logging.warning(f"401 {self.data.username} no #1, trying to reload token")
                    self._refresh()
                    request.headers["authorization"] = "Bearer " + self.data.bearer_token
                    response = super().send(request, **kwargs)
                else:
                    logging.warning(f"401 {self.data.username} no #1, its not possible to reload token")
            except TypeError:
                pass
            finally:
                if response.status_code == 401:
                    logging.warning(f"401 {self.data.username} no #2, trying to login")
                    self.session.headers["authorization"] = ""
                    self.session.cookies.clear_session_cookies()
                    self._login()
                    request.headers["authorization"] = "Bearer " + self.data.bearer_token
                    response = super().send(request, **kwargs)
                    if response.status_code == 401:
                        raise Exception(f"401 {self.data.username} no #3, there is some issue with your account")

        return response
