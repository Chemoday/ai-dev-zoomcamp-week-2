# Interactive Restaurant Table Reservation System

[![Tests](https://github.com/Chemoday/ai-dev-zoomcamp-week-2/actions/workflows/tests.yml/badge.svg)](https://github.com/Chemoday/ai-dev-zoomcamp-week-2/actions/workflows/tests.yml)

Module 2 project for the AI-dev Zoomcamp: a full-stack MVP for
restaurant table reservations and floor management, built with a
frontend-first, contract-driven workflow.

See [`product-spec.md`](product-spec.md) for the full spec (business
logic, API contract, UI/UX) and [`_plan/roadmap.md`](_plan/roadmap.md)
for the step-by-step build plan.

## Stack

- **Frontend**: Vue 3 (Composition API, `<script setup>`), Vite, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic v2
- **Database**: SQLite

## Status

Module 2 complete — see [`_plan/roadmap.md`](_plan/roadmap.md) for the
full build history. Frontend and backend are integrated: run both
servers below and the app talks to the real FastAPI + SQLite backend.
Both have test coverage (38 backend tests, a frontend smoke test),
enforced on every push to `main` via CI.

## Running locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### Tests

```bash
# backend (38 tests)
source backend/venv/bin/activate
pytest

# frontend (smoke test)
cd frontend
npm install
npm test
```

## Repository layout

```text
product-spec.md            product spec: scope, contract, UI/UX, roadmap
CLAUDE.md / AGENTS.md       stack + AI-generation guardrails
openapi.yaml                API contract (frontend <-> backend)
frontend/                   Vue 3 app (frontend/tests/ has its own smoke test)
backend/                    FastAPI app
tests/                      backend unit tests
docs/ai-usage-report.md     log of AI tool usage for this project
_plan/                      module reference material and roadmap
```
