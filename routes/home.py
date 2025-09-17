from fastapi import APIRouter, Request, Depends
from starlette.responses import HTMLResponse
from app_context import templates, get_current_user_context
from scheduler import get_jobs
from medicover.referrals import get_referrals

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user_context=Depends(get_current_user_context)):
    jobs = get_jobs(user_context.username)
    referrals = get_referrals(user_context.session)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user_context.username,
        "jobs": jobs,
        "referrals": referrals
    })
