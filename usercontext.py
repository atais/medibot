import logging

import attr
import requests
from fake_useragent import UserAgent

import auth

_default_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-PL;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


@attr.s
class UserContext:
    username: str = attr.ib()
    password: str = attr.ib()

    def __attrs_post_init__(self):
        self.session = requests.Session()
        self.bearer_token: ""
        self.refresh_token: ""
        self.ua = UserAgent().random

        self.session.headers.update(_default_headers)
        self.session.headers["User-Agent"] = self.ua

    def login(self) -> None:
        logging.info(f"Logging in {self.username}")
        (b, r) = auth.login(self.username, self.password, self.session)
        self.session.headers["authorization"] = "Bearer " + b
        self.bearer_token = b
        self.refresh_token = r
        logging.debug(f"{self.username}: {b}")

    def refresh(self) -> None:
        logging.info(f"Keep alive {self.username}")
        (b, r) = auth.refresh(self.refresh_token, self.session)
        self.session.headers["authorization"] = "Bearer " + b
        self.bearer_token = b
        self.refresh_token = r
        logging.debug(f"{self.username}: {b}")
