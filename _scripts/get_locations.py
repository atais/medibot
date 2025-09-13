import json
import os

from dotenv import load_dotenv

from _scripts.user_context import UserContext
from medicover.keywords import get_locations

load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
PASSWORD = os.environ.get("MEDICOVER_PASS")

print(USERNAME)

user_context = UserContext(USERNAME, PASSWORD)
user_context._login()
session = user_context.session

locations_response = get_locations(session)
locations_dict = locations_response.model_dump()
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
os.makedirs(static_dir, exist_ok=True)
locations_file = os.path.join(static_dir, 'locations.json')
with open(locations_file, 'w', encoding='utf-8') as f:
    json.dump(locations_dict, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Locations saved to {locations_file}")
print(json.dumps(locations_dict, indent=2, ensure_ascii=False))
