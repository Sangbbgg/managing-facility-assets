---
name: managing-facility-assets-standard
description: Project-standard skill for the managing-facility-assets repository. Use when Codex is working in this repository or implementing related backend, frontend, database, report, or Codex-process changes and needs the repository-specific architecture, versioning rules, naming rules, feature boundaries, and consistency expectations. The current repository state is the v1 baseline. Any newly introduced standard, concept, or architectural expansion must be documented as v2 updates instead of rewriting v1 history.
---

# Managing Facility Assets Standard

Use this skill as the repository-specific source of truth for Codex work on this project.

## Start Here

1. Read `references/v1-baseline.md`.
2. Read `references/versioning-rules.md`.
3. Treat the live repository as canonical when the legacy bundle conflicts with current code.

## Working Rules

- Preserve the current stack: FastAPI, SQLAlchemy async, PostgreSQL, Vue 3, Pinia, Axios, Docker Compose.
- Keep backend resources aligned across `models`, `schemas`, `api/routes`, and router registration in `backend/app/main.py`.
- When adding a new SQLAlchemy model, also update `backend/app/models/__init__.py`.
- Prefer extending existing flows over creating parallel patterns.
- Preserve the current route topology unless the task explicitly requires route changes.
- Treat mojibake Korean comments and labels as non-authoritative. Verify intended wording from nearby code or user intent before propagating it.
- Treat the current repository shape as `v1`.
- Do not retroactively reclassify existing repository features as `v2`.
- When introducing new standards or concepts, append them as `v2` updates and keep the `v1` baseline readable as a historical snapshot.

## v1 Baseline Scope

- Asset lifecycle: list, register, detail, bulk register, code preview.
- Master data: locations, groups, equipment types, OS catalog, antivirus catalog, departments, persons.
- Detail domain: hardware, software, custom fields, collection scripts, layouts, change history.
- Report domain: form templates, mappings, HTML preview, XLSX generation.

## Frontend Expectations

- Keep major route pages under `frontend/src/pages/`.
- Reusable visual building blocks belong under `frontend/src/components/`.
- Current asset detail tabs live under `frontend/src/pages/assets/tabs/`; do not move them unless refactoring intentionally.
- Keep stores lean. Do not introduce a new store unless state is shared enough to justify it.

## Backend Expectations

- Use route modules under `backend/app/api/routes/`.
- Keep business logic in `backend/app/services/` when it exceeds trivial CRUD.
- Keep schema synchronization safe for additive changes; avoid silent destructive schema mutations.
- Preserve asset code issuance semantics and do not bypass sequence handling.

## Versioning Rule

- `v1` means the current integrated repository state after the Claude-driven second revision.
- `v2` means any future standard, architecture rule, domain expansion, or development convention introduced after this baseline was declared.
- When implementing `v2`, update the dedicated versioning references in the same change set.

## References

- v1 baseline: `references/v1-baseline.md`
- Versioning rules: `references/versioning-rules.md`
- v2 frontend list standard: `references/v2-frontend-list-standard.md`

Load those references only as needed.
