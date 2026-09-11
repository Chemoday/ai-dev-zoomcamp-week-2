# Interactive Restaurant Table Reservation System

This is the Module 2 project for the AI-dev Zoomcamp. See
`product-spec.md` for the full, authoritative spec (business logic, API
contract, UI/UX, implementation roadmap, and AI-generation guardrails),
`docs/ui-spec.md` for the detailed screen/state/transition brief used
for frontend generation, and `_plan/module_syllabus.md` for the module
context and deliverable list.

## Tech stack

- **Frontend**: Vue 3, **Composition API only**, using `<script setup>`
  syntax in every component (no Options API, no bare `setup()`
  function), Vite, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy (synchronous ORM), Pydantic v2
- **Database**: SQLite

## Conventions

See `product-spec.md` section 8 ("Guardrails for AI Code Generation")
for concrete rules (JSON field naming, Vue syntax, CSS layout, date/time
handling). Further conventions (testing, linting, etc.) will be added
here as those decisions are made in later steps.
