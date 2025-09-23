from fastapi import APIRouter, Request, Depends, Form
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import all_regions, all_specialities
from app_context import templates, get_current_user_context
from app_context import user_contexts
from medicover import get_person_appointments, get_referrals, personal_data
from scheduler import get_jobs

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, user_context=Depends(get_current_user_context)):
    jobs = get_jobs(user_context.data.username)
    referrals = get_referrals(user_context.session)
    appointments = get_person_appointments(user_context.session)
    flash_message = request.session.pop("flash_message", None)
    flash_category = request.session.pop("flash_category", "info")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user_context.data.profile,
        "jobs": jobs,
        "referrals": referrals,
        "appointments": appointments,
        "all_regions": all_regions,
        "all_specialities": all_specialities,
        "flash_message": flash_message,
        "flash_category": flash_category,
    })


@router.post("/update_profile", response_class=HTMLResponse)
async def update_profile(request: Request, region_id: int = Form(...), user_context=Depends(get_current_user_context)):
    user_context.data.profile.homeClinicId = str(region_id)
    user_contexts.set(user_context)
    request.session["flash_message"] = "Profil został zaktualizowany."
    request.session["flash_category"] = "success"
    return RedirectResponse(url="/", status_code=303)


@router.get("/refresh_profile", response_class=HTMLResponse)
async def refresh_profile(request: Request, user_context=Depends(get_current_user_context)):
    try:
        me = personal_data(user_context.session)
        user_context.data.profile = me
        user_contexts.set(user_context)
        request.session["flash_message"] = "Profil odświeżony z Medicover."
        request.session["flash_category"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Błąd odświeżania profilu: {str(e)}"
        request.session["flash_category"] = "danger"
    return RedirectResponse(url="/", status_code=303)
