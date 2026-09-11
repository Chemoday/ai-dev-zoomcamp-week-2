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

Built with Claude Design, committed raw. **Known drift to reconcile in
step 3**: the mock API uses `pos_x`/`pos_y` and
`start_hour`/`duration_hours`, while `product-spec.md` §4 specifies
`grid_x`/`grid_y` and `start_time`/`duration`; the file also lives at
`src/api/mock_api.js` rather than the spec's suggested
`src/services/api.js`. Decide whether `openapi.yaml` follows the spec's
original names or the frontend's actual names before writing it.

## 3. Formalize the OpenAPI contract
- [ ] Resolve the field-naming drift noted above (grid_x/grid_y vs
      pos_x/pos_y, start_time/duration vs start_hour/duration_hours)
- [ ] Write `openapi.yaml` from spec section 4 (Table/Reservation
      schemas, all REST endpoints, error responses) — this becomes the
      binding contract both sides implement against from here on

## 4. Phase 2 — FastAPI backend
- [ ] Scaffold `backend/app/` (`main.py`, `database.py`, `models.py`,
      `schemas.py`, `crud.py`) per spec section 2's directory layout
- [ ] Implement endpoints against `openapi.yaml` / spec section 4,
      backed by SQLite via SQLAlchemy (see spec section 7 for seeding:
      `Base.metadata.create_all`, no Alembic, auto-seed 5 tables on
      first startup)
- [ ] Write backend tests for the key endpoints (add/list/book/delete,
      availability/overlap logic, delete-with-active-reservations guard)

## 5. Phase 3 — Integration
- [ ] Flip `USE_MOCKS = false` in `frontend/src/services/api.js`,
      point real `fetch`/`axios` calls at `http://localhost:8000/api`
- [ ] Test end-to-end: reserve a table as guest → status turns
      red/reserved → row persists in SQLite; switch to staff view →
      delete a table → deletion-safety guard triggers if it has active
      bookings

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
