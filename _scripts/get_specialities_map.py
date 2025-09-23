import glob
import json
import os

from dotenv import load_dotenv

from medicover import get_filters
from medicover.keywords import get_keyword_details
from user_context import UserContext
from medicover.keywords import get_keywords

load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
PASSWORD = os.environ.get("MEDICOVER_PASS")

user_context = UserContext.init(USERNAME, PASSWORD)
user_context._login()

region_id = "204"



### Get keywords
keywords_response = get_keywords(user_context.session)
keywords_dict = keywords_response.model_dump()
tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
os.makedirs(tmp_dir, exist_ok=True)

keywords_file = os.path.join(tmp_dir, 'keywords.json')
with open(keywords_file, 'w', encoding='utf-8') as f:
    json.dump(keywords_dict, f, indent=2, ensure_ascii=False)

print(f"[SUCCESS] Keywords saved to {keywords_file}")

### Get all the keywords consultations
with open(keywords_file, encoding='utf-8') as f:
    keywords_data = json.load(f)
keywords = keywords_data.get('keywords', [])

spec_dir = os.path.join(os.path.dirname(__file__), 'tmp', 'specialties')
os.makedirs(spec_dir, exist_ok=True)
saved = []
for kw in keywords:
    kw_id = kw.get('id')
    selection_path = kw.get('selectionPath', '').lower()
    mode = 'triage' if selection_path == 'triage' else 'sections'
    try:
        details = get_keyword_details(user_context.session, kw_id, region_id, mode=mode)
        spec_list = os.path.join(spec_dir, f"{kw_id}.json")
        with open(spec_list, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        saved.append(kw_id)
    except Exception as e:
        continue
summary = {"saved_files": saved, "count": len(saved)}
print(f"[SUCCESS] Saved {len(saved)} specialty JSON files to {spec_dir}")

### Extract consultation ids
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
spec_list = os.path.join(os.path.dirname(__file__), 'tmp', 'specialities.json')
with open(spec_list, 'w', encoding='utf-8') as f:
    json.dump(sorted_ids, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Extracted {len(sorted_ids)} unique specialty IDs to {spec_list}")

### Make a map
with open(spec_list, 'r', encoding='utf-8') as f:
    specialty_ids = json.load(f)


results = []
for specialty_id in specialty_ids:
    response = get_filters(user_context.session, [specialty_id], int(region_id))
    for specialty in response.specialties:
        print(specialty)
        results.append({"id": specialty.id, "name": specialty.value})

static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
os.makedirs(static_dir, exist_ok=True)
specialities_file = os.path.join(static_dir, 'specialities.json')
with open(specialities_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Specialities saved to {specialities_file}")
