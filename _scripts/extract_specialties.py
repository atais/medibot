import glob
import json
import os

specialties_dir = os.path.join(os.path.dirname(__file__), 'tmp', 'specialties')
specialty_files = glob.glob(os.path.join(specialties_dir, '*.json'))
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
out_path = os.path.join(os.path.dirname(__file__), 'tmp', 'specialities.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(sorted_ids, f, indent=2, ensure_ascii=False)
print(f"[SUCCESS] Extracted {len(sorted_ids)} unique specialty IDs to {out_path}")
print(json.dumps(sorted_ids, indent=2, ensure_ascii=False))
