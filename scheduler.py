from datetime import datetime, timedelta, timezone
import logging

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

import medicover
from app_context import user_contexts, fcm
from medicover.appointments import SearchParams

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
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


def _search(username: str, search_params: SearchParams, job_id: str):
    user_context = user_contexts.get(username)
    result = medicover.appointments(
        user_context.session,
        region_ids=search_params.region_ids,
        specialty_ids=search_params.specialty_ids,
        start_time=search_params.start_time
    )

    # Send FCM notification to the job owner
    try:
        fcm.notify(
            fcm_token=user_context.fcm_token,
            notification_title="Medibot Search",
            notification_body="Hello! Your appointment search has been executed."
        )
        logging.info(f"Notification sent to {username}")
    except Exception as e:
        logging.error(f"Failed to send notification to {username}: {e}")

    # logging.info(f"{job_id}")
    # logging.info([item.model_dump() for item in result])


def create_job(username: str, search_params: SearchParams) -> Job:
    job_id = f"{username}_{list(search_params.model_dump().values())}"
    return scheduler.add_job(
        func=_search,
        trigger='interval',
        minutes=1,
        start_date=datetime.now(timezone.utc) + timedelta(minutes=1),  # Use timezone-aware UTC
        args=[username, search_params, job_id],
        id=job_id,
        name=job_id
    )


def get_jobs(username: str) -> list[Job]:
    user_prefix = username + "_"
    jobs = scheduler.get_jobs()
    filtered_jobs = [job for job in jobs if job.id.startswith(user_prefix)]
    return filtered_jobs
