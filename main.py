import logging
import os

from dotenv import load_dotenv

from api import initial_filters
from user_context import UserContext

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logging.info("Starting the application...")

    load_dotenv()
    username = os.environ.get("MEDICOVER_USER")
    password = os.environ.get("MEDICOVER_PASS")

    uc = UserContext(username, password)

    initial_filters(uc.session)

    logging.info(f"Processing complete: {uc}")


if __name__ == "__main__":
    main()
