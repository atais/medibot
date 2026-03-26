import base64
import hashlib
import json
import random
import re
import string
import time
import uuid
from typing import Tuple
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from pydantic import BaseModel
from requests import Session

from ._constants import ONLINE24, LOGIN


class LoginSuccess(BaseModel):
    access_token: str
    refresh_token: str


class LoginMFAPending(BaseModel):
    code_verifier: str
    token: str
    mfa_code_id: str
    return_url: str
    channel: str
    operation: str
    post_url: str


def _uuid_v4() -> str:
    return str(uuid.uuid4()).replace("-", "")


def _gen_code_challenge(seed: str) -> str:
    uuid_sha = hashlib.sha256(seed.encode("utf-8")).digest()
    based = base64.urlsafe_b64encode(uuid_sha).decode("utf-8")
    return re.sub(r"=+$", "", based.replace("+", "-").replace("/", "_"))


_oidc_url = f'{ONLINE24}/signin-oidc'


# 3a. GET the MFA page – extract token and MfaCodeId hidden input
def _get_mfa(next_url: str, code_verifier: str, session: Session) -> LoginMFAPending:
    response = session.get(f"{LOGIN}{next_url}", allow_redirects=False)
    parser = BeautifulSoup(response.content, "html.parser")
    token = parser.find("input", {"name": "__RequestVerificationToken"}).get('value')
    mfa_code_id = parser.find("input", {"name": "Input.MfaCodeId"}).get('value')
    return_url = parser.find("input", {"name": "Input.ReturnUrl"}).get('value')
    channel = parser.find("input", {"name": "Input.Channel"}).get('value')
    operation = parser.find("input", {"name": "Input.Operation"}).get('value')
    post_url = next_url.split('&Operation=')[0]

    return LoginMFAPending(
        code_verifier=code_verifier,
        token=token,
        mfa_code_id=mfa_code_id,
        return_url=return_url,
        channel=channel,
        operation=operation,
        post_url=post_url
    )


# 3b. POST the MFA form (Operation moves from query string into form body)
def handle_mfa(login: LoginMFAPending, otp_code: str, session: Session):
    mfa_form = {
        "Input.MfaCodeId": login.mfa_code_id,
        "Input.ReturnUrl": login.return_url,
        "Input.DeviceName": "Chrome",
        "Input.MfaCode": otp_code,
        "Input.IsTrustedDevice": "true",
        "Input.Channel": login.channel,
        "Input.Operation": login.operation,
        "Input.Button": "confirm",
        "__RequestVerificationToken": login.token,
    }
    response = session.post(f"{LOGIN}{login.post_url}", data=mfa_form, allow_redirects=False)
    return response.headers.get("Location")


def login1(username: str, password: str, device_id: str, session: Session) -> LoginSuccess | LoginMFAPending:
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
        "app_version": "3.24.0-beta.1.7",
        "device_id": device_id,
        "device_name": "Chrome",
        "ts": int(time.time() * 1000)
    }

    # 0. initialize login
    # https://login-online24.medicover.pl/connect/authorize?client_id=web...
    response = session.get(f"{LOGIN}/connect/authorize", params=auth_params, allow_redirects=False)
    next_url = response.headers.get("Location")
    return_url = parse_qs(urlparse(next_url).query)["ReturnUrl"][0]

    # 1. get __RequestVerificationToken
    # https://login-online24.medicover.pl/Account/Login?...
    response = session.get(next_url, allow_redirects=False)
    parser = BeautifulSoup(response.content, "html.parser")
    token = parser.find("input", {"name": "__RequestVerificationToken"}).get('value')

    # 2. send the form
    # https://login-online24.medicover.pl/Account/Login....
    login_form = {
        "Input.ReturnUrl": return_url,
        "Input.LoginType": "FullLogin",
        "Input.Username": username,
        "Input.Password": password,
        "Input.Button": "login",
        "Input.IsSimpleAccessRegulationAccepted": "false",
        "__RequestVerificationToken": token
    }
    response = session.post(next_url, data=login_form, allow_redirects=False)
    next_url = response.headers.get("Location")

    # 3. handle MFA
    if 'Account/Mfa' not in next_url:
        return login2(next_url, code_verifier, session)
    else:
        return _get_mfa(next_url, code_verifier, session)


def login2(next_url: str, code_verifier: str, session: Session) -> LoginSuccess:
    # 4. get code
    # https://login-online24.medicover.pl/connect/authorize/callback...
    response = session.get(f"{LOGIN}{next_url}", allow_redirects=False)
    next_url = response.headers.get("Location")
    code = parse_qs(urlparse(next_url).query)["code"][0]

    # 5. send code
    # https://online24.medicover.pl/signin-oidc?code=...
    response = session.get(next_url)

    # 6. get token
    token_data = {
        "grant_type": "authorization_code",
        "redirect_uri": _oidc_url,
        "code": code,
        "code_verifier": code_verifier,
        "client_id": "web"
    }
    response = session.post(f"{LOGIN}/connect/token", data=token_data)
    session_data = json.loads(response.content)
    access_token = session_data.get("access_token")
    refresh_token = session_data.get("refresh_token")

    return LoginSuccess(access_token=access_token, refresh_token=refresh_token)


def refresh(old_refresh: str, session: Session) -> Tuple[str, str]:
    # 7. to refresh token
    refresh_token_data = {
        "grant_type": "refresh_token",
        "refresh_token": old_refresh,
        "scope": "openid offline_access profile",
        "client_id": "web"
    }
    response = session.post(f"{LOGIN}/connect/token", data=refresh_token_data, allow_redirects=False)
    session_data = json.loads(response.content)
    access_token = session_data.get("access_token")
    refresh_token = session_data.get("refresh_token")

    return access_token, refresh_token
