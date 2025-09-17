import os

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

session_secret_key = os.getenv("SESSION_KEY")


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
