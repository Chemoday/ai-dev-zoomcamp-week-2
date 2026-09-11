Module 2 — Build and Ship an AI-Assisted Full-Stack App
7. Module 2 positioning
Module 2 is already strong and should remain the backbone of the practical course. It should take students from idea to deployed app.

The current Snake app structure is still a good choice because it is visual, interactive, and small enough to complete while still requiring frontend, backend, API, database, tests, Docker, deployment, and CI/CD.

8. Module 2 content flow
Lesson 2.1 — Product spec and acceptance criteria
Before using a bootstrapper, students write:

product-spec.md
user stories
acceptance criteria
non-goals
technical constraints
Example:

# Product spec

## App

Snake Arena

## Users

- anonymous visitor
- registered player
- admin / maintainer

## Features

- play snake
- register/login
- leaderboard
- watch simulated games
- submit score

## Non-goals

- real-time multiplayer in this version
- payment
- social login

## Acceptance criteria

- user can play a local game
- user can submit score
- leaderboard shows top scores
- app works locally with Docker Compose
- backend tests pass
- frontend smoke test passes
Lesson 2.2 — Frontend prototype
Tools

Lovable
Bolt
Replit Agent
Cursor / Claude Code / Codex as fallback
Goal

Generate an initial frontend, then pull it into a normal repo workflow.

Teaching point

The prototype is not the final product. It is a first draft.

Lesson 2.3 — OpenAPI contract
Students extract or write:

openapi.yaml
Teach:

API-first development
contract between frontend and backend
schema validation
generated clients/servers
how AI can hallucinate endpoints
Lesson 2.4 — Backend implementation
Options

FastAPI
Django
Node/Express
The default should probably remain FastAPI because it fits the current material.

Topics

backend scaffolding
uv dependency management
OpenAPI-guided implementation
mock DB first
tests first for key endpoints
Lesson 2.5 — Database support
Topics

SQLite for local tests
Postgres for Docker/production
SQLAlchemy or Django ORM
migrations
integration tests
Lesson 2.6 — Containerization
Deliverables

Dockerfile
docker-compose.yml
.env.example
Lesson 2.7 — Deployment
Options

Render
Fly.io
Railway
Cloud Run
Keep the default simple.

Lesson 2.8 — CI/CD
Required

backend tests
frontend tests
integration tests if feasible
build check
deployment trigger
9. Module 2 deliverable
At the end of Module 2, each student should have:

/product-spec.md
/AGENTS.md
/CLAUDE.md or equivalent
/frontend
/backend
/openapi.yaml
/docker-compose.yml
/tests
/.github/workflows
/docs/ai-usage-report.md
The app should be deployed and the repository should be reproducible.

