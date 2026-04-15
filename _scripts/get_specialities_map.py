import glob
import json
import logging
import os
import time

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from medicover import get_filters
from medicover.keywords import get_keyword_details, get_keywords
from user_context_store import UserContextStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
db_url = os.getenv("APP_DB")

logging.info(f"Opening DB connection @ {db_url}")
engine: Engine = create_engine(db_url, echo=False)
orm_session: sessionmaker[Session] = sessionmaker(bind=engine)
user_contexts = UserContextStore(engine, orm_session)

logging.info(f"Using user @ {USERNAME}")
user_context = user_contexts.get(USERNAME)

region_id = "204"


# Get keywords
keywords_response = get_keywords(user_context.session)
keywords_dict = keywords_response.model_dump()
tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
os.makedirs(tmp_dir, exist_ok=True)

keywords_file = os.path.join(tmp_dir, 'keywords.json')
with open(keywords_file, 'w', encoding='utf-8') as f:
    json.dump(keywords_dict, f, indent=2, ensure_ascii=False)

logging.info(f"[SUCCESS] Keywords saved to {keywords_file}")

# Get all the keywords consultations
with open(keywords_file, encoding='utf-8') as f:
    keywords_data = json.load(f)
keywords = keywords_data.get('keywords', [])

spec_dir = os.path.join(os.path.dirname(__file__), 'tmp', 'specialties')
os.makedirs(spec_dir, exist_ok=True)
saved = []
for kw in keywords:
    try:
        kw_id = kw.get('id')
        selection_path = kw.get('selectionPath', '').lower()
        mode = 'triage' if selection_path == 'triage' else 'sections'
        details = get_keyword_details(user_context.session, kw_id, region_id, mode=mode)
        spec_list = os.path.join(spec_dir, f"{kw_id}.json")
        with open(spec_list, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        saved.append(kw_id)
    except Exception:
        logging.error(f"ERROR on parsing {kw}")
        continue
summary = {"saved_files": saved, "count": len(saved)}
logging.info(f"[SUCCESS] Saved {len(saved)} specialty JSON files to {spec_dir}")

# Extract consultation ids
specialty_files = glob.glob(os.path.join(spec_dir, '*.json'))
found_ids = set()


def find_specialties(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'specialties' and isinstance(v, list):
                for sid in v:
                    found_ids.add(str(sid))
            else:
                find_specialties(v)
    elif isinstance(obj, list):
        for item in obj:
            find_specialties(item)


for file_path in specialty_files:
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)
    find_specialties(data)
sorted_ids = sorted(found_ids, key=lambda x: int(x) if x.isdigit() else x)
spec_list = os.path.join(os.path.dirname(__file__), 'tmp', 'specialities_list.json')
with open(spec_list, 'w', encoding='utf-8') as f:
    json.dump(sorted_ids, f, indent=2, ensure_ascii=False)
logging.info(f"[SUCCESS] Extracted {len(sorted_ids)} unique specialty IDs to {spec_list}")

# Make a map
with open(spec_list, 'r', encoding='utf-8') as f:
    specialty_ids = json.load(f)


results = []
for specialty_id in specialty_ids:
    response = get_filters(user_context.session, [specialty_id], int(region_id))
    for specialty in response.specialties:
        logging.info(specialty)
        results.append({"id": specialty.id, "name": specialty.value})
    time.sleep(2)  # rate limiting

new_specialities_file = os.path.join(os.path.dirname(__file__), 'tmp', 'specialities.json')
with open(new_specialities_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

logging.info(f"[SUCCESS] Specialities saved to {new_specialities_file}")

old_specialities_file = os.path.join(os.path.dirname(__file__), '..', 'static', 'specialities.json')
with open(old_specialities_file, 'r', encoding='utf-8') as f:
    old_specialities = json.load(f)

old_by_id = {str(s["id"]): s for s in old_specialities}
new_by_id = {str(s["id"]): s for s in results}

added_items = [s for sid, s in new_by_id.items() if sid not in old_by_id]
removed_items = [s for sid, s in old_by_id.items() if sid not in new_by_id]

logging.info(f"New specialities +({len(added_items)}):")
for s in added_items:
    logging.info(f"[NEW] id={s['id']} name={s['name']}")

logging.info(f"Missing specialities (-{len(removed_items)}):")
for s in removed_items:
    logging.info(f"[MISSING] id={s['id']} name={s['name']}")

merged = list({**old_by_id, **new_by_id}.values())
merged.sort(key=lambda s: int(s["id"]))

with open(old_specialities_file, 'w', encoding='utf-8') as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

logging.info(
    f"[SUCCESS] Merged specialities saved to {old_specialities_file} "
    f"({len(merged)} total, +{len(added_items)} new"
)
if len(removed_items) > 0:
    logging.info(f"MISSING (-{len(removed_items)}) WERE NOT REMOVED, JUST LISTED HERE")
    logging.info("COMPARE THE TMP FILE WITH STATIC ONE MANUALLY")
