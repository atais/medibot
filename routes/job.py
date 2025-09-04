from fastapi import APIRouter, Request, Query, Depends
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import templates, get_current_user_context
from medicover.appointments import SearchParams
from scheduler import get_jobs, scheduler, create_job

router = APIRouter()


# Endpoint to render jobs table
@router.get("/get_jobs", response_class=HTMLResponse)
async def jobs_list(request: Request, user_context=Depends(get_current_user_context)):
    jobs = get_jobs(user_context.username) if user_context else []
    return templates.TemplateResponse("search.html", {
        "request": request,
        "name": user_context.username,
        "jobs": jobs
    })


@router.get("/edit_job/{job_id}", response_class=HTMLResponse)
async def edit_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    return HTMLResponse(f"<h1>Edit Job {job_id} (not implemented)</h1>")


@router.post("/remove_job/{job_id}", response_class=HTMLResponse)
async def remove_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.remove_job(job_id)
    jobs = get_jobs(user_context.username) if user_context else []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": user_context.username,
        "jobs": jobs
    })


@router.get("/add_job", response_class=HTMLResponse)
async def add_job(request: Request,
                  region_ids: int = Query(...),
                  specialty_ids: str = Query(...),
                  start_time: str = Query(...),
                  user_context=Depends(get_current_user_context)):
    search_params = SearchParams(
        region_ids=region_ids,
        specialty_ids=[int(x) for x in specialty_ids.split(",") if x.strip()],
        start_time=start_time
    )
    create_job(user_context.username, search_params)
    return RedirectResponse(url="/", status_code=302)
