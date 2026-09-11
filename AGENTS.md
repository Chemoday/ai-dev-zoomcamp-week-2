# Interactive Restaurant Table Reservation System

This is the Module 2 project for the AI-dev Zoomcamp. See
`product-spec.md` for the full, authoritative spec (business logic, API
contract, UI/UX, implementation roadmap), `_plan/roadmap.md` for the
step-by-step plan, and `_plan/lesson.md` / `_plan/module_syllabus.md`
for the module context.

## Tech stack

- **Frontend**: Vue 3, **Composition API only**, using `<script setup>`
  syntax in every component (no Options API, no bare `setup()`
  function), Vite, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy (synchronous ORM), Pydantic v2
- **Database**: SQLite

## Build order

Per `_plan/roadmap.md`: frontend prototype + mock service layer first,
then the OpenAPI contract, then the FastAPI backend (mock store first,
then SQLite). Do not build the backend ahead of the contract.

## AI code-generation guardrails

From `product-spec.md` section 8 — follow these exactly:

- **Field naming**: always `snake_case` in JSON payloads/responses
  (`table_number`, not `tableNumber`)
- **Vue syntax**: strictly Vue 3 `<script setup>` SFC syntax — never
  generate Vue 2 Options API code
- **CSS layout**: plain Tailwind CSS Grid (`grid grid-cols-6 gap-3`) —
  do not install drag-and-drop or external layout packages
- **Time/date safety**: no JS `Date` object math — use integer hours
  (`10..21`) and plain ISO date strings (`YYYY-MM-DD`)

## Conventions

Not yet decided beyond the above (testing, linting, folder layout, etc.
will be added here as those decisions are made in later steps).
