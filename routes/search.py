from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, get_current_user_context, all_regions, all_specialities
from medicover.appointments import SearchParams

router = APIRouter()


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request,
                 region_ids: int = Query(...),
                 specialty_ids: list[int] = Query(...),
                 doctor_ids: list[int] = Query(None),
                 clinic_ids: list[int] = Query(None),
                 start_time: str = Query(None),
                 end_time: str = Query(None),
                 previous_id: Optional[str] = Query(None),
                 user_context=Depends(get_current_user_context)):
    if start_time is None:
        start_time = datetime.now().strftime("%Y-%m-%d")
    filters = medicover.get_filters(
        user_context.session,
        region_ids=region_ids,
        specialty_ids=specialty_ids
    )
    slots = medicover.get_slots(
        user_context.session,
        SearchParams(
            region_ids=region_ids,
            doctor_ids=doctor_ids,
            clinic_ids=clinic_ids,
            specialty_ids=specialty_ids,
            start_time=start_time,
            end_time=end_time
        )
    )

    appointments = [item.model_dump() for item in slots] if slots else []
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "user": user_context.data.profile,
            "appointments": appointments,
            "region_ids": region_ids,
            "specialty_ids": specialty_ids,
            "start_time": start_time,
            "previous_id": previous_id,
            "clinic_ids": clinic_ids,
            "doctor_ids": doctor_ids,
            "all_clinics": filters.clinics,
            "all_doctors": filters.doctors,
            "all_regions": all_regions,
            "all_specialities": all_specialities,
        }
    )
