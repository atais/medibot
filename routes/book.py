from fastapi import APIRouter, Request, Form, Depends
from starlette.responses import HTMLResponse

import medicover
from app_context import templates, get_current_user_context

router = APIRouter()


@router.post("/book", response_class=HTMLResponse)
async def search(request: Request, booking_string: str = Form(...), user_context=Depends(get_current_user_context)):
    response = medicover.book(
        user_context.session,
        booking_string=booking_string
    )
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "appointments": []
        }
    )
