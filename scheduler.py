import logging
from datetime import datetime, timedelta, timezone

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

import medicover
from app_context import user_contexts, fcm, app_db_env
from medicover.appointments import SearchParams, Appointment

jobstores = {
    'default': SQLAlchemyJobStore(url=app_db_env)
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


def _search(username: str, search_params: SearchParams, search_url: str, autobook: bool, job_id: str):
    try:
        user_context = user_contexts.get(username)

        # do not run search for past-date
        today = datetime.now().date().strftime("%Y-%m-%d")
        start_time = max(search_params.start_time, today)

        result: list[Appointment] = medicover.get_slots(
            user_context.session,
            region_ids=search_params.region_ids,
            doctor_ids=search_params.doctor_ids,
            clinic_ids=search_params.clinic_ids,
            specialty_ids=search_params.specialty_ids,
            start_time=start_time
        )

        if len(result) > 0 and autobook:
            b = result[0]
            medicover.book(
                user_context.session,
                booking_string=b.bookingString,
                old_id=search_params.previous_id
            )
            fcm.notify(
                fcm_token=user_context.fcm_token,
                notification_title="Medibot Search",
                notification_body=f"Booked {b.specialty.name}, {b.clinic.name}, {b.doctor.name} @ {b.appointmentDate}",
                data_payload={
                    "click_action": "/"
                }
            )
            logging.info(f"Notification sent to {username}")
            scheduler.pause_job(job_id)
        elif len(result) > 0 and not autobook:
            fcm.notify(
                fcm_token=user_context.fcm_token,
                notification_title="Medibot Search",
                notification_body=f"Found {len(result)} appointments!",
                data_payload={
                    "click_action": search_url
                }
            )
            logging.info(f"Notification sent to {username}")
    except Exception as e:
        logging.error(f"Failed _search of to {username}: {e}")


def create_job(username: str, search_params: SearchParams, search_url: str, name: str, autobook: bool) -> Job:
    job_id = f"{username}_{list(search_params.model_dump().values())}"
    return scheduler.add_job(
        func=_search,
        trigger='interval',
        minutes=5,
        start_date=datetime.now(timezone.utc) + timedelta(seconds=30),
        args=[username, search_params, search_url, autobook, job_id],
        id=job_id,
        name=name
    )


def get_jobs(username: str) -> list[Job]:
    user_prefix = username + "_"
    jobs = scheduler.get_jobs()
    filtered_jobs = [job for job in jobs if job.id.startswith(user_prefix)]
    return filtered_jobs
