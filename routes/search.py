from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, get_current_user_context

router = APIRouter()


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request,
                 region_ids: int = Query(...),
                 specialty_ids: str = Query(...),
                 start_time: str = Query(...),
                 user_context=Depends(get_current_user_context)):
    response = medicover.appointments(
        user_context.session,
        region_ids=region_ids,
        specialty_ids=[int(x) for x in specialty_ids.split(",") if x.strip()],
        start_time=start_time
    )
    appointments = [item.model_dump() for item in response] if response else []
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "appointments": appointments,
            "region_ids": region_ids,
            "specialty_ids": specialty_ids,
            "start_time": start_time
        }
    )
