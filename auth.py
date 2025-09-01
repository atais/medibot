import base64
import hashlib
import json
import random
import re
import string
import uuid
from typing import Tuple
from urllib.parse import urlparse, parse_qs
import time

from bs4 import BeautifulSoup
from requests import Session


def _uuid_v4() -> str:
    return str(uuid.uuid4()).replace("-", "")


def _gen_code_challenge(seed: str) -> str:
    uuid_sha = hashlib.sha256(seed.encode("utf-8")).digest()
    based = base64.urlsafe_b64encode(uuid_sha).decode("utf-8")
    return re.sub(r"=+$", "", based.replace("+", "-").replace("/", "_"))


_login_url = "https://login-online24.medicover.pl"
_online_url = "https://online24.medicover.pl"
_oidc_url = f'{_online_url}/signin-oidc'


def login(username: str, password: str, device_id: str, session: Session) -> Tuple[str, str]:
    state = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))
    code_verifier = _uuid_v4() + _uuid_v4() + _uuid_v4()
    code_challenge = _gen_code_challenge(code_verifier)

    auth_params = {
        "client_id": "web",
        "redirect_uri": _oidc_url,
        "response_type": "code",
        "scope": "openid offline_access profile",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "response_mode": "query",
        "ui_locales": "pl",
        "app_version": "3.9.3-beta.1.8",
        "device_id": device_id,
        "device_name": "Chrome",
        "ts": int(time.time() * 1000)
    }

    # 0. initialize login
    # https://login-online24.medicover.pl/connect/authorize?client_id=web...
    response = session.get(f"{_login_url}/connect/authorize", params=auth_params, allow_redirects=False)
    next_url = response.headers.get("Location")
    return_url = parse_qs(urlparse(next_url).query)["ReturnUrl"][0]

    # 1. get __RequestVerificationToken
    # https://login-online24.medicover.pl/Account/Login?...
    response = session.get(next_url, allow_redirects=False)
    login_form = BeautifulSoup(response.content, "html.parser")
    token = login_form.find("input", {"name": "__RequestVerificationToken"}).get('value')

    # 2. send the form
    # https://login-online24.medicover.pl/Account/Login....
    login_form = {
        "Input.ReturnUrl": return_url,
        "Input.LoginType": "FullLogin",
        "Input.Username": username,
        "Input.Password": password,
        "Input.Button": "login",
        "__RequestVerificationToken": token
    }
    response = session.post(next_url, data=login_form, allow_redirects=False)
    next_url = response.headers.get("Location")

    # 3. get code
    # https://login-online24.medicover.pl/connect/authorize/callback...
    response = session.get(f"{_login_url}{next_url}", allow_redirects=False)
    next_url = response.headers.get("Location")
    code = parse_qs(urlparse(next_url).query)["code"][0]

    # 4. send code
    # https://online24.medicover.pl/signin-oidc?code=...
    response = session.get(next_url)

    # 5. get token
    token_data = {
        "grant_type": "authorization_code",
        "redirect_uri": _oidc_url,
        "code": code,
        "code_verifier": code_verifier,
        "client_id": "web"
    }
    response = session.post(f"{_login_url}/connect/token", data=token_data)
    session_data = json.loads(response.content)
    access_token = session_data.get("access_token")
    refresh_token = session_data.get("refresh_token")

    return access_token, refresh_token


def refresh(old_refresh: str, session: Session) -> Tuple[str, str]:
    # 7. to refresh token
    refresh_token_data = {
        "grant_type": "refresh_token",
        "refresh_token": old_refresh,
        "scope": "openid offline_access profile",
        "client_id": "web"
    }
    response = session.post(f"{_login_url}/connect/token", data=refresh_token_data, allow_redirects=False)
    session_data = json.loads(response.content)
    access_token = session_data.get("access_token")
    refresh_token = session_data.get("refresh_token")

    return access_token, refresh_token
