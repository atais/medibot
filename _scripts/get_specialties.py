import json
import os

from dotenv import load_dotenv

from medicover.keywords import get_keyword_details
from user_context import UserContext

load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
PASSWORD = os.environ.get("MEDICOVER_PASS")

user_context = UserContext(USERNAME, PASSWORD)
user_context._login()

keywords_path = os.path.join(os.path.dirname(__file__), 'tmp', 'keywords.json')
with open(keywords_path, encoding='utf-8') as f:
    keywords_data = json.load(f)
keywords = keywords_data.get('keywords', [])
region_id = "204"
spec_dir = os.path.join(os.path.dirname(__file__), 'tmp', 'specialties')
os.makedirs(spec_dir, exist_ok=True)
saved = []
for kw in keywords:
    kw_id = kw.get('id')
    selection_path = kw.get('selectionPath', '').lower()
    mode = 'triage_flat' if selection_path == 'triage' else 'sections'
    try:
        details = get_keyword_details(user_context.session, kw_id, region_id, mode=mode)
        out_path = os.path.join(spec_dir, f"{kw_id}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2, ensure_ascii=False)
        saved.append(kw_id)
    except Exception as e:
        continue
summary = {"saved_files": saved, "count": len(saved)}
print(f"[SUCCESS] Saved {len(saved)} specialty JSON files to {spec_dir}")
print(json.dumps(summary, indent=2, ensure_ascii=False))
