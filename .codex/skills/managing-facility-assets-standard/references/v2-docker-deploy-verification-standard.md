# v2 Docker Deploy Verification Standard

This v2 workflow standard defines how Codex should verify repository changes in this project after implementation work.

## When It Applies

- Any non-trivial backend or frontend code change
- Any change that affects runtime behavior, API behavior, database structure, or Docker image contents

## Required Verification Flow

1. Perform local code-level verification that fits the change.
2. Rebuild and restart the affected Docker services with `docker compose`.
3. Confirm the containers are up after the rebuild.
4. Verify the changed behavior from the running Docker deployment when feasible.

## Expectations

- Treat Docker deployment verification as part of normal completion, not an optional extra step.
- If a schema-additive backend change depends on startup sync, the Docker restart is the step that applies it.
- If Docker deployment cannot be completed, clearly report the blocker and what was verified instead.

## Default Command Pattern

- Prefer `docker compose up -d --build` for the affected stack.
- Follow with `docker compose ps` and targeted logs or HTTP checks when needed.
