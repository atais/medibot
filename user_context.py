import logging
import uuid

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter

import medicover

_default_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-PL;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class UserContext(HTTPAdapter):
    def __init__(
            self,
            username: str,
            password: str,
            user_agent: str = None,
            device_id: str = None,
            bearer_token: str = "",
            refresh_token: str = "",
            fcm_token: str = "",
            *args,
            **kwargs
    ):
        self.username = username
        self.password = password

        self.user_agent: str = user_agent if user_agent is not None else UserAgent().random
        self.device_id: str = device_id if device_id is not None else str(uuid.uuid4())
        self.bearer_token: str = bearer_token
        self.refresh_token: str = refresh_token
        self.fcm_token: str = fcm_token

        self.session = requests.Session()
        self.session.headers.update(_default_headers)
        self.session.mount('https://', self)
        self.session.mount('http://', self)
        self.session.headers["User-Agent"] = self.user_agent
        self.session.headers["authorization"] = "Bearer " + self.bearer_token

        super().__init__(*args, **kwargs)

    def _login(self) -> None:
        logging.info(f"Logging in {self.username}")
        at, rt = medicover.login(self.username, self.password, self.device_id, self.session)
        self.bearer_token = at
        self.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.bearer_token

    def _refresh(self) -> None:
        logging.info(f"Keep alive {self.username}")
        at, rt = medicover.refresh(self.refresh_token, self.session)
        self.bearer_token = at
        self.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.bearer_token

    def send(self, request, **kwargs):
        response = super().send(request, **kwargs)

        if response.status_code == 401:
            try:
                if self.bearer_token != "":
                    logging.warning(f"401 {self.username} no #1, trying to reload token")
                    self._refresh()
                    request.headers["authorization"] = "Bearer " + self.bearer_token
                    response = super().send(request, **kwargs)
                else:
                    logging.warning(f"401 {self.username} no #1, its not possible to reload token")
            except TypeError:
                pass
            finally:
                if response.status_code == 401:
                    logging.warning(f"401 {self.username} no #2, trying to login")
                    self._login()
                    request.headers["authorization"] = "Bearer " + self.bearer_token
                    response = super().send(request, **kwargs)
                    if response.status_code == 401:
                        raise Exception(f"401 {self.username} no #3, there is some issue with your account")

        return response
