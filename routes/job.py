from typing import List

from fastapi import APIRouter, Request, Depends
from pydantic import BaseModel
from starlette.responses import HTMLResponse, RedirectResponse

from app_context import get_current_user_context
from medicover.appointments import SearchParams
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


@router.post("/add_job", response_class=HTMLResponse)
async def add_job(request: Request,
                  selected_data: SelectedData,
                  user_context=Depends(get_current_user_context)):
    # Extract values from selectedData structure
    region_ids = int(selected_data.region[0].value)
    specialty_ids = [int(opt.value) for opt in selected_data.specialties]
    doctor_ids = [int(opt.value) for opt in selected_data.doctors] if selected_data.doctors else None
    clinic_ids = [int(opt.value) for opt in selected_data.clinics] if selected_data.clinics else None

    name = ", ".join([
        selected_data.region[0].label,
        ", ".join([opt.label for opt in selected_data.specialties]),
        ", ".join([opt.label for opt in selected_data.clinics]) if selected_data.clinics else "",
        ", ".join([opt.label for opt in selected_data.doctors]) if selected_data.doctors else ""
    ]).strip(", ")

    search_params = SearchParams(
        region_ids=region_ids,
        specialty_ids=specialty_ids,
        doctor_ids=doctor_ids,
        clinic_ids=clinic_ids,
        start_time=selected_data.start_time
    )
    create_job(user_context.username, search_params, selected_data.url, name, selected_data.autobook)
    return RedirectResponse(url="/", status_code=302)


@router.get("/pause_job/{job_id}", response_class=HTMLResponse)
async def pause_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.pause_job(job_id)
    return RedirectResponse(url="/", status_code=302)

@router.get("/resume_job/{job_id}", response_class=HTMLResponse)
async def resume_job(request: Request, job_id: str, user_context=Depends(get_current_user_context)):
    scheduler.resume_job(job_id)
    return RedirectResponse(url="/", status_code=302)
