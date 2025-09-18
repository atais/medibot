from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import all_regions, all_specialities
from app_context import templates, get_current_user_context
from app_context import user_contexts
from medicover import get_person_appointments, get_referrals
from scheduler import get_jobs

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user_context=Depends(get_current_user_context)):
    jobs = get_jobs(user_context.username)
    referrals = get_referrals(user_context.session)
    appointments = get_person_appointments(user_context.session)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user_context.username,
        "profile": user_context,
        "jobs": jobs,
        "referrals": referrals,
        "appointments": appointments,
        "all_regions": all_regions,
        "all_specialities": all_specialities,
    })


@router.post("/update_profile", response_class=HTMLResponse)
async def update_region(request: Request, region_id: int = Form(None), user_context=Depends(get_current_user_context)):
    if region_id is not None:
        user_context.home_clinic = region_id
        user_contexts.set(user_context)
    return RedirectResponse(url="/", status_code=303)
