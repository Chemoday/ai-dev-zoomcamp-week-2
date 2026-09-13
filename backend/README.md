# backend/

FastAPI + SQLAlchemy + Pydantic v2 backend, implemented against
`../openapi.yaml`, backed by SQLite (auto-created and seeded on first
run, no migrations — see `product-spec.md` section 7.1). Dependencies
managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` +
`uv.lock`).

## Run

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Test

From the repo root (uses the top-level `pytest.ini` / `tests/`):

```bash
uv run --project backend pytest
```
