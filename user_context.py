import logging

import requests
from requests.adapters import HTTPAdapter

import medicover
from user_data import UserData

_default_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-PL;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class UserContext(HTTPAdapter):

    def __init__(self, username: str, password: str, *args, **kwargs):
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.session.headers.update(_default_headers)
        self.session.mount('https://', self)
        self.session.mount('http://', self)

        self.user_data = UserData(username)
        self.session.headers["User-Agent"] = self.user_data.user_agent
        self._update_bearer()

        super().__init__(*args, **kwargs)

    def _update_bearer(self) -> None:
        self.session.headers["authorization"] = "Bearer " + self.user_data.bearer_token

    def _login(self) -> None:
        logging.info(f"Logging in {self.username}")
        r = medicover.login(self.username, self.password, self.user_data.device_id, self.session)
        self.user_data.update_tokens(*r)
        self._update_bearer()

    def _refresh(self) -> None:
        logging.info(f"Keep alive {self.username}")
        r = medicover.refresh(self.user_data.refresh_token, self.session)
        self.user_data.update_tokens(*r)
        self._update_bearer()

    def send(self, request, **kwargs):
        response = super().send(request, **kwargs)

        if response.status_code == 401:
            try:
                if self.user_data.bearer_token != "":
                    logging.warning(f"401 {self.user_data.username} no #1, trying to reload token")
                    self._refresh()
                    request.headers["authorization"] = "Bearer " + self.user_data.bearer_token
                    response = super().send(request, **kwargs)
                else:
                    logging.warning(f"401 {self.user_data.username} no #1, its not possible to reload token")
            except TypeError:
                pass
            finally:
                if response.status_code == 401:
                    logging.warning(f"401 {self.user_data.username} no #2, trying to login")
                    self._login()
                    request.headers["authorization"] = "Bearer " + self.user_data.bearer_token
                    response = super().send(request, **kwargs)
                    if response.status_code == 401:
                        raise Exception(f"401 {self.user_data.username} no #3, there is some issue with your account")

        return response
