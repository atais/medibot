import logging

from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse, HTMLResponse

import medicover
from app_context import templates, user_contexts
from user_context import UserContext

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        uc = UserContext(username, password, on_update=user_contexts.set)
        me = medicover.personal_data(uc.session)

        request.session["username"] = username
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="username", value=username, max_age=60 * 60 * 24 * 30)

        uc.home_clinic = int(me.homeClinicId)
        user_contexts.set(uc)
        return response
    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": str(e)}
        )
