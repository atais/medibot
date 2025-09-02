from fastapi import APIRouter, Request, Form
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, user_contexts

router = APIRouter()


@router.post("/book", response_class=HTMLResponse)
async def search(request: Request, booking_string: str = Form(...)):
    session_id = request.session.get("session_id")
    context = user_contexts.get(session_id)
    response = medicover.book(
        context.session,
        booking_string=booking_string
    )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "appointments": []
        }
    )
