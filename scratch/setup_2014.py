import json
import os

json_path = r"d:\Claude Cowork\exam-wiki-SA\raw\json\question_index.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

new_questions = [
    {
        "moduleId": "SA-2014-1",
        "year": 2014,
        "rocYear": 103,
        "questionNumber": 1,
        "primaryTopicId": "SA-U1-2",
        "primaryTopicName": "靜定結構之分析",
        "secondaryTopicIds": ["SA-U1-3"],
        "verificationStatus": "unverified",
        "hasSolution": False,
        "hasViz": False,
        "hasHandwritten": False,
        "tags": ["靜定桁架", "影響線", "最大軸力"]
    },
    {
        "moduleId": "SA-2014-2",
        "year": 2014,
        "rocYear": 103,
        "questionNumber": 2,
        "primaryTopicId": "SA-U2-2",
        "primaryTopicName": "靜不定結構諧合變位",
        "secondaryTopicIds": [],
        "verificationStatus": "unverified",
        "hasSolution": False,
        "hasViz": False,
        "hasHandwritten": False,
        "tags": ["諧合變位法", "複合結構", "最大彎矩"]
    },
    {
        "moduleId": "SA-2014-3",
        "year": 2014,
        "rocYear": 103,
        "questionNumber": 3,
        "primaryTopicId": "SA-U2-3",
        "primaryTopicName": "靜不定結構之傾角變位法",
        "secondaryTopicIds": [],
        "verificationStatus": "unverified",
        "hasSolution": False,
        "hasViz": False,
        "hasHandwritten": False,
        "tags": ["傾角變位法", "剛架結構", "節點彎矩"]
    },
    {
        "moduleId": "SA-2014-4",
        "year": 2014,
        "rocYear": 103,
        "questionNumber": 4,
        "primaryTopicId": "SA-U2-1",
        "primaryTopicName": "靜不定結構最小功法",
        "secondaryTopicIds": [],
        "verificationStatus": "unverified",
        "hasSolution": False,
        "hasViz": False,
        "hasHandwritten": False,
        "tags": ["最小功法", "剛架", "轉角計算"]
    }
]

existing_ids = [q["moduleId"] for q in data.get("questions", [])]
for q in new_questions:
    if q["moduleId"] not in existing_ids:
        data["questions"].append(q)

data["questions"].sort(key=lambda x: (-x.get("year", 0), x.get("questionNumber", 0)))

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

base_dir = r"d:\Claude Cowork\exam-wiki-SA\raw\solutions"
for i in range(1, 5):
    folder = os.path.join(base_dir, f"SA-2014-{i}")
    os.makedirs(folder, exist_ok=True)
    print(f"Created/Verified {folder}")

print("Successfully updated question_index.json and created directories.")
