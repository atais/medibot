import os

from dotenv import load_dotenv
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates
from pyfcm import FCMNotification

from user_context_store import UserContextStore

load_dotenv()

templates = Jinja2Templates(directory="templates")

USER_CONTEXTS_PATH = os.path.join(os.getcwd(), "user_contexts.db")
user_contexts = UserContextStore(USER_CONTEXTS_PATH)

# Initialize FCM with environment variables
fcm_service_account_path = os.getenv("FCM_SERVICE_ACCOUNT_PATH")
fcm_project_id = os.getenv("FCM_PROJECT_ID")

if not fcm_service_account_path or not fcm_project_id:
    raise RuntimeError("FCM_SERVICE_ACCOUNT_PATH and FCM_PROJECT_ID must be set in environment variables")

fcm = FCMNotification(service_account_file=fcm_service_account_path, project_id=fcm_project_id)


def get_current_user_context(request: Request):
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
