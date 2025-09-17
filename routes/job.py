from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import get_current_user_context
from medicover.appointments import SearchParams
from scheduler import scheduler, create_job

router = APIRouter()


@router.get("/edit_job/{job_id}", response_class=HTMLResponse)
async def edit_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    return HTMLResponse(f"<h1>Edit Job {job_id} (not implemented)</h1>")


@router.post("/remove_job/{job_id}", response_class=HTMLResponse)
async def remove_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.remove_job(job_id)
    return RedirectResponse(url="/", status_code=302)


@router.get("/add_job", response_class=HTMLResponse)
async def add_job(request: Request,
                  region_ids: int = Query(...),
                  specialty_ids: list[int] = Query(...),
                  start_time: str = Query(...),
                  user_context=Depends(get_current_user_context)):
    search_params = SearchParams(
        region_ids=region_ids,
        specialty_ids=specialty_ids,
        start_time=start_time
    )
    create_job(user_context.username, search_params)
    return RedirectResponse(url="/", status_code=302)
