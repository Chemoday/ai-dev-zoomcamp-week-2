# tests/

Backend unit tests for the FastAPI app (`test_tables.py`,
`test_availability.py`, `test_reservations.py`), run with `pytest` from
the repo root (see the top-level `pytest.ini`, which puts `backend/` on
`sys.path`). Each test gets a fresh, seeded in-memory SQLite database
via the `client` fixture in `conftest.py`.

A frontend smoke test covering the main guest booking flow is still
outstanding — see `_plan/roadmap.md` step 6.
