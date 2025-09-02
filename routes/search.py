from fastapi import APIRouter, Request, Form
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, user_contexts

router = APIRouter()


@router.post("/search", response_class=HTMLResponse)
async def search(request: Request, region_ids: int = Form(...), specialty_ids: str = Form(...),
                 start_time: str = Form(...)):
    session_id = request.session.get("session_id")
    context = user_contexts.get(session_id)
    response = medicover.appointments(
        context.session,
        region_ids=region_ids,
        specialty_ids=[int(x) for x in specialty_ids.split(",") if x.strip()],
        start_time=start_time
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "appointments": [item.model_dump() for item in response] if response else []
        }
    )
