# TeachMate AI — 3-Minute Demo Presentation Script

**Audience**: Hackathon Judges & Educators  
**Time Limit**: 3 to 4 minutes  
**Goal**: Demonstrate a grounded, structured AI teaching workflow with educator in the loop.

---

## What to Say vs. What NOT to Say (Safety & Accuracy Guardrails)

| ✅ What to Say | ❌ What NOT to Say |
|:---|:---|
| "Curriculum grounding anchors generation in teacher-provided textbooks." | "Our AI guarantees 100% factual accuracy and eliminates hallucinations." |
| "Deterministic checks validate structural quality and completeness." | "Our validator mathematically verifies everything is true." |
| "The teacher remains the final reviewer and editor." | "This replaces the teacher." |
| "Generates classroom-ready, practical teaching packages in seconds." | "Generic chatbot that answers anything." |

---

## Step-by-Step Demo Flow

### 0:00 - 0:30 | Hook & Problem Statement
- **Presenter Speaks**:
  > *"Every week, teachers spend 10 to 15 hours preparing lesson plans, classroom activities, differentiated explanations, quizzes, and answer keys. While generic chatbots can generate text, they often hallucinate, miss grade-level appropriateness, and provide no trace of where the material came from.*
  > 
  > *Meet **TeachMate AI** — an AI-powered teaching copilot that transforms curriculum textbooks and classroom objectives into complete, grounded, ready-to-teach classroom packages."*

---

### 0:30 - 1:00 | Teacher Input & Curriculum Grounding
- **Action**: Open UI. Show the input form.
  - Subject: `Science`
  - Topic: `Photosynthesis`
  - Grade: `8`
  - Duration: `45 minutes`
  - Difficulty: `Intermediate`
  - Learning Objective: `Understand how plants make food using sunlight, carbon dioxide and water`
- **Action**: Drag & drop `CBSE_Science_Grade8.pdf`.
- **Presenter Speaks**:
  > *"Instead of relying on generic web data, we upload the actual textbook chapter. Our RAG engine extracts and indexes relevant curriculum chunks."*
- **Action**: Click **"Generate Teaching Package"**.

---

### 1:00 - 1:45 | Lesson Generation & Content Adaptation
- **Action**: Switch between `[Lesson]` and `[Explain]` tabs.
- **Presenter Speaks**:
  > *"In one click, TeachMate AI generates a fully structured lesson: introduction hook, core explanation, key concepts, and common misconceptions.*
  > 
  > *Need to adapt for diverse learners? Watch this — we can click **'Simplify'** or **'Add Analogy'**. Instantly, complex biochemistry is adapted into a relatable kitchen analogy, while preserving scientific integrity."*

---

### 1:45 - 2:25 | Classroom Activity & Formative Quiz
- **Action**: Click `[Activity]` tab.
- **Presenter Speaks**:
  > *"TeachMate doesn't stop at lecture notes. In the Activity tab, it creates the 'Photosynthesis Recipe Challenge' — a 15-minute collaborative group activity using simple classroom supplies like paper and markers, complete with step-by-step instructions, teacher facilitation tips, and a 30-second assessment check."*
- **Action**: Click `[Quiz]` tab.
- **Presenter Speaks**:
  > *"Next, we have a multi-tier formative quiz tagged with Bloom's Taxonomy levels, complete with an answer key and rationale. Notice our **Quality Check banner**: deterministic validators verify that all questions have valid answers, no duplicate questions exist, and time allocations match."*

---

### 2:25 - 2:50 | Sources & PDF Export
- **Action**: Click `[Sources]` tab to highlight exact page numbers (`CBSE_Science_Grade8.pdf — Page 82, Page 84`).
- **Action**: Click `Export PDF`. Open the generated PDF.
- **Presenter Speaks**:
  > *"Teachers have complete visibility into where information came from. And when the teacher is ready, one click exports the complete teaching package into a clean, printable PDF ready for the classroom."*

---

### 2:50 - 3:15 | Summary & Value Proposition
- **Presenter Speaks**:
  > *"To summarize: TeachMate AI saves educators hours of prep time, ensures curriculum alignment through grounded RAG, guarantees structural reliability with automated validation, and keeps the teacher firmly in control as the final decision maker.*
  > 
  > *Thank you! We'd love to answer any questions."*

---

## Live Demo Fallback Contingency Protocol

If live LLM API encounters network delay or rate limits during the presentation:
1. Immediately switch to local demo mode loading `demo/fallback_teaching_package.json`.
2. Open the pre-generated PDF from `exports/Photosynthesis_Grade_8.pdf`.
3. Presenters should seamlessly continue explaining the architecture, validation checks, and curriculum grounding without pausing the pitch.
