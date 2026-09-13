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
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic v2, [uv](https://docs.astral.sh/uv/)
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
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

### With Docker

```bash
docker compose up --build
```

Backend: http://localhost:8000/docs · Frontend: http://localhost:5173
(SQLite data persists in the `backend_data` named volume across
restarts.) Released versions are also published to GitHub Container
Registry — see [Releases](../../releases) for image tags, e.g.:

```bash
docker pull ghcr.io/chemoday/ai-dev-zoomcamp-week-2-backend:latest
docker pull ghcr.io/chemoday/ai-dev-zoomcamp-week-2-frontend:latest
```

### Deploying to Render

`render.yaml` is a [Blueprint](https://render.com/docs/blueprint-spec)
that deploys both services from this one repo:

- **`restaurant-backend`** — Docker web service, built from
  `backend/Dockerfile`
- **`restaurant-frontend`** — static site, built from `frontend/`
  (`npm ci && npm run build`), with `VITE_API_BASE` wired to the
  backend service's host automatically

To deploy: push this repo to GitHub, then in the Render dashboard
choose **New > Blueprint** and point it at the repo — Render reads
`render.yaml` and creates both services.

**Free-tier caveat**: Render's free web services have no persistent
disk, so the backend's SQLite file resets on every redeploy and on the
automatic spin-down after 15 minutes of inactivity. Fine for a demo;
not durable storage — see `_plan/roadmap.md` step 9 for details.

### Tests

```bash
# backend (38 tests), from the repo root
uv run --project backend pytest

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
docker-compose.yml          runs backend + frontend containers together
render.yaml                 Render Blueprint (deploys both services)
frontend/                   Vue 3 app (frontend/tests/ has its own smoke test, Dockerfile)
backend/                    FastAPI app (Dockerfile, pyproject.toml/uv.lock)
tests/                      backend unit tests
docs/ai-usage-report.md     log of AI tool usage for this project
_plan/                      module reference material and roadmap
```
