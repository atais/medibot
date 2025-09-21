from fastapi import APIRouter, Request, Form, Depends, Query
from starlette.responses import HTMLResponse, RedirectResponse

import medicover
from app_context import get_current_user_context

router = APIRouter()


@router.post("/book", response_class=HTMLResponse)
async def book(request: Request,
               booking_string: str = Form(...),
               previous_booking_id: str = Form(None),
               user_context=Depends(get_current_user_context)
               ):
    response = medicover.book(
        user_context.session,
        booking_string=booking_string,
        old_id=previous_booking_id
    )
    return RedirectResponse(url="/", status_code=303)


@router.get("/delete")
async def delete(request: Request, appointment_id: str = Query(...),
                 user_context=Depends(get_current_user_context)):
    result = medicover.delete(
        user_context.session,
        appointment_id
    )
    return RedirectResponse(url="/", status_code=303)
