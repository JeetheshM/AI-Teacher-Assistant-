# TeachMate AI — End-to-End QA & Reliability Checklist

This checklist is owned by **Person 6 (QA & Demo Reliability Lead)**. It must be executed before final judging and demo presentations.

---

## 1. System Startup & Smoke Verification
- [ ] Python backend starts cleanly (`uvicorn main:app --reload` on port 8000)
- [ ] Frontend starts cleanly (`npm start` / `flutter run` / dev server)
- [ ] `GET /api/health` returns `{ "status": "ok" }` or equivalent `200 OK`
- [ ] Environment variables are configured (`LLM_API_KEY`, `LLM_MODEL`, `DATABASE_URL`) without committing `.env`

---

## 2. Primary End-to-End Workflow Verification
- [ ] **Step 1: Input Form**
  - [ ] Subject: `Science`
  - [ ] Topic: `Photosynthesis`
  - [ ] Grade: `8`
  - [ ] Duration: `45 minutes`
  - [ ] Difficulty: `Intermediate`
  - [ ] Learning Objective: `Understand how plants make food using sunlight, carbon dioxide and water`
- [ ] **Step 2: Curriculum PDF Upload**
  - [ ] Upload valid PDF (e.g. `CBSE_Science_Grade8.pdf`)
  - [ ] Verify upload completes and document ID is returned
  - [ ] Verify chunking and vector storage index successfully
- [ ] **Step 3: Lesson Generation**
  - [ ] Click "Generate Teaching Package"
  - [ ] Structured lesson renders in `[Lesson]` tab
  - [ ] Introduction, Explanation, Key Points, Examples, Misconceptions, and Recap present
- [ ] **Step 4: Curriculum Source Grounding**
  - [ ] `[Sources]` tab displays cited textbook filename and exact page numbers (e.g. Page 82, Page 84)
  - [ ] No fake or hallucinated citations
- [ ] **Step 5: Content Adaptation (Explain / Simplify)**
  - [ ] Click `Simplify` -> simplified explanation generated and displayed
  - [ ] Click `Add Analogy` / `Real-world Example` -> kitchen / solar panel analogy generated
- [ ] **Step 6: Classroom Activity Generation**
  - [ ] `[Activity]` tab displays structured activity (Title, Materials, Step-by-step Instructions, Teacher Role, Student Role, Assessment Method)
  - [ ] Activity is age-appropriate (Grade 8) and duration-aware (15 minutes)
  - [ ] Materials use common classroom supplies (paper, markers, post-its)
  - [ ] Safety notes and adaptations displayed
- [ ] **Step 7: Quiz & Answer Key Generation**
  - [ ] `[Quiz]` tab displays 5 questions with options and Bloom's taxonomy tags
  - [ ] Answer key displays correct answers and explanations directly extracted from quiz model
- [ ] **Step 8: Quality Validation Display**
  - [ ] Structural checks show green checkmarks (Required fields present, Correct answer exists, Non-empty options, Duration consistent)
- [ ] **Step 9: Teaching Package PDF Export**
  - [ ] Click `Export PDF`
  - [ ] Downloaded PDF opens without errors
  - [ ] Layout includes metadata, lesson plan, activity, quiz, answer key, and curriculum citations
  - [ ] Page numbers ("Page X of Y") render in footer

---

## 3. Edge-Case & Error-Resilience Matrix

| Test Case | Input / Scenario | Expected Behavior | Pass / Fail |
|:---|:---|:---|:---:|
| **EC-01** | Empty Topic | UI displays validation warning; API returns `400 Bad Request` | [ ] |
| **EC-02** | Empty Subject | UI displays validation warning; API returns `400 Bad Request` | [ ] |
| **EC-03** | Invalid Grade (`0` or `15`) | Pydantic validation rejects; clean error message | [ ] |
| **EC-04** | Invalid Duration (`0` or negative) | Validator flags error; rejects with user-friendly message | [ ] |
| **EC-05** | Very long topic description (>200 chars) | System processes without crashing or overflowing UI | [ ] |
| **EC-06** | No curriculum PDF uploaded (pure prompt mode) | Full generation succeeds using domain knowledge; Sources tab shows "General Curriculum Knowledge" | [ ] |
| **EC-07** | Non-PDF file uploaded (.exe, .zip) | Rejected with "Unsupported file type. Please upload a PDF." | [ ] |
| **EC-08** | Empty / 0-byte PDF | Handled gracefully with warning; falls back to standard generation | [ ] |
| **EC-09** | Scanned PDF (image-only, no text) | Text extraction returns empty; no crash; user informed | [ ] |
| **EC-10** | RAG returns 0 chunks for query | No false citations fabricated; generation proceeds safely | [ ] |
| **EC-11** | LLM API Timeout or Network Disconnect | UI shows "Unable to reach AI service. Please retry." (No blank white screen) | [ ] |
| **EC-12** | LLM returns Markdown fences around JSON | Extractor strips ````json ```` and parses valid JSON | [ ] |
| **EC-13** | LLM returns malformed JSON | Service catches JSONDecodeError, logs technical error, returns friendly error | [ ] |
| **EC-14** | Quiz missing correct answer in options | Validator flags validation failure; does not publish broken quiz | [ ] |
| **EC-15** | Export with partial data (e.g. no quiz or no activity) | Exporter renders available sections cleanly without crashing | [ ] |

---

## 4. Final Demo Readiness Criteria
- [ ] Full demo flow executed **TWICE** consecutively end-to-end without errors.
- [ ] Local fallback JSON files verified in `demo/` folder (`fallback_lesson.json`, `fallback_quiz.json`, `fallback_activity.json`, `fallback_teaching_package.json`).
- [ ] Sample exported PDF pre-generated and stored in `exports/` as an offline backup.
- [ ] All teammates agree on feature freeze (No unreviewed PRs merged within 40 minutes of demo).
