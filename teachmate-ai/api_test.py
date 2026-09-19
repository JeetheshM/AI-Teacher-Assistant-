"""
api_test.py
-----------
Hits the running FastAPI server with httpx and prints results.

Usage (start server first):
    uvicorn main:app --reload --port 8000

Then in a SECOND terminal:
    python api_test.py
"""

import httpx
import json

BASE = "http://localhost:8000"

PAYLOAD = {
    "subject": "Science",
    "topic": "Photosynthesis",
    "grade": 8,
    "difficulty": "intermediate",
    "question_count": 5,
    "question_types": ["mcq", "true_false", "short_answer"],
    "learning_objective": "Understand how plants make food using sunlight, CO2 and water",
    "bloom_levels": ["remember", "understand", "apply"],
    "curriculum_context": [
        {
            "content": "Green plants prepare their own food using carbon dioxide and water in the presence of sunlight and chlorophyll.",
            "source": "CBSE_Science.pdf",
            "page_number": 82
        }
    ]
}

print("🔍 Checking server health...")
r = httpx.get(f"{BASE}/health")
print(f"   Status: {r.status_code}  {r.json()}\n")

print("📝 Sending quiz generation request...")
r = httpx.post(f"{BASE}/api/quizzes/generate", json=PAYLOAD, timeout=60.0)

if r.status_code != 200:
    print(f"❌ Error {r.status_code}: {r.text}")
    exit(1)

data = r.json()
quiz = data["quiz"]
validation = data["validation"]
answer_key = data["answer_key"]

print(f"\n{'='*60}")
print(f"  {quiz['title'].upper()}")
print(f"  {quiz['subject']} | Grade {quiz['grade']} | {quiz['difficulty']}")
print(f"{'='*60}")

for q in quiz["questions"]:
    print(f"\n{q['id'].upper()}. {q['question']}")
    print(f"   [{q['type']}] Bloom: {q['bloom_level']} | Difficulty: {q['difficulty']}")
    if q["options"]:
        for i, opt in enumerate(q["options"], 1):
            print(f"     {chr(64+i)}) {opt}")

print(f"\n{'─'*60}")
print("  ANSWER KEY")
print(f"{'─'*60}")
for e in answer_key["entries"]:
    print(f"  {e['question_id'].upper()}. ✅ {e['answer']}")
    print(f"     💡 {e['explanation']}\n")

print(f"{'─'*60}")
overall = "✅ PASSED" if validation["valid"] else "❌ FAILED"
print(f"  QUALITY CHECK  {overall}")
print(f"{'─'*60}")
for check, passed in validation["checks"].items():
    icon = "✓" if passed else "✗"
    print(f"  {icon}  {check.replace('_', ' ').title()}")

if validation["warnings"]:
    for w in validation["warnings"]:
        print(f"  ⚠️  {w}")
if validation["errors"]:
    for e in validation["errors"]:
        print(f"  ❌ {e}")

print(f"\n✔ Done. Full JSON saved to quiz_output.json")
with open("quiz_output.json", "w") as f:
    json.dump(data, f, indent=2)
