"""
generate_custom_quiz.py
-----------------------
Generate a quiz from ANY custom PDF or text file on your computer.

Usage:
    python generate_custom_quiz.py path/to/your_file.pdf

Options:
    python generate_custom_quiz.py "C:\\path\\to\\chapter.pdf" --subject "Biology" --topic "Cell Structure" --grade 9 --count 5
"""

import argparse
import json
import os
import sys
import httpx

# Ensure UTF-8 output on Windows
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_URL = "http://localhost:8080/api/quizzes/generate-from-file"


def main():
    parser = argparse.ArgumentParser(description="Generate a quiz from any custom PDF or TXT file.")
    parser.add_argument("file", help="Path to your custom .pdf or .txt file")
    parser.add_argument("--subject", default="General Science", help="Subject name (e.g. Science, History)")
    parser.add_argument("--topic", default=None, help="Specific topic (defaults to filename if omitted)")
    parser.add_argument("--grade", type=int, default=8, help="School grade (1-12, default: 8)")
    parser.add_argument("--difficulty", choices=["easy", "intermediate", "hard"], default="intermediate", help="Difficulty level")
    parser.add_argument("--count", type=int, default=5, help="Number of questions (default: 5)")
    parser.add_argument("--types", default="mcq,true_false,short_answer", help="Comma-separated: mcq,true_false,short_answer")
    parser.add_argument("--bloom", default="remember,understand,apply", help="Comma-separated bloom levels")
    parser.add_argument("--output", default="custom_quiz_output.json", help="Path to save output JSON")

    args = parser.parse_args()

    file_path = os.path.abspath(args.file)
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at '{file_path}'")
        sys.exit(1)

    filename = os.path.basename(file_path)
    topic = args.topic or os.path.splitext(filename)[0].replace("_", " ").title()

    print("=" * 60)
    print("  TeachMate AI - Custom File Quiz Generator")
    print("=" * 60)
    print(f"📄 Custom File : {file_path}")
    print(f"📚 Subject     : {args.subject}")
    print(f"🎯 Topic       : {topic}")
    print(f"🏫 Grade       : {args.grade}")
    print(f"⚙️  Difficulty  : {args.difficulty}")
    print(f"🔢 Count       : {args.count} questions")
    print("-" * 60)
    print("⏳ Uploading file and generating quiz with Gemini (takes ~10s)...")

    mime_type = "application/pdf" if file_path.lower().endswith(".pdf") else "text/plain"

    with open(file_path, "rb") as f:
        files = {"file": (filename, f, mime_type)}
        data = {
            "subject": args.subject,
            "topic": topic,
            "grade": str(args.grade),
            "difficulty": args.difficulty,
            "question_count": str(args.count),
            "question_types": args.types,
            "bloom_levels": args.bloom,
        }

        try:
            response = httpx.post(API_URL, files=files, data=data, timeout=120.0)
        except httpx.ConnectError:
            print(f"\n❌ Error: Cannot connect to server at {API_URL}")
            print("Please make sure the server is running in another terminal:")
            print("  python -m uvicorn main:app --port 8080")
            sys.exit(1)

    if response.status_code != 200:
        print(f"\n❌ Generation failed ({response.status_code}):")
        print(response.text)
        sys.exit(1)

    res_json = response.json()
    quiz = res_json["quiz"]
    answer_key = res_json["answer_key"]
    validation = res_json["validation"]
    file_info = res_json.get("file_info", {})

    print("\n" + "=" * 60)
    print(f"  {quiz['title'].upper()}")
    print(f"  Pages Extracted: {file_info.get('pages_extracted', 1)} | Characters: {file_info.get('total_chars', 0)}")
    print("=" * 60)

    for q in quiz["questions"]:
        print(f"\n{q['id'].upper()}.  {q['question']}")
        print(f"    Type: {q['type']}  |  Bloom: {q['bloom_level']}  |  Difficulty: {q['difficulty']}")
        if q.get("options"):
            for idx, opt in enumerate(q["options"], 1):
                print(f"      {chr(64+idx)}) {opt}")

    print("\n" + "-" * 60)
    print("  ANSWER KEY & EXPLANATIONS")
    print("-" * 60)
    for entry in answer_key["entries"]:
        print(f"\n{entry['question_id'].upper()}.  Answer: {entry['answer']}")
        print(f"     Explain: {entry['explanation']}")

    print("\n" + "-" * 60)
    status_str = "PASSED" if validation["valid"] else "FAILED"
    print(f"  QUALITY VALIDATION -- {status_str}")
    print("-" * 60)
    for check_name, passed in validation["checks"].items():
        icon = "[OK]" if passed else "[FAIL]"
        print(f"  {icon}  {check_name.replace('_', ' ').title()}")

    with open(args.output, "w", encoding="utf-8") as out_f:
        json.dump(res_json, out_f, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ Success! Full quiz saved to: {args.output}")
    print("=" * 60)


if __name__ == "__main__":
    main()
