import base64
import hashlib
import json
import os
import random
import re
import string
import uuid
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fake_useragent import UserAgent

# import logging
# import http.client
# logging.basicConfig(level=logging.DEBUG)
# http.client.HTTPConnection.debuglevel = 1

load_dotenv()

username = os.environ.get("MEDICOVER_USER")
password = os.environ.get("MEDICOVER_PASS")
session = requests.Session()
headers = {
    "User-Agent": UserAgent().random,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pl-PL,pl;q=0.9,en-PL;q=0.8,en;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

state = "".join(random.choices(string.ascii_lowercase + string.digits, k=32))


def uuid_v4():
    return str(uuid.uuid4()).replace("-", "")


def gen_code_challenge(input):
    uuid_sha = hashlib.sha256(str(input).encode("utf-8")).digest()
    based = base64.urlsafe_b64encode(uuid_sha).decode("utf-8")
    return re.sub(r"=+$", "", based.replace("+", "-").replace("/", "_"))


device_id = str(uuid.uuid4())
code_verifier = uuid_v4() + uuid_v4() + uuid_v4()
code_challenge = gen_code_challenge(code_verifier)

login = "https://login-online24.medicover.pl"
online = "https://online24.medicover.pl"
oidc = f'{online}/signin-oidc'

auth_params = ("?client_id=web" +
               f"&redirect_uri={oidc}" +
               "&response_type=code" +
               "&scope=openid+offline_access+profile" +
               f"&state={state}" +
               f"&code_challenge={code_challenge}" +
               "&code_challenge_method=S256" +
               "&response_mode=query" +
               "&ui_locales=pl" +
               "&app_version=3.2.0.482" +
               "&previous_app_version=3.2.0.482" +
               f"&device_id={device_id}" +
               "&device_name=Chrome")

# 0. initialize login
# https://login-online24.medicover.pl/connect/authorize?client_id=web...
response = session.get(f"{login}/connect/authorize" + auth_params, headers=headers, allow_redirects=False)
next_url = response.headers.get("Location")

# 1. get __RequestVerificationToken
# https://login-online24.medicover.pl/Account/Login?...
response = session.get(next_url, headers=headers, allow_redirects=False)
login_form = BeautifulSoup(response.content, "html.parser")
token = login_form.find("input", {"name": "__RequestVerificationToken"}).get('value')

# 2. send the form
# https://login-online24.medicover.pl/Account/Login....
login_form = {
    "Input.ReturnUrl": "/connect/authorize/callback" + auth_params,
    "Input.LoginType": "FullLogin",
    "Input.Username": username,
    "Input.Password": password,
    "Input.Button": "login",
    "__RequestVerificationToken": token
}
response = session.post(next_url, data=login_form, headers=headers, allow_redirects=False)
next_url = response.headers.get("Location")

# 3. get code
# https://login-online24.medicover.pl/connect/authorize/callback...
response = session.get(f"{login}{next_url}", headers=headers, allow_redirects=False)
next_url = response.headers.get("Location")
code = parse_qs(urlparse(next_url).query)["code"][0]

# 4. send code
# https://online24.medicover.pl/signin-oidc?code=...
response = session.get(next_url, headers=headers, allow_redirects=False)

# 5. get token
token_data = {
    "grant_type": "authorization_code",
    "redirect_uri": oidc,
    "code": code,
    "code_verifier": code_verifier,
    "client_id": "web"
}
response = session.post(f"{login}/connect/token", data=token_data, headers=headers, allow_redirects=False)
session_data = json.loads(response.content)
tokenB = session_data.get("id_token")
tokenR = session_data.get("refresh_token")

# 6. we are in!
headers["authorization"] = "Bearer " + tokenB
response = session.get(
    "https://api-gateway-online24.medicover.pl/service-selector-configurator/api/search-appointments/filters?RegionId=204",
    headers=headers)
print(json.dumps(json.loads(response.content)))

# 7. to refresh token
refresh_token_data = {
    "grant_type": "refresh_token",
    "refresh_token": tokenR,
    "scope": "openid offline_access profile",
    "client_id": "web"
}
response = session.post(f"{login}/connect/token", data=refresh_token_data, headers=headers, allow_redirects=False)
print(json.dumps(json.loads(response.content)))
