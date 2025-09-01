from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import logging
import api
from starlette.responses import HTMLResponse

logging.basicConfig(level=logging.INFO)

from user_context import UserContext

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
templates = Jinja2Templates(directory="templates")

# Global dictionary to store user contexts
user_contexts = {}

@app.get("/", response_class=HTMLResponse)
async def hello(request: Request):
    try:
        session_id = request.session.get("session_id")
        context = user_contexts.get(session_id)
        me = api.me(context.session)
        logging.info(me)

        if not session_id or not context or not me:
            return RedirectResponse(url="/login", status_code=302)
        else:
            return templates.TemplateResponse("index.html", {"request": request, "name": session_id})
    except Exception as e:
        return RedirectResponse(url="/login", status_code=302)


@app.post("/search", response_class=HTMLResponse)
async def search(
        request: Request,
        region_ids: int = Form(...),
        specialty_ids: str = Form(...),
        start_time: str = Form(...)
):
    session_id = request.session.get("session_id")
    context = user_contexts.get(session_id)
    response = api.search(
        context.session,
        region_ids=region_ids,
        specialty_ids=specialty_ids,
        start_time=start_time
    )

    response_dict = [item.dict() for item in response] if response else []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "response": response_dict
        }
    )


@app.get("/login", response_class=HTMLResponse)
async def show_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(...), password: str = Form(...)):
    user_contexts[username] = UserContext(username, password)
    request.session["session_id"] = username
    return RedirectResponse(url="/", status_code=303)
