import os

from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates

from user_context_store import UserContextStore

templates = Jinja2Templates(directory="templates")

USER_CONTEXTS_PATH = os.path.join(os.getcwd(), "user_contexts.db")
user_contexts = UserContextStore(USER_CONTEXTS_PATH)


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
