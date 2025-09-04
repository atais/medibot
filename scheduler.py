import logging
from datetime import datetime, timedelta, timezone

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

import medicover
from medicover.appointments import SearchParams
from user_context import UserContext

jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(1)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 1
}

scheduler = BackgroundScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone=utc
)


def _search(user_context: UserContext, search_params: SearchParams, job_id: str):
    result = medicover.appointments(
        user_context.session,
        region_ids=search_params.region_ids,
        specialty_ids=search_params.specialty_ids,
        start_time=search_params.start_time
    )
    logging.info(f"{job_id}")
    logging.info([item.model_dump() for item in result])


def create_job(user_context: UserContext, search_params: SearchParams) -> Job:
    job_id = f"{user_context.username}_{list(search_params.model_dump().values())}"
    return scheduler.add_job(
        func=_search,
        trigger='interval',
        minutes=5,
        start_date=datetime.now(timezone.utc) + timedelta(minutes=1),  # Use timezone-aware UTC
        args=[user_context, search_params, job_id],
        id=job_id
    )


def get_jobs(user_context: UserContext) -> list[Job]:
    user_prefix = user_context.username + "_"
    jobs = scheduler.get_jobs()
    filtered_jobs = [job for job in jobs if job.id.startswith(user_prefix)]
    return filtered_jobs
