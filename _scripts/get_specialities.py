import json
import os
from dotenv import load_dotenv
from _scripts.user_context import UserContext
from medicover.book import get_specialties

load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
PASSWORD = os.environ.get("MEDICOVER_PASS")

user_context = UserContext(USERNAME, PASSWORD)
user_context._login()
session = user_context.session

specialities_path = os.path.join(os.path.dirname(__file__), 'tmp', 'specialities.json')
with open(specialities_path, 'r', encoding='utf-8') as f:
    specialty_ids = json.load(f)

region_id = "204"  # Default region, adjust as needed
slot_search_type = "Standard"  # Default slot search type, adjust as needed

results = []
for specialty_id in specialty_ids:
    response = get_specialties(session, region_id, slot_search_type, str(specialty_id))
    for specialty in response.specialties:
        print(specialty)
        results.append({"id": specialty.id, "name": specialty.value})

static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
os.makedirs(static_dir, exist_ok=True)
specialities_file = os.path.join(static_dir, 'specialities.json')
with open(specialities_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Specialities saved to {specialities_file}")
print(json.dumps(results, indent=2, ensure_ascii=False))

