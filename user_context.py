import json
import logging
import uuid

import requests
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter

import app_context
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
            cookie_jar: str = "",
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

        # Restore cookie jar if provided
        if cookie_jar:
            self._restore_cookie_jar(cookie_jar)

        super().__init__(*args, **kwargs)

    def _restore_cookie_jar(self, cookie_jar_data: str):
        """Restore the entire cookie jar from JSON data"""

        try:
            if not cookie_jar_data:
                return

            # Parse JSON data
            cookies_data = json.loads(cookie_jar_data)

            # Restore each cookie
            for cookie_info in cookies_data:
                self.session.cookies.set(
                    name=cookie_info['name'],
                    value=cookie_info['value'],
                    domain=cookie_info.get('domain'),
                    path=cookie_info.get('path', '/'),
                    secure=cookie_info.get('secure', False),
                    expires=cookie_info.get('expires')
                )

            logging.debug(f"Restored {len(cookies_data)} cookies for {self.username}")
        except Exception as e:
            logging.warning(f"Failed to restore cookie jar for {self.username}: {e}")

    def _login(self) -> None:
        logging.info(f"Logging in {self.username}")
        at, rt = medicover.login(self.username, self.password, self.device_id, self.session)
        self.bearer_token = at
        self.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.bearer_token
        app_context.user_contexts.set(self.username, self)

    def _refresh(self) -> None:
        logging.info(f"Keep alive {self.username}")
        at, rt = medicover.refresh(self.refresh_token, self.session)
        self.bearer_token = at
        self.refresh_token = rt
        self.session.headers["authorization"] = "Bearer " + self.bearer_token
        app_context.user_contexts.set(self.username, self)

    def send(self, request, **kwargs):
        response = super().send(request, **kwargs)

        if response.status_code == 401:
            try:
                if self.bearer_token != "":
                    logging.warning(f"401 {self.username} no #1, trying to reload token")
                    self._refresh()
                    response = super().send(request, **kwargs)
                else:
                    logging.warning(f"401 {self.username} no #1, its not possible to reload token")
            except TypeError:
                pass
            finally:
                if response.status_code == 401:
                    logging.warning(f"401 {self.username} no #2, trying to login")
                    self.session.headers["authorization"] = ""
                    self.session.cookies.clear_session_cookies()
                    self._login()
                    response = super().send(request, **kwargs)
                    if response.status_code == 401:
                        raise Exception(f"401 {self.username} no #3, there is some issue with your account")

        return response
