from fastapi import APIRouter, Request, Form
from starlette.responses import RedirectResponse, HTMLResponse

from app_context import templates, user_contexts
from user_context import UserContext

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_contexts[username] = UserContext(username, password)
    request.session["session_id"] = username
    return RedirectResponse(url="/", status_code=303)
