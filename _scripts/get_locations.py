import json
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from medicover.keywords import get_locations
from user_context_store import UserContextStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()

username: str = os.environ.get("MEDICOVER_USER")
db_url = os.getenv("APP_DB")

logging.info(f"Opening DB connection @ {db_url}")
engine: Engine = create_engine(db_url, echo=False)
orm_session: sessionmaker[Session] = sessionmaker(bind=engine)
user_contexts = UserContextStore(engine, orm_session)

logging.info(f"Using user @ {username}")

user_context = user_contexts.get(username)
session = user_context.session

locations_response = get_locations(session)
locations_dict = locations_response.model_dump()
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
os.makedirs(static_dir, exist_ok=True)
locations_file = os.path.join(static_dir, 'locations.json')
with open(locations_file, 'w', encoding='utf-8') as f:
    json.dump(locations_dict, f, indent=2, ensure_ascii=False)
logging.info(f"[SUCCESS] Locations saved to {locations_file}")
logging.info(json.dumps(locations_dict, indent=2, ensure_ascii=False))
