---
name: managing-facility-assets-standard
description: Repository-standard skill for the managing-facility-assets project. Use when Codex is working in this repository and needs the current codebase structure, feature map, domain concepts, versioning rules, and project-specific implementation constraints. The repository itself is the canonical v1 baseline, and any future standard or concept expansion must be documented as v2 instead of silently rewriting history.
---

# Managing Facility Assets Standard

Use this skill as the repository-specific source of truth for Codex work in this project.

## Start Here

1. Read `references/v1-baseline.md`.
2. Read `references/versioning-rules.md`.
3. If the task touches Korean text, Korean filenames, Desktop files, Windows paths, or any PowerShell output that may contain Korean, first apply the UTF-8 handling rule below before trusting terminal output.
4. Read `references/current-system-flow.md` when the task touches DB structure, backend routes/services, frontend pages/stores, or end-to-end data flow.
5. Read `references/v2-frontend-list-standard.md` only when the task touches frontend list or table behavior.
6. Read `references/v2-powershell-utf8-standard.md` when the task involves reading or verifying Korean text through PowerShell.
7. Treat the live repository as canonical when older notes or legacy bundles conflict with the current code.

## Immediate Korean Path Rule

When PowerShell work may involve Korean text or filenames, do this before reading or trusting output:

```powershell
chcp 65001 > $null
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
```

Then prefer:

```powershell
Get-Content -Encoding UTF8 <path>
```

Treat mojibake Korean output as a terminal decoding problem first. This rule also applies to:

- Korean filenames on the Windows Desktop
- Korean workbook names such as uploaded `.xlsx` templates
- copied Windows paths that contain Korean folder or file names

## Codebase Categories

### Backend

- App entry: `backend/app/main.py`
- Data model layers:
  - `backend/app/models`
  - `backend/app/schemas`
  - `backend/app/api/routes`
  - `backend/app/services`
- Backend changes must stay aligned across model, schema, route, and service layers.

### Frontend

- Main route pages live under `frontend/src/pages`
- Shared API modules live under `frontend/src/api`
- Shared state lives under `frontend/src/stores`
- Asset detail tabs live under `frontend/src/pages/assets/tabs`
- Shared UI building blocks live under `frontend/src/components`

### Codex Standards

- Preserve the current stack: FastAPI, async SQLAlchemy, PostgreSQL, Vue 3, Pinia, Axios, Docker Compose.
- Before reading or verifying any Korean path or filename through PowerShell, apply the UTF-8 session setup from `Immediate Korean Path Rule`.
- When adding a new SQLAlchemy model, also register it in `backend/app/models/__init__.py`.
- Prefer extending current flows over creating parallel patterns.
- Keep schema synchronization additive by default. Do not introduce silent destructive schema mutations.
- Treat mojibake Korean labels and comments as non-authoritative. Use current user intent and nearby clean code as the wording source.
- Do not introduce new mojibake into code, seeds, or DB defaults. For Korean user-facing literals that must survive editor, shell, and Docker encoding differences, prefer ASCII-safe storage such as Python `\u` escapes or HTML entities, then verify both source rendering and persisted DB values before finishing.

## Current Feature Categories

### Asset Core

- Asset list: `/assets`
- Asset register and edit flows
- Asset detail workspace: `/assets/details`
- Bulk registration and preview code issuance

### Master Data

- Locations
- Groups
- Equipment types
- OS catalogs
- Antivirus catalogs
- Departments
- Persons
- DB viewer

### Detail Domains

- Hardware detail
- Software detail
- Custom fields
- Collection upload
- Change log
- Layout handling
- Optical drive detail

### Collection Domains

- PowerShell collection scripts
- Script bundle download
- Raw collection run storage
- Normalized hardware/software/account/network storage
- Optical drive collection via `Win32_CDROMDrive`

### Report Domains

- Form templates
- Template mappings
- Mapping modal sample-data preview
- Workbook-style template preview
- Workbook-style filled-report preview
- HTML preview
- XLSX generation
- EVTX upload and report-related data flows

## Current Domain Concepts

### Asset Master vs Collected Detail

- `assets` is the master table for operational asset state.
- Collected hardware, software, account, and connection data belong in 1:N child tables.
- Do not move collected detail back into flattened master columns unless the user explicitly wants a new standard.

### Representative vs Non-Representative Data

- Representative NIC is selected by `assets.representative_nic_id`.
- Representative account is selected by `assets.representative_account_id`.
- Non-representative NIC and account data remain in their own child tables.

### Unused NIC Concept

- NIC rows use `asset_hw_nics.is_unused`.
- Asset list IP/NIC views must separate active and unused data.
- Representative NIC cannot stay unused at the same time.

### Unused Account Concept

- Account rows do not use a separate unused flag.
- “Unused account” is represented by editing the collected `enabled` value on `asset_sw_accounts`.
- Representative account should remain enabled.

### Custom Field Concept

- Custom fields are still stored in `asset_custom_fields`.
- `assets.custom_fields_json` is the synchronized JSON snapshot for easier list/detail rendering.
- Global custom field keys can be created and removed from the detail list workflow.

### Group Code Concept

- `group_nodes.code` is the internal unique code.
- `group_nodes.display_code` is the user-facing code.
- For COM-like cases, UI and generated identifiers may use `display_code` while queries and uniqueness continue to rely on `code`.

## Working Expectations

### When touching `/assets`

- Keep column configuration based on actual API-available fields.
- Keep column groups organized by source table or domain.
- Multi-valued fields should render as row-stacked values inside a single cell instead of ellipsis truncation.

### When touching `/assets/details`

- Treat it as a one-asset operational review workspace, not a bulk entry screen.
- Keep list-level common-field editing lightweight.
- Keep detailed review in the modal tabs.
- Preserve the separation of common info, collected hardware, collected software, custom fields, collect upload, and change history.
- Keep collected hardware tabs aligned with supported collection domains, including optical drives.

### When touching collection

- Collection scripts must stay consistent with parser expectations.
- Bundle script output must remain compatible with single-script output.
- When a new collected domain is introduced, update:
  - script definitions
  - parser normalization
  - storage table
  - API response
  - frontend display

### When touching `/reports/form-templates`

- Keep `FIELD_CATALOG`, backend data-source fetch definitions, and frontend source selectors aligned.
- Mapping modal preview should stay inside the modal and use internal scrolling for large tables.
- Mapping currently supports repeat direction `down` and `right`, aggregate modes for repeatable sources, and `output_template` placeholders `{value}`, `{secondary}`, `{count}`.
- Horizontal repeat placement must respect merged cells and skip merged-child targets.

### When touching `/reports/form-report`

- Prefer workbook-style preview of the filled XLSX when users need fidelity comparable to the template workbook view.
- Keep report preview and downloaded XLSX driven by the same generation output so preview matches export.

## Versioning Rule

- The live repository is the v1 baseline.
- Already-implemented repository behavior belongs to v1 unless a new standard is explicitly introduced as v2.
- New architecture rules, new cross-cutting concepts, or new Codex workflow standards must be documented as v2 instead of silently overwriting v1.

## References

- v1 baseline: `references/v1-baseline.md`
- Versioning rules: `references/versioning-rules.md`
- Current DB/backend/frontend flow: `references/current-system-flow.md`
- v2 frontend list standard: `references/v2-frontend-list-standard.md`
- v2 PowerShell UTF-8 standard: `references/v2-powershell-utf8-standard.md`
