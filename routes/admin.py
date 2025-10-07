from apscheduler.job import Job
from fastapi import APIRouter, Request, Depends
from fastapi import status
from fastapi.responses import PlainTextResponse
from starlette.responses import HTMLResponse

from app_context import get_current_user_context, templates, user_contexts, admins
from scheduler import scheduler
from user_context import UserData, UserContext

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
async def book(request: Request,
               user_context: UserContext = Depends(get_current_user_context)
               ):
    if user_context.data.username not in admins:
        return PlainTextResponse("Unauthorized", status_code=status.HTTP_401_UNAUTHORIZED)

    users: list[UserData] = user_contexts.get_all()
    jobs: list[Job] = scheduler.get_jobs()

    flash_message = request.session.pop("flash_message", None)
    flash_category = request.session.pop("flash_category", "info")
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "user": user_context.data.profile,
        "users": users,
        "jobs": jobs,
        "flash_message": flash_message,
        "flash_category": flash_category
    })
