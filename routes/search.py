from fastapi import APIRouter, Request, Query
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, user_contexts
from medicover.appointments import SearchParams
from scheduler import create_job

router = APIRouter()


@router.get("/search", response_class=HTMLResponse)
async def search(request: Request,
                 region_ids: int = Query(...),
                 specialty_ids: str = Query(...),
                 start_time: str = Query(...),
                 action: str = Query(...)
                 ):
    session_id = request.session.get("session_id")
    context = user_contexts.get(session_id)
    appointments = []
    if action == "search":
        response = medicover.appointments(
            context.session,
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
            "start_time": start_time,
            "action": action
        }
    )
