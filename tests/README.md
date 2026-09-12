# tests/

Backend unit tests for the FastAPI app (`test_tables.py`,
`test_availability.py`, `test_reservations.py`, `test_validation.py`,
`test_overlap_boundaries.py` — 38 tests total), run with `pytest` from
the repo root (see the top-level `pytest.ini`, which puts `backend/` on
`sys.path`). Each test gets a fresh, seeded in-memory SQLite database
via the `client` fixture in `conftest.py`.

The frontend smoke test lives in `frontend/tests/` instead (co-located
with the Vite/Vitest project it exercises) — run it with `npm test`
from `frontend/`.
