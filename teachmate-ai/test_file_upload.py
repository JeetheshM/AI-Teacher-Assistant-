"""Quick test of the file upload endpoint."""
import httpx, json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with open("sample_science.txt", "rb") as f:
    files = {"file": ("sample_science.txt", f, "text/plain")}
    data = {
        "subject": "Science",
        "topic": "Photosynthesis",
        "grade": "8",
        "difficulty": "intermediate",
        "question_count": "5",
        "question_types": "mcq,true_false,short_answer",
        "bloom_levels": "remember,understand,apply",
    }
    r = httpx.post(
        "http://localhost:8080/api/quizzes/generate-from-file",
        files=files, data=data, timeout=90
    )

print("Status:", r.status_code)
if r.status_code != 200:
    print("Error:", r.text[:800])
    exit(1)

d = r.json()
fi = d["file_info"]
print(f"\nFile uploaded : {fi['filename']}")
print(f"Pages read    : {fi['pages_extracted']}")
print(f"Characters    : {fi['total_chars']}")

SEP = "=" * 60
LINE = "-" * 60
print(f"\n{SEP}")
print(f"  {d['quiz']['title'].upper()}")
print(SEP)

for q in d["quiz"]["questions"]:
    print(f"\n{q['id'].upper()}.  {q['question']}")
    print(f"    [{q['type']}]  Bloom: {q['bloom_level']}  Difficulty: {q['difficulty']}")
    if q["options"]:
        for i, opt in enumerate(q["options"], 1):
            print(f"      {chr(64+i)}) {opt}")

print(f"\n{LINE}")
print("  ANSWER KEY")
print(LINE)
for e in d["answer_key"]["entries"]:
    print(f"\n  {e['question_id'].upper()}.  {e['answer']}")
    print(f"       {e['explanation']}")

print(f"\n{LINE}")
v = d["validation"]
print(f"  QUALITY CHECK -- {'PASSED' if v['valid'] else 'FAILED'}")
print(LINE)
for check, passed in v["checks"].items():
    icon = "[OK]" if passed else "[!!]"
    print(f"  {icon}  {check.replace('_', ' ').title()}")

with open("file_upload_output.json", "w", encoding="utf-8") as f:
    json.dump(d, f, indent=2)
print("\nFull JSON saved to: file_upload_output.json")
