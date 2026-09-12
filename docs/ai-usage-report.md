# AI usage report

A log of where and how AI tools were used to build the Interactive
Restaurant Table Reservation System, for Module 2's deliverable
requirement.

## Approach

Per `_plan/lesson.md`: "the goal is not to let an AI tool build
everything unchecked... you verify each step." Every entry below has a
concrete verification step attached — a test suite, a build, a live
run against a real server — rather than accepting AI output on faith.

## Format

For each entry: date, tool used, what it was used for, and how the
output was verified/reviewed before accepting it.

| Date | Tool | Task | Verification |
|------|------|------|---------------|
| 2026-09-12 | Claude Code (Sonnet 5) | Wrote `product-spec.md` structure, `docs/ui-spec.md` (UI/UX brief), `CLAUDE.md`/`AGENTS.md`, and the phased `_plan/roadmap.md` | Reviewed each doc for internal consistency and cross-checked against `_plan/lesson.md` / `module_syllabus.md` |
| 2026-09-12 | Claude Design | Generated the initial Vue 3 + Vite + Tailwind frontend prototype (components, mock API layer, design tokens) from `docs/ui-spec.md` and `product-spec.md` | Read every generated file before committing; verified with `npm run build` |
| 2026-09-12 | Claude Code (Sonnet 5) | Reconciled frontend field names (`pos_x`/`pos_y`, `start_hour`/`duration_hours`) and file layout to match the intended API contract | Re-ran `npm run build` after each rename across all affected files |
| 2026-09-12 | Claude Code (Sonnet 5) | Authored `openapi.yaml` from `product-spec.md` section 4, resolving a few spots where the frontend's actual behavior was more precise than the spec's narrative sketch | Validated with `openapi-spec-validator`; diffed against FastAPI's generated `/openapi.json` |
| 2026-09-12 | Claude Code (Sonnet 5) | Implemented the FastAPI backend (`models.py`, `schemas.py`, `crud.py`, `main.py`) against `openapi.yaml` | 17 initial unit tests plus a manual `curl` smoke test against a running `uvicorn` server |
| 2026-09-12 | Claude Code (Sonnet 5) | Wired the frontend to the real backend (`USE_MOCKS = false`) | Drove the real `services/api.js` module with Node against the live backend, exercising the booking, conflict, and delete-blocked paths end to end |
| 2026-09-12 | Claude Code (Sonnet 5) | Extensive backend test pass: request-validation edge cases and overlap-boundary cases | Found and fixed a real gap (reservations could run past the 22:00 close); grew the suite to 38 passing tests |
| 2026-09-12 | Claude Code (Sonnet 5) | Added a Vitest frontend smoke test for the guest booking flow | Found and fixed a time-picker range bug and a missing duration option surfaced while writing the test; test passes, `npm run build` still succeeds |
| 2026-09-12 | Claude Code (Sonnet 5) | Added GitHub Actions CI (backend + frontend test jobs) | Watched the live workflow run to completion on GitHub after pushing |
