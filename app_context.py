import json
import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from pyfcm import FCMNotification

from user_context import UserContext
from user_context_store import UserContextStore

load_dotenv()

templates = Jinja2Templates(directory="templates")

app_db_env = os.getenv("APP_DB")
user_contexts = UserContextStore(app_db_env)

# Initialize FCM with environment variables
fcm_service_account_path = os.getenv("FCM_SERVICE_ACCOUNT_PATH")
fcm = FCMNotification(service_account_file=fcm_service_account_path)

firebase_config = {
    "apiKey": os.environ["FIREBASE_API_KEY"],
    "authDomain": os.environ["FIREBASE_AUTH_DOMAIN"],
    "projectId": os.environ["FIREBASE_PROJECT_ID"],
    "storageBucket": os.environ["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": os.environ["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": os.environ["FIREBASE_APP_ID"],
    "vapidKey": os.environ["FIREBASE_VAPID_KEY"]
}

session_secret_key = os.getenv("SESSION_KEY")
admins_env = os.getenv("APP_ADMINS")
admins: list[str] = [admin.strip() for admin in admins_env.split(",") if admin.strip()]


def load_all_regions() -> dict[int, str]:
    locations_path = os.path.join(os.path.dirname(__file__), 'static', 'locations.json')
    with open(locations_path, encoding='utf-8') as f:
        data = json.load(f)
    return {int(region['id']): region['value'] for region in data.get('regions', [])}


def load_all_specialties() -> dict[int, str]:
    specialties_path = os.path.join(os.path.dirname(__file__), 'static', 'specialities.json')
    with open(specialties_path, encoding='utf-8') as f:
        data = json.load(f)
    return {int(specialty['id']): specialty['name'] for specialty in data}


all_regions: dict[int, str] = load_all_regions()
all_specialities: dict[int, str] = load_all_specialties()


def get_current_user_context(request: Request) -> UserContext:
    username = next(
        (u for u in [
            request.session.get("username"),
            request.cookies.get("username")
        ] if u),
        None,
    )
    if username:
        request.session["username"] = username
        user_context = user_contexts.get(username)
        if user_context:
            return user_context
    raise HTTPException(status_code=302, headers={"Location": "/login"})


def datetimeformat(value, format='%d.%m.%Y %H:%M'):
    if value is None:
        return ""
    try:
        if hasattr(value, 'strftime'):
            return value.strftime(format)
        else:
            dt = datetime.fromisoformat(value)
            return dt.strftime(format)
    except Exception:
        return str(value)


# Register the filter with Jinja2
templates.env.filters['datetimeformat'] = datetimeformat
