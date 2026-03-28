# v1 Baseline

This file defines the current repository as the official `v1` baseline.

## Definition

- `v1` is the integrated repository state after the Claude-driven second revision, as it exists now.
- `v1` is not a proposal. It is the current operating standard.
- Existing features that were historically described as legacy `v2` or `v3` are considered part of `v1` because they are already implemented in the repository.

## Backend

- App entrypoint: `backend/app/main.py`
- Core packages:
  - `backend/app/models`
  - `backend/app/schemas`
  - `backend/app/api/routes`
  - `backend/app/services`

### Registered route groups in v1

- `health`
- `locations`
- `groups`
- `assets`
- `catalogs`
- `persons`
- `reports`
- `evtx`
- `form_templates`
- `hardware`
- `software`
- `custom_fields`
- `collect`
- `layouts`
- `admin`

### Model domains in v1

- Master data: location, group, equipment type, OS, antivirus, department, person
- Asset core: assets, asset code sequences, asset change log
- Records: inspection, event log, console access, seal, password
- Detail domain: hardware, software, custom fields, layouts, collect scripts
- Form report domain: report form templates, report form mappings
- Report jobs: asynchronous report-related state

## Frontend

- Router entrypoint: `frontend/src/router/index.js`
- Main page groups:
  - `frontend/src/pages/assets`
  - `frontend/src/pages/dashboard`
  - `frontend/src/pages/reports`
  - `frontend/src/pages/settings`

### Important routes in v1

- `/assets`
- `/assets/register`
- `/assets/details`
- `/assets/new`
- `/assets/:id/edit`
- `/reports`
- `/reports/evtx`
- `/reports/form-templates`
- `/reports/form-report`
- `/settings/locations`
- `/settings/groups`
- `/settings/os`
- `/settings/av`
- `/settings/persons`
- `/settings/departments`
- `/settings/equipment-types`
- `/settings/db`

### State and API shape in v1

- API modules live under `frontend/src/api`
- Stores live under `frontend/src/stores`
- Asset detail tabs currently live under `frontend/src/pages/assets/tabs`
- Form-template UI components live under `frontend/src/components/reports`

## v1 Design Intent

- Keep the repository operational without requiring the old external skill bundle.
- Treat the current codebase as the baseline standard for future Codex work.
- Favor repository-local standards over historical naming ideals when the code already diverged.
