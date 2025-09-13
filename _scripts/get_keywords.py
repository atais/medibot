import json
import os

from dotenv import load_dotenv

from medicover.keywords import get_keywords
from user_context import UserContext

load_dotenv()

USERNAME = os.environ.get("MEDICOVER_USER")
PASSWORD = os.environ.get("MEDICOVER_PASS")

user_context = UserContext(USERNAME, PASSWORD)
user_context._login()

keywords_response = get_keywords(user_context.session)
keywords_dict = keywords_response.model_dump()
tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
os.makedirs(tmp_dir, exist_ok=True)
keywords_file = os.path.join(tmp_dir, 'keywords.json')
with open(keywords_file, 'w', encoding='utf-8') as f:
    json.dump(keywords_dict, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Keywords saved to {keywords_file}")
print(json.dumps(keywords_dict, indent=2, ensure_ascii=False))
