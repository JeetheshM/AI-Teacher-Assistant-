# TeachMate AI

> **From curriculum to classroom — in minutes.**

TeachMate AI is an AI-powered teaching copilot designed to help educators turn curriculum resources and teaching requirements into structured, classroom-ready teaching material.

The system combines **LLM-based generation, curriculum-grounded RAG, structured outputs, deterministic validation, teacher review, and PDF export** into one workflow.

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [System Architecture](#system-architecture)
- [AI Modules](#ai-modules)
- [My Contribution](#my-contribution)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Example Workflow](#example-workflow)
- [Quality and Validation](#quality-and-validation)
- [Demo Scenario](#demo-scenario)
- [Future Scope](#future-scope)
- [Team](#team)

---

## Problem

Teachers spend significant time preparing lesson plans, explanations, activities, quizzes, answer keys, and supporting material.

Generic AI tools can generate content quickly, but they may:

- Produce generic content that is not aligned with the curriculum.
- Ignore grade level, duration, difficulty, or learning objectives.
- Return inconsistent free-form output.
- Make it difficult to trace generated content back to source material.
- Require teachers to manually combine multiple outputs into a usable teaching package.

TeachMate AI addresses this as a **structured teaching workflow**, rather than simply placing a chatbot behind a teacher interface.

---

## Solution

TeachMate AI takes teacher requirements and optional curriculum documents and produces a structured teaching package.

### Input

- Subject
- Topic
- Grade
- Duration
- Difficulty
- Class size
- Learning objective
- Optional curriculum PDF/document

### Output

- Lesson plan
- Teaching notes
- Simplified explanations
- Real-world examples
- Classroom activity
- Quiz
- Answer key
- Sources
- Exportable teaching package

The workflow is:

```text
Teacher Input
     |
     v
Curriculum Document (optional)
     |
     v
Document Processing + RAG
     |
     v
AI Orchestrator
     |
     +----------+----------+
     |          |          |
     v          v          v
  Lesson      Quiz      Activity
     |          |          |
     +----------+----------+
                |
                v
       Structured Output
                |
                v
          Validation
                |
                v
        Teacher Review
                |
                v
           PDF Export
```

---

## Key Features

### 1. Curriculum-Grounded Generation

Teachers can provide curriculum documents. Relevant content is retrieved and passed to the appropriate AI module instead of blindly sending an entire document to the LLM.

### 2. Lesson Generation

Generates structured lesson material based on the teacher's requirements and available curriculum context.

### 3. Simplification

Produces easier-to-understand explanations while preserving the core concept.

### 4. Classroom Activity Generation

Creates practical activities aligned with:

- Grade
- Topic
- Duration
- Difficulty
- Class size
- Learning objective
- Curriculum context

### 5. Quiz Generation

Generates assessment material and answer keys.

### 6. Structured Validation

AI output is validated before being displayed or exported.

### 7. Teaching Package Export

Combines generated material into a teacher-facing PDF.

### 8. Teacher-in-the-Loop

AI assists the teacher, but the teacher remains the final reviewer and decision-maker.

---

## How It Works

### Step 1 — Teacher provides requirements

Example:

```text
Subject: Science
Topic: Photosynthesis
Grade: 8
Duration: 45 minutes
Difficulty: Intermediate
Learning Objective:
Understand how plants make food using sunlight,
carbon dioxide and water.
```

### Step 2 — Curriculum is processed

If a curriculum document is provided:

```text
PDF
 |
 v
Text Extraction
 |
 v
Chunking
 |
 v
Embeddings
 |
 v
Vector Store
 |
 v
Relevant Context
```

### Step 3 — AI generation

The relevant context and teacher requirements are passed to feature-specific prompts.

The system generates structured outputs for:

- Lesson
- Activity
- Quiz

### Step 4 — Validation

The generated structure is checked for required fields and basic consistency.

### Step 5 — Teacher review

The teacher can inspect and revise the generated content.

### Step 6 — Export

The final material can be combined into a teaching package PDF.

---

## System Architecture

```text
                         TEACHER
                            |
                            v
                  FRONTEND APPLICATION
                            |
                            v
                         FastAPI
                            |
                            v
                     AI ORCHESTRATOR
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
           LESSON          QUIZ        ACTIVITY
              |             |             |
              +-------------+-------------+
                            |
                            v
                           RAG
                            |
                +-----------+-----------+
                |                       |
                v                       v
          Application DB          Vector Store
                |                       |
                +-----------+-----------+
                            |
                            v
                           LLM
                            |
                            v
                      VALIDATION
                            |
                            v
                     TEACHER REVIEW
                            |
                            v
                       PDF EXPORT
```

---

## AI Modules

The project is organized into modular responsibilities.

| Module | Responsibility |
|---|---|
| Frontend | Teacher dashboard, forms, results and API integration |
| Lesson AI | Lesson planning, explanations, simplification and examples |
| Quiz AI | Quiz generation, question types and answer keys |
| RAG | Document processing, chunking, embeddings, retrieval and sources |
| Backend | FastAPI, database, shared schemas and LLM integration |
| Activity + QA | Classroom activities, PDF export, validation, QA and demo reliability |

This modular design allows individual AI features to be developed and tested independently while still fitting into a single end-to-end workflow.

---


# Tech Stack

## Backend

- Python
- FastAPI
- Pydantic
- SQLite for MVP
- PostgreSQL + pgvector as a production direction

## AI

- LLM API
- Prompt engineering
- Structured JSON generation
- Feature-specific AI modules

## RAG

- PDF/document text extraction
- Chunking
- Embeddings
- FAISS / Chroma or equivalent lightweight vector store
- Source/page traceability

## Frontend

- React or Flutter

## Export

- Python-based PDF generation

## Configuration

- `.env` environment variables

---

# Project Structure

A modular structure is:

```text
teachmate-ai/
|
├── frontend/
│   ├── components/
│   ├── pages/
│   └── services/
|
├── backend/
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   ├── lesson/
│   │   ├── quiz/
│   │   ├── activity/
│   │   ├── rag/
│   │   └── export/
│   ├── prompts/
│   └── tests/
|
├── data/
│   └── curriculum/
|
├── .env.example
├── requirements.txt
└── README.md
```

The exact folder names can be adapted to the team's implementation.

---

# Getting Started

## 1. Clone the repository

```bash
git clone <repository-url>
cd teachmate-ai
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
LLM_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./teachmate.db
VECTOR_STORE_PATH=./data/vector_store
```

Do not commit real API keys or secrets to Git.

## 5. Start the backend

For a FastAPI application:

```bash
uvicorn backend.main:app --reload
```

The exact startup command may vary depending on the final repository structure.

## 6. Start the frontend

Use the frontend framework's standard development command.

For example, if using a typical React setup:

```bash
npm install
npm run dev
```

---

# Environment Variables

Recommended configuration:

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` | API key for the selected LLM provider |
| `DATABASE_URL` | Application database connection |
| `VECTOR_STORE_PATH` | Location of the local vector store |

Never commit `.env` containing real secrets.

---

# Example Workflow

## Photosynthesis Demo

The recommended demo scenario is:

```text
Subject:
Science

Topic:
Photosynthesis

Grade:
8

Duration:
45 minutes

Difficulty:
Intermediate

Learning Objective:
Understand how plants make food using sunlight,
carbon dioxide and water.
```

Optional curriculum:

```text
CBSE Science PDF
```

The system then produces:

```text
1. Lesson Plan
2. Teaching Notes
3. Simplified Explanation
4. Real-world Example
5. Classroom Activity
6. Quiz
7. Answer Key
8. Sources
```

Finally:

```text
Teaching Package
       |
       v
     PDF
```

---

# Quality and Validation

TeachMate uses deterministic checks around AI-generated content.

For an activity, validation can verify:

```text
✓ Title exists
✓ Objective exists
✓ Instructions exist
✓ Materials are present
✓ Duration is valid
✓ Expected outcome exists
✓ Assessment exists
```

The validation layer improves structural reliability.

It does **not** claim that an LLM output is guaranteed to be factually correct. The teacher remains the final reviewer.

---

# Responsible AI Design

TeachMate follows a teacher-in-the-loop approach.

The system is designed so that:

```text
AI
 |
 | generates
 v
Teacher
 |
 | reviews / edits
 v
Final Teaching Material
```

Important principles:

- Curriculum grounding where source material is available.
- Source traceability where retrieval is used.
- Structured outputs rather than unrestricted free-form responses.
- Deterministic validation around AI-generated content.
- Teacher review before final use.
- No claim that AI output is automatically correct.

---

# Demo Flow

A recommended live demonstration:

```text
1. Open TeachMate AI
       ↓
2. Upload curriculum PDF
       ↓
3. Enter teaching requirements
       ↓
4. Generate lesson
       ↓
5. Show retrieved sources
       ↓
6. Show simplified explanation
       ↓
7. Generate classroom activity
       ↓
8. Generate quiz
       ↓
9. Show validation
       ↓
10. Export teaching package
       ↓
11. Open generated PDF
```

---

# Future Scope

Potential future improvements include:

- More curriculum formats
- More advanced teacher editing
- Additional assessment types
- More classroom activity templates
- Better source citation and traceability
- Production PostgreSQL + pgvector deployment
- Expanded analytics and feedback loops
- More robust automated evaluation of generated content

These should be treated as future directions rather than current MVP functionality.

---

# Team

TeachMate AI is developed as a modular team project with responsibilities spanning:

- Frontend and integration
- Lesson planning and simplification
- Quiz and assessment generation
- RAG and document processing
- Backend and database
- Classroom activity generation
- PDF export
- QA and demo reliability

---

# Core Idea

> **TeachMate AI is not simply a chatbot for teachers.**

It is a structured AI workflow that combines:

```text
Curriculum Grounding
        +
AI Generation
        +
Structured Outputs
        +
Quality Validation
        +
Teacher Control
        =
Classroom-Ready Teaching
```

## TeachMate AI

**From curriculum to classroom — in minutes.**
