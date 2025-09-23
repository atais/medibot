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
    try:
        medicover.book(
            user_context.session,
            booking_string=booking_string,
            old_id=previous_booking_id
        )
        request.session["flash_message"] = "Rezerwacja zakończona sukcesem."
        request.session["flash_category"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Błąd rezerwacji: {str(e)}"
        request.session["flash_category"] = "danger"
    return RedirectResponse(url="/", status_code=303)


@router.get("/delete")
async def delete(request: Request, appointment_id: str = Query(...),
                 user_context=Depends(get_current_user_context)):
    try:
        medicover.delete(
            user_context.session,
            appointment_id
        )
        request.session["flash_message"] = "Wizyta została usunięta."
        request.session["flash_category"] = "success"
    except Exception as e:
        request.session["flash_message"] = f"Błąd usuwania wizyty: {str(e)}"
        request.session["flash_category"] = "danger"
    return RedirectResponse(url="/", status_code=303)
