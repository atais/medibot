from typing import List

from fastapi import APIRouter, Request, Depends, Query
from pydantic import BaseModel
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import get_current_user_context, all_regions, all_specialities
from medicover.appointments import SearchParams, FiltersResponse, get_filters
from scheduler import scheduler, create_job

router = APIRouter()


class Option(BaseModel):
    value: str
    label: str


class SelectedData(BaseModel):
    url: str
    region: List[Option]
    specialties: List[Option]
    clinics: List[Option]
    doctors: List[Option]
    start_time: str
    autobook: bool


@router.post("/remove_job/{job_id}", response_class=HTMLResponse)
async def remove_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.remove_job(job_id)
    return RedirectResponse(url="/", status_code=302)


@router.get("/add_job", response_class=HTMLResponse)
async def add_job(request: Request,
                  region_ids: int = Query(...),
                  specialty_ids: list[int] = Query(...),
                  doctor_ids: list[int] = Query(None),
                  clinic_ids: list[int] = Query(None),
                  start_time: str = Query(...),
                  end_time: str = Query(None),
                  autobook: bool = Query(False),
                  previous_id: str = Query(None),
                  user_context=Depends(get_current_user_context)):
    filters: FiltersResponse = get_filters(
        user_context.session,
        region_ids=region_ids,
        specialty_ids=specialty_ids
    )

    parts = [
        all_regions.get(region_ids),
        *[all_specialities.get(id) for id in specialty_ids],
        *(c.value for c in filters.clinics for id in (clinic_ids or []) if c.id == str(id)),
        *(d.value for d in filters.doctors for id in (doctor_ids or []) if d.id == str(id))
    ]
    name = ", ".join(part for part in parts if part)

    search_params = SearchParams(
        region_ids=region_ids,
        specialty_ids=specialty_ids,
        doctor_ids=doctor_ids,
        clinic_ids=clinic_ids,
        previous_id=previous_id,
        start_time=start_time,
        end_time=end_time
    )
    url = "/search" + (f"?{request.url.query}" if request.url.query else "")
    create_job(user_context.data.username, search_params, url, name, autobook)
    return RedirectResponse(url="/", status_code=302)


@router.get("/pause_job/{job_id}", response_class=HTMLResponse)
async def pause_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.pause_job(job_id)
    return RedirectResponse(url="/", status_code=302)


@router.get("/resume_job/{job_id}", response_class=HTMLResponse)
async def resume_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.resume_job(job_id)
    return RedirectResponse(url="/", status_code=302)
