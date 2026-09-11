# backend/

FastAPI + SQLAlchemy + Pydantic v2 backend, implemented against
`../openapi.yaml`, backed by SQLite (auto-created and seeded on first
run, no migrations — see `product-spec.md` section 7.1).

## Run

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Test

From the repo root (uses the top-level `pytest.ini` / `tests/`):

```bash
source backend/venv/bin/activate
pytest
```
