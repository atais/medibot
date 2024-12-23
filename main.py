import logging
import os

from dotenv import load_dotenv

from api import *
from user_context import UserContext

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Starting the application...")

    load_dotenv()
    username = os.environ.get("MEDICOVER_USER")
    password = os.environ.get("MEDICOVER_PASS")

    uc = UserContext(username, password)

    r = initial_filters(
        session=uc.session,
        region_id=204
    )
    print(r.status_code)

    r = (search_appointments(
        session=uc.session,
        page=1,
        page_size=2,
        service_type="Standard",
        slot_search_type=1,
        start_time="2024-12-08",
        visit_type="Center",
        region_ids=204,
        specialty_ids=[163, 202, 64796]
    ))
    print(r.status_code)

    print("----")
    print(uc.user_data.bearer_token)
    # print(r.request.url)
    # print(r.content)

    # print(search_appointments(
    #     session=uc.session,
    #     page=1,
    #     page_size=10,
    #     service_type="Standard",
    #     slot_search_type=1,
    #     start_time="2024-12-08",
    #     visit_type="Tele",
    #     region_ids=[204],
    #     specialty_ids=[44058, 49378]
    # ).content)


if __name__ == "__main__":
    main()
