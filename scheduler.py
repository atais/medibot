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
    'default': SQLAlchemyJobStore(url='sqlite:///medibot.sqlite')
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

    if len(result) > 0:
        try:
            specialty_ids_str = ','.join(map(str, search_params.specialty_ids))

            fcm.notify(
                fcm_token=user_context.fcm_token,
                notification_title="Medibot Search",
                notification_body=f"Found {len(result)} appointments!",
                data_payload={
                    "click_action": f"/search?region_ids={search_params.region_ids}&specialty_ids={specialty_ids_str}&start_time={search_params.start_time}"
                }
            )
            logging.info(f"Notification sent to {username}")
        except Exception as e:
            logging.error(f"Failed to send notification to {username}: {e}")


def create_job(username: str, search_params: SearchParams) -> Job:
    job_id = f"{username}_{list(search_params.model_dump().values())}"
    return scheduler.add_job(
        func=_search,
        trigger='interval',
        minutes=5,
        start_date=datetime.now(timezone.utc) + timedelta(minutes=5),
        args=[username, search_params, job_id],
        id=job_id,
        name=job_id
    )


def get_jobs(username: str) -> list[Job]:
    user_prefix = username + "_"
    jobs = scheduler.get_jobs()
    filtered_jobs = [job for job in jobs if job.id.startswith(user_prefix)]
    return filtered_jobs
