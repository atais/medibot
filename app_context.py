import logging
from fastapi import Request, HTTPException
from fastapi.templating import Jinja2Templates

from user_context import UserContext

templates = Jinja2Templates(directory="templates")

user_contexts: dict[str, UserContext] = {}


def get_current_user_context(request: Request):
    session_id = request.session.get("session_id")
    user_context = user_contexts.get(session_id)
    if not user_context:
        logging.info("no session")
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    else:
        logging.info(f"session: {user_context}")
        return user_context
