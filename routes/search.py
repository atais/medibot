from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, get_current_user_context

router = APIRouter()


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request,
                 region_ids: int = Query(...),
                 specialty_ids: list[int] = Query(...),
                 doctor_ids: list[int] = Query(None),
                 clinic_ids: list[int] = Query(None),
                 start_time: str = Query(...),
                 user_context=Depends(get_current_user_context)):
    filters = medicover.get_filters(
        user_context.session,
        region_ids=region_ids,
        specialty_ids=specialty_ids
    )
    slots = medicover.get_slots(
        user_context.session,
        region_ids=region_ids,
        doctor_ids=doctor_ids,
        clinic_ids=clinic_ids,
        specialty_ids=specialty_ids,
        start_time=start_time
    )
    appointments = [item.model_dump() for item in slots] if slots else []
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "user": user_context.username,
            "appointments": appointments,
            "region_ids": region_ids,
            "specialty_ids": specialty_ids,
            "start_time": start_time,
            "clinic_ids": clinic_ids,
            "doctor_ids": doctor_ids,
            "all_clinics": filters.clinics,
            "all_doctors": filters.doctors,
        }
    )
