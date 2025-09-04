from fastapi import APIRouter, Request, Query
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import templates, user_contexts
from scheduler import get_jobs, scheduler, create_job
from medicover.appointments import SearchParams

router = APIRouter()

# Endpoint to render jobs table
@router.get("/get_jobs", response_class=HTMLResponse)
async def jobs_list(request: Request):
    session_id = request.session.get("session_id")
    user_context = user_contexts.get(session_id)
    jobs = get_jobs(user_context) if user_context else []
    return templates.TemplateResponse("search.html", {
        "request": request,
        "name": session_id,
        "jobs": jobs
    })


@router.get("/edit_job/{job_id}", response_class=HTMLResponse)
async def edit_job(request: Request, job_id: str):
    # ...existing code...
    return HTMLResponse(f"<h1>Edit Job {job_id} (not implemented)</h1>")


@router.post("/remove_job/{job_id}", response_class=HTMLResponse)
async def remove_job(request: Request, job_id: str):
    session_id = request.session.get("session_id")
    user_context = user_contexts.get(session_id)
    scheduler.remove_job(job_id)
    jobs = get_jobs(user_context) if user_context else []
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": session_id,
        "jobs": jobs
    })


@router.get("/add_job", response_class=HTMLResponse)
async def add_job(request: Request,
                  region_ids: int = Query(...),
                  specialty_ids: str = Query(...),
                  start_time: str = Query(...)):
    session_id = request.session.get("session_id")
    user_context = user_contexts.get(session_id)
    if not user_context:
        return RedirectResponse(url="/login", status_code=302)
    search_params = SearchParams(
        region_ids=region_ids,
        specialty_ids=[int(x) for x in specialty_ids.split(",") if x.strip()],
        start_time=start_time
    )
    create_job(user_context, search_params)
    jobs = get_jobs(user_context)
    # Render index.html with jobs list after scheduling
    return templates.TemplateResponse("index.html", {
        "request": request,
        "name": session_id,
        "jobs": jobs
    })
