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

## 6. Tests wrap-up — done
- [x] Confirm backend unit tests cover the behavior in the spec and
      contract
- [x] Add a frontend smoke test covering the main guest booking flow

Extensive backend testing pass (38 tests total, up from 17):
- `tests/test_validation.py` (14 tests): 422s for bad `table_type`,
  out-of-range `grid_x`/`grid_y`, missing fields, out-of-range
  `start_time`/`duration`, empty `customer_name`, malformed dates, and
  missing/invalid `party_size` on `/api/availability`.
- `tests/test_overlap_boundaries.py` (7 tests): exercises the exact
  overlap formula from product-spec.md §3.3 — back-to-back bookings
  that only touch are allowed, any real overlap (partial, nested,
  identical) conflicts, different tables/dates never conflict.
- **Bug found and fixed**: `start_time` (10-21) and `duration` (1-4)
  were validated independently, so a booking could run past the 22:00
  close (e.g. `start_time=21, duration=2` → ends at 23:00). Added a
  `model_validator` on `ReservationCreate` (`backend/app/schemas.py`)
  enforcing `start_time + duration <= 22`, plus the same check in the
  `/api/availability` handler. This also caught the *same* bug already
  present in the seed data (Dala Okonkwo's booking, `21:00 + 2h`) —
  fixed in both `backend/app/main.py` and `frontend/src/services/api.js`
  (duration `2` → `1`) so the seeded demo data is valid in both places.

Frontend: added Vitest + Vue Test Utils (`frontend/tests/`,
`npm test`). `booking-flow.spec.js` mocks `services/api` and drives the
real `App.vue` through the guest flow: see an available table → open
the reservation modal → submit → success state → modal auto-closes →
grid re-fetches and shows the table as reserved.

While writing it, found and fixed a real frontend bug: `HOURS` in
`utils/format.js` was `[11..22]`, but the backend only accepts
`start_time` in `10..21` (and now also enforces the closing-time rule)
— so the time picker offered an invalid 22:00 slot and never offered
the valid 10:00 opening slot. Fixed to `[10..21]`. Also added the
missing "4 hours" option to `ReservationModal`'s duration picker (the
backend allows 1-4, the UI only offered 1-3).

## 7. Wrap-up deliverables — done
- [x] `README.md` — how to run frontend + backend locally (see spec
      section 7.2 for the quickstart commands)
- [x] `docs/ai-usage-report.md` — log where/how AI tools were used
- [x] Confirm the repo matches the Module 2 deliverable list from
      `_plan/lesson.md` / `_plan/module_syllabus.md`

`docs/ai-usage-report.md` filled in with a real, dated log (sourced
from `git log`) of every AI-assisted step and how each was verified,
per `_plan/lesson.md`'s "verify each step" principle.

Final deliverable check against `_plan/lesson.md`'s list — all present:
`product-spec.md`, `AGENTS.md` (+ `CLAUDE.md`), `frontend/`, `backend/`,
`openapi.yaml`, `tests/` (+ `frontend/tests/`), `docs/ai-usage-report.md`.
Runs locally per `README.md`, persists in SQLite, passes its own tests
(38 backend + 1 frontend, both green in CI).

`module_syllabus.md` §9 additionally lists `/docker-compose.yml` and
`/.github/workflows` — the latter now exists (added for test-on-push
CI, matching this module's "verify each step" spirit); `docker-compose.yml`
is intentionally still absent, since containerization/deployment is
explicitly Module 3 per `_plan/lesson.md` and the top of this file.

Module 2 is complete.

## Notes
- Frontend-before-backend, mocked-before-real is intentional — it lets
  the UI drive what the contract actually needs to be, instead of
  guessing the API shape upfront.
- Reference app for the pattern (different domain, same flow):
  https://github.com/alexeygrigorev/interview-canvas-share
