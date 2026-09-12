# Roadmap — Interactive Restaurant Table Reservation System (Module 2)

Step-by-step plan, following `product-spec.md` section 6's own
implementation roadmap, with the Module 2 deliverables from
`_plan/lesson.md` folded in. Deployment/Docker/CI-CD is out of scope
here — that's Module 3.

## 1. Product spec — done
- [x] `product-spec.md` written: scope, stack, business logic, API
      contract, UI/UX spec, and AI-generation guardrails

## 2. Phase 1 — Frontend first, with a mock layer — done
- [x] Read `docs/ui-spec.md` for the full screen/state/transition brief
      before generating any frontend code
- [x] Initialize Vite + Vue 3 + Tailwind CSS project in `frontend/`
- [x] Implement `src/api/mock_api.js`: in-memory mock store (9 default
      tables, 4 initial reservations, ~200ms simulated network delay),
      matching the contract in spec section 4
- [x] Build components: `AppHeader`, `FilterBar`, `FloorGrid`,
      `FloorCell`/`TableShape`, `ReservationModal`, `AddTableModal`,
      `AdminDrawer`, `ReservationsList`, `ToastStack`, `DemoPanel`
- [x] Verify full client-side reactivity against mocks (party size
      changes, booking, role toggle, adding/deleting tables) — no real
      backend yet

Built with Claude Design, committed raw, then reconciled: renamed
`pos_x`/`pos_y` → `grid_x`/`grid_y` and `start_hour`/`duration_hours` →
`start_time`/`duration` throughout `frontend/src`, and moved the mock
API from `src/api/mock_api.js` to `src/services/api.js` per spec
section 2's layout. Verified with `npm run build`.

## 3. Formalize the OpenAPI contract — done
- [x] Write `openapi.yaml` from spec section 4 (Table/Reservation
      schemas, all REST endpoints, error responses) — this becomes the
      binding contract both sides implement against from here on

Written to match what `frontend/src/services/api.js` actually
implements (validated with `openapi-spec-validator`), which in a few
spots is more precise than `product-spec.md` §4's narrative sketch —
see the Notes block at the bottom of `openapi.yaml`: `GET /api/availability`
takes a required `party_size` and returns one entry per table
(`is_reserved`/`fits_party`/`is_available`) instead of a bare boolean
map, and `table_number` is an integer, not the spec's string example.

## 4. Phase 2 — FastAPI backend — done
- [x] Scaffold `backend/app/` (`main.py`, `database.py`, `models.py`,
      `schemas.py`, `crud.py`) per spec section 2's directory layout
- [x] Implement endpoints against `openapi.yaml` / spec section 4,
      backed by SQLite via SQLAlchemy (`Base.metadata.create_all` in a
      lifespan handler, no Alembic, per spec section 7)
- [x] Write backend tests for the key endpoints (add/list/book/delete,
      availability/overlap logic, delete-with-active-reservations guard)

17 tests pass (`tests/test_tables.py`, `test_availability.py`,
`test_reservations.py`), each against a fresh in-memory SQLite DB
(`tests/conftest.py`). Manually smoke-tested with `uvicorn` + `curl`
and confirmed the generated `/openapi.json` paths match `openapi.yaml`.
Seeds the same 9 tables as `frontend/src/services/api.js` (not the 5
from `product-spec.md` §7.1, which also used string table numbers) so
Phase 3 integration shows an identical floor plan to what the frontend
was built against.

## 5. Phase 3 — Integration — done
- [x] Flip `USE_MOCKS = false` in `frontend/src/services/api.js`,
      point real `fetch`/`axios` calls at `http://localhost:8000/api`
- [x] Test end-to-end: reserve a table as guest → status turns
      red/reserved → row persists in SQLite; switch to staff view →
      delete a table → deletion-safety guard triggers if it has active
      bookings

`services/api.js` now dispatches every exported function to either the
mock store or a real `fetch` against the backend based on `USE_MOCKS`
(currently `false`), so components never needed to change. The
mock-only "Demo states" panel (`DemoPanel.vue`) is now gated behind
`USE_MOCKS` in `AppHeader.vue`/`App.vue` since its error-simulation
flags and reset/clear actions don't apply to a real backend.

Verified end-to-end by running the real backend and driving
`frontend/src/services/api.js` directly with Node (it's a plain ES
module, no bundler magic) against it: guest booking → table turns
reserved and the reservation persists via `GET /api/reservations`;
overlapping booking → `409`; staff delete of a table with active
bookings → blocked with `400`; staff add + delete of a table without
bookings → succeeds. Also confirmed the backend's CORS headers permit
the Vite dev origin (`http://localhost:5173`), and `npm run build`
still succeeds with `USE_MOCKS = false`.

## 6. Tests wrap-up
- [ ] Confirm backend unit tests cover the behavior in the spec and
      contract
- [ ] Add a frontend smoke test covering the main guest booking flow

## 7. Wrap-up deliverables
- [ ] `README.md` — how to run frontend + backend locally (see spec
      section 7.2 for the quickstart commands)
- [ ] `docs/ai-usage-report.md` — log where/how AI tools were used
- [ ] Confirm the repo matches the Module 2 deliverable list from
      `_plan/lesson.md` / `_plan/module_syllabus.md`

## Notes
- Frontend-before-backend, mocked-before-real is intentional — it lets
  the UI drive what the contract actually needs to be, instead of
  guessing the API shape upfront.
- Reference app for the pattern (different domain, same flow):
  https://github.com/alexeygrigorev/interview-canvas-share
