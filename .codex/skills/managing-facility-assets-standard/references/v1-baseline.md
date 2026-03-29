# v1 Baseline

This file defines the current repository as the official `v1` baseline.

## Definition

- `v1` is the integrated repository state that currently exists in this repository.
- `v1` is operational reality, not a proposal.
- Existing implemented features belong to `v1` even if older notes once described them as future work.

## Stack and Entrypoints

### Backend

- App entry: `backend/app/main.py`
- Database/session: `backend/app/core/database.py`
- Schema sync: `backend/app/core/schema_sync.py`
- Default collection scripts: `backend/app/core/default_collect_scripts.py`

### Frontend

- Router entry: `frontend/src/router/index.js`
- Main page groups:
  - `frontend/src/pages/assets`
  - `frontend/src/pages/dashboard`
  - `frontend/src/pages/reports`
  - `frontend/src/pages/settings`

## Backend Categories

### Route Groups

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

### Model Domains

- Master data:
  - locations
  - groups
  - equipment types
  - OS catalogs
  - antivirus catalogs
  - departments
  - persons
  - person-group roles
- Asset core:
  - assets
  - asset code sequences
  - asset change log
- Hardware detail:
  - systems
  - CPUs
  - memories
  - disks
  - GPUs
  - NICs
- Software/detail collection:
  - installed products
  - hotfixes
  - processes
  - local accounts
  - network connections
- Collection infrastructure:
  - collect scripts
  - collect runs
- Custom fields and layouts
- Report templates and form mappings
- Record domains:
  - inspection
  - event log
  - console access
  - seal
  - password

## Frontend Categories

### Asset Pages

- `/assets`
- `/assets/register`
- `/assets/details`
- `/assets/new`
- `/assets/:id/edit`

### Report Pages

- `/reports`
- `/reports/evtx`
- `/reports/form-templates`
- `/reports/form-report`

### Settings Pages

- `/settings/locations`
- `/settings/groups`
- `/settings/os`
- `/settings/av`
- `/settings/persons`
- `/settings/departments`
- `/settings/equipment-types`
- `/settings/db`

## Current Functional Baseline

### Asset List

- Column configuration is driven by actual API-available fields.
- Column groups are organized by source table or domain.
- Multi-valued fields such as IPs, NICs, accounts, and custom-field-derived columns render as stacked values in a single cell.
- Custom fields can appear as dynamic columns based on synchronized JSON values.

### Asset Detail Workspace

- `/assets/details` is a review and correction workspace, not a bulk entry page.
- The left-side list is grouped by equipment-type tabs.
- Common fields can be edited directly in the list.
- Detail review opens in a modal.

### Asset Detail Tabs

- Common info
- Collected hardware
- Collected software
- Custom fields
- Collect upload
- Change log

### Collection Upload

- Collection scripts can be downloaded individually.
- A bundle script can be downloaded for all active collection domains.
- Upload accepts JSON and legacy ZIP flows.
- Upload stores raw collection runs and normalized detail rows.

### Current Collection Domains

- Summary
- Installed software
- Processes
- Local accounts
- Network connections
- Windows hotfixes

### Reports

- Report template management
- Form-template mappings
- HTML preview
- XLSX generation
- EVTX-related upload/report support

## Current Data Concepts

### Asset Master

- `assets` stores operational master state.
- Representative selections live in the asset master:
  - `representative_nic_id`
  - `representative_account_id`
- `last_collected_at` is updated when collection data is saved.

### NIC Concept

- NIC detail lives in `asset_hw_nics`.
- Representative NIC is selected by id from collected NIC rows.
- Unused NIC is stored by `asset_hw_nics.is_unused`.
- Asset list separates:
  - active IPs
  - unused IPs
  - representative NIC
  - used NICs
  - unused NICs

### Account Concept

- Local account detail lives in `asset_sw_accounts`.
- Representative account is selected by id from collected account rows.
- There is no separate unused-account flag.
- Unused-account behavior is represented by editing the collected `enabled` value.

### Custom Field Concept

- Structured custom field rows remain in `asset_custom_fields`.
- `assets.custom_fields_json` mirrors them for fast list/detail rendering.
- Global custom-field keys can be created from the detail-list workflow.

### Group Code Concept

- `code` is the internal unique key.
- `display_code` is the user-facing code.
- COM-style grouping relies on display behavior without breaking internal uniqueness.

## Current Working Rules for Codex

- Keep repository-local behavior authoritative over older bundles or comments.
- When adding a new collected domain, update the script, parser, storage, API, and frontend in the same change set.
- Keep `/assets` and `/assets/details` consistent with the current master/detail separation.
- Prefer additive schema evolution unless the user explicitly requests cleanup or deletion.
