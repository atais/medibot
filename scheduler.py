import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.job import Job
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from pyfcm.errors import FCMNotRegisteredError
from pytz import utc

import medicover
from app_context import user_contexts, fcm, app_db_env
from medicover.appointments import SearchParams, Appointment
from user_context import UserContext

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


def _notify(user_context: UserContext, body: str, payload: Optional[Dict]) -> None:
    user = user_context.data.username
    logging.info(f"Sending notifications to {user} to {len(user_context.data.fcm_token)} devices")
    tokens_to_remove = set()
    for token in set(user_context.data.fcm_token):
        try:
            fcm.notify(
                fcm_token=token,
                notification_title="Medibot Search",
                notification_body=body,
                data_payload=payload
            )
        except FCMNotRegisteredError:
            logging.info(f"FCM token not registered or invalid for {user}, removing: {token}")
            tokens_to_remove.add(token)
        except Exception as e:
            logging.error(f"Error sending notification to {user} using token {token}: {e}")
    if tokens_to_remove:
        user_context.data.fcm_token -= tokens_to_remove
        user_contexts.set(user_context)


def _search(username: str, search_params: SearchParams, search_url: str, autobook: bool, job_id: str):
    try:
        user_context: UserContext = user_contexts.get(username)

        # do not run search for past-date
        today = datetime.now().date().strftime("%Y-%m-%d")
        search_params.start_time = max(search_params.start_time, today)
        result: list[Appointment] = medicover.get_slots(user_context.session, search_params)

        if len(result) > 0 and autobook:
            b = result[0]
            medicover.book(
                user_context.session,
                booking_string=b.bookingString,
                old_id=search_params.previous_id
            )
            _notify(
                user_context=user_context,
                body=f"Booked {b.specialty.name}, {b.clinic.name}, {b.doctor.name} @ {b.appointmentDate.strftime('%Y-%m-%d %H:%M')}",
                payload={
                    "click_action": "/"
                }
            )
            logging.info(f"Booked {job_id}, pausing.")
            scheduler.pause_job(job_id)
        elif len(result) > 0 and not autobook:
            _notify(
                user_context=user_context,
                body=f"Found {len(result)} appointments!",
                payload={
                    "click_action": search_url
                }
            )
            logging.info(f"Found appointments for {job_id}, notification sent to {username}")
        elif search_params.end_time is not None and today > search_params.end_time:
            logging.info(f"Search {job_id} is past its endtime, pausing.")
            scheduler.pause_job(job_id)
        else:
            pass

    except Exception as e:
        logging.error(f"Failed _search execution to {username}: {e}")


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
