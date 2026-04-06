import logging

from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse, HTMLResponse

import medicover
from app_context import templates, user_contexts
from user_context import UserContext

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        logging.info(f"Manual logging in {username}")
        uc = UserContext.init(username, password, on_update=user_contexts.set)
        res = medicover.login1(uc.data.username, uc.data.password, uc.data.device_id, uc.session)

        if isinstance(res, medicover.LoginSuccess):
            logging.info(f"Manual logging successful for {username}")
            uc.data.bearer_token = res.access_token
            uc.data.refresh_token = res.refresh_token
            uc.session.headers["authorization"] = "Bearer " + uc.data.bearer_token
            if uc.on_update:
                uc.on_update(uc)

            me = medicover.personal_data(uc.session)
            request.session["username"] = username
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="username", value=username, max_age=60 * 60 * 24 * 30)

            uc.data.profile = me
            user_contexts.set(uc)
            return response

        elif isinstance(res, medicover.LoginMFAPending):
            logging.info(f"Manual logging requires MFA for {username}")

            # Save UserContext for later retrieval
            user_contexts.set(uc)

            # Store MFA data in session
            request.session["mfa_pending"] = res.model_dump()
            request.session["username"] = username

            return RedirectResponse(url="/mfa", status_code=303)

    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": str(e)}
        )


@router.get("/mfa", response_class=HTMLResponse)
async def show_mfa(request: Request):
    return templates.TemplateResponse("mfa.html", {"request": request})


@router.post("/mfa", response_class=HTMLResponse)
async def process_mfa(request: Request, mfa: str = Form(...)):
    try:
        # Retrieve MFA data from session
        mfa_pending_data = request.session.pop("mfa_pending")
        username = request.session.get("username")

        if not mfa_pending_data or not username:
            logging.error("MFA session data missing")
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Session expired, please login again"}
            )

        # Reconstruct LoginMFAPending from session data
        mfa_pending = medicover.LoginMFAPending(**mfa_pending_data)

        # Get UserContext (should already be created during login1)
        uc = user_contexts.get(username)
        if not uc:
            logging.error(f"UserContext not found for {username}")
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": "Session expired, please login again"}
            )

        logging.info(f"Processing MFA for {username}")

        # Call handle_mfa from medicover
        redirect_location = medicover.handle_mfa(mfa_pending, mfa, uc.session)
        res = medicover.login2(redirect_location, mfa_pending.code_verifier, uc.session)

        logging.info(f"Manual logging successful for {username}")
        uc.data.bearer_token = res.access_token
        uc.data.refresh_token = res.refresh_token
        uc.session.headers["authorization"] = "Bearer " + uc.data.bearer_token
        if uc.on_update:
            uc.on_update(uc)

        me = medicover.personal_data(uc.session)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="username", value=username, max_age=60 * 60 * 24 * 30)

        uc.data.profile = me
        user_contexts.set(uc)
        return response
    except Exception as e:
        logging.error(e)
        return templates.TemplateResponse(
            request,
            "login.html",
            {
                "error": str(e)
            }
        )
