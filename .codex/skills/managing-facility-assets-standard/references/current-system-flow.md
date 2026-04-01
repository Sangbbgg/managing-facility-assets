# Current System Flow

This document is the current reference for how the repository is wired across database, backend, and frontend layers.

## 1. Database Flow

### Master Tables

- `location_nodes`
- `group_nodes`
- `equipment_types`
- `os_catalogs`
- `antivirus_catalogs`
- `departments`
- `persons`
- `person_group_roles`

Purpose:
- Keep tree, catalog, and person master data separate from asset detail.
- Provide source data for asset registration, filtering, grouping, and default manager resolution.

Current seeded default hierarchy:
- `group_nodes` root is `신인천빛드림본부`.
- Main seeded report/registration branches are `발전제어` and `신재생에너지`.
- `발전제어` currently splits into `기반` and `비기반`.
- `기반` currently continues through staged branches such as `1단계`, `2단계`, `1CC`, `2CC`, and leaf code nodes like `ST1`, `GT1`, `COM`.
- `신재생에너지` currently uses `연료전지` as the main seeded branch.
- `location_nodes` mirrors the operational site tree separately from `group_nodes`, so location filtering should follow the selected group branch instead of assuming identical ids or depth.

### Asset Master Table

- `assets`

Current role:
- Stores operational master state.
- Stores ids that point to selected representative detail rows.

Current key fields:
- `asset_code`
- `asset_name`
- `purpose`
- `importance`
- `install_date`
- `status`
- `group_id`
- `location_id`
- `equipment_type_id`
- `manager_id`
- `representative_nic_id`
- `representative_account_id`
- `last_collected_at`
- `custom_fields_json`

Important concept:
- Collected hardware, software, account, and connection detail should not be flattened into the asset master unless the user explicitly introduces a new standard.

### Hardware Detail Tables

- `asset_hw_systems`
- `asset_hw_cpus`
- `asset_hw_memories`
- `asset_hw_disks`
- `asset_hw_opticals`
- `asset_hw_gpus`
- `asset_hw_nics`

Purpose:
- Store 1:N hardware detail collected from scripts.

Important concept:
- `asset_hw_nics.is_unused` is the current unused-NIC flag.
- `assets.representative_nic_id` selects the representative NIC row.

### Software and Account Detail Tables

- `asset_sw_products`
- `asset_sw_hotfixes`
- `asset_sw_processes`
- `asset_sw_accounts`
- `asset_network_connections`

Purpose:
- Store installed software, hotfixes, processes, local accounts, and network connection detail per asset.

Important concept:
- There is no separate unused-account flag.
- Unused-account behavior is represented by editing `asset_sw_accounts.enabled`.
- `assets.representative_account_id` selects the representative account row.

### Collection Infrastructure Tables

- `collect_scripts`
- `asset_collect_runs`

Purpose:
- Manage downloadable scripts and keep raw collection payload history.

### Custom Field and Layout Tables

- `asset_custom_fields`
- `column_layouts`

Purpose:
- Store custom key/value fields and saved list/table layouts.

Important concept:
- `asset_custom_fields` is the source-of-truth row store.
- `assets.custom_fields_json` is the synchronized snapshot for faster list/detail rendering.

### Record and Report Tables

- `inspection_records`
- `event_log_records`
- `console_access_records`
- `seal_records`
- `password_records`
- `report_templates`
- `report_form_templates`
- `report_form_mappings`

Purpose:
- Store reporting source data and reporting templates/mappings.

## 2. Backend Flow

### App Bootstrap

Entry:
- `backend/app/main.py`

Startup flow:
1. `Base.metadata.create_all`
2. `sync_schema(engine)`
3. optional seed when `RESET_AND_SEED_ON_STARTUP=true`
4. `ensure_default_collect_scripts(session)`

Meaning:
- New tables are created automatically.
- Additive columns are synchronized automatically.
- Destructive schema cleanup still requires explicit manual handling.

### Route Topology

Registered route groups:
- `/api`
- `/api/locations`
- `/api/groups`
- `/api/assets`
- `/api/catalogs`
- `/api/persons`
- `/api/reports`
- `/api/evtx`
- `/api/form-templates`
- `/api/assets` for hardware/software/custom-fields subdomains
- `/api/collect`
- `/api/layouts`
- `/api/admin`

### Key Backend Flows

#### A. Asset List Flow

Route:
- `GET /api/assets/enriched`

Service:
- `backend/app/services/report_builder/data_fetchers.py`

Flow:
1. Load asset master rows.
2. Join master tables in memory.
3. Join representative NIC/account and custom field snapshot data.
4. Build frontend-friendly flattened rows.

Used by:
- `/assets`
- report/data export related flows that need flattened current asset rows

#### B. Asset Detail List Flow

Route:
- `GET /api/assets/detail-list`

Service:
- `backend/app/services/asset_detail_list.py`

Flow:
1. Load assets.
2. Load groups, locations, equipment types, persons, NICs, accounts.
3. Resolve explicit manager and fallback manager.
4. Return modal/list-friendly summary rows for `/assets/details`.

Used by:
- `/assets/details` left-side list and modal context summary

#### C. Asset Master CRUD Flow

Routes:
- `GET /api/assets`
- `POST /api/assets`
- `GET /api/assets/{asset_id}`
- `PATCH /api/assets/{asset_id}`
- `DELETE /api/assets/{asset_id}`

Primary logic:
- `backend/app/api/routes/assets.py`
- supporting services:
  - `asset_code.py`
  - `asset_manager_assignment.py`
  - `change_logger.py`

Flow:
1. Validate group/equipment type.
2. Issue asset code when creating.
3. Apply representative selections and manager rules.
4. Log change history on update.

#### D. Hardware Detail Flow

Routes:
- `GET /api/assets/{asset_id}/hardware`
- `GET /api/assets/{asset_id}/hardware/{hw_type}`
- `DELETE /api/assets/{asset_id}/hardware/{hw_type}/{hw_id}`
- `PATCH /api/assets/{asset_id}/hardware/nics/unused`

Role:
- Serve collected hardware detail.
- Allow unused-NIC selection persistence.

#### E. Software, Account, and Connection Flow

Routes:
- `GET /api/assets/{asset_id}/software`
- `GET /api/assets/{asset_id}/software/{sw_type}`
- `DELETE /api/assets/{asset_id}/software/{sw_type}/{sw_id}`
- `PATCH /api/assets/{asset_id}/software/accounts/status`

Role:
- Serve collected product, hotfix, process, account, and network connection data.
- Update account `enabled` values to represent unused-account status.

#### F. Custom Field Flow

Routes:
- `GET /api/assets/custom-fields/keys`
- `POST /api/assets/custom-fields/keys`
- `DELETE /api/assets/custom-fields/keys/{field_key}`
- `GET /api/assets/{asset_id}/custom-fields`
- `POST /api/assets/{asset_id}/custom-fields`
- `PATCH /api/assets/{asset_id}/custom-fields/{field_id}`
- `DELETE /api/assets/{asset_id}/custom-fields/{field_id}`
- `PATCH /api/assets/{asset_id}/custom-fields/reorder`

Role:
- Maintain per-asset custom rows.
- Maintain global key creation/removal workflow.
- Synchronize `assets.custom_fields_json`.

#### G. Collection Upload Flow

Routes:
- `GET /api/collect/scripts`
- `GET /api/collect/scripts/{key}/download`
- `GET /api/collect/script-bundle`
- `PATCH /api/collect/scripts/{key}`
- `POST /api/collect/upload`
- `POST /api/collect/parse-preview`
- `POST /api/collect/confirm`

Primary logic:
- `backend/app/core/default_collect_scripts.py`
- `backend/app/services/script_generator.py`
- `backend/app/services/collect_parser.py`

Flow:
1. Download individual or bundled PowerShell scripts.
2. Upload JSON or legacy ZIP.
3. Preview parse result if needed.
4. Normalize payload.
5. Store raw payload in `asset_collect_runs`.
6. Replace and rebuild normalized detail rows.
7. Remap representative NIC/account ids where possible.
8. Update `assets.last_collected_at`.

Current detail coverage:
- Summary collection includes optical drive inventory from `Win32_CDROMDrive`.
- Parser normalizes both legacy `optical_devices` values and structured `optical_drives` rows.
- Optical drive rows are stored in `asset_hw_opticals` and returned from hardware APIs.

#### H. Report Flow

Routes:
- `/api/reports/*`
- `/api/form-templates/*`
- `/api/evtx/upload`

Primary logic:
- `backend/app/services/report_builder/*`
- `backend/app/services/form_report_builder.py`

Role:
- Build report field catalogs, generate reports, and manage form-template mappings.

Current form-template/report behavior:
- `/api/form-templates/field-catalog` is driven by `form_report_builder.FIELD_CATALOG`.
- Form templates can be assigned to zero, one, or many equipment types.
- Templates with no assigned equipment types behave as global templates for backward compatibility.
- Form-template mapping supports repeat directions `down` and `right`.
- Repeat placement skips merged-child cells so repeated values land in visible worksheet cells.
- Non-repeat mappings on repeatable sources can use aggregate modes plus `output_template`.
- Mapping modal sample preview is backed by `/api/form-templates/data-preview`.
- `hw_optical` is part of the form-template data-source catalog.
- Form report preview and XLSX generation reject templates that do not match the selected asset equipment type.

## 3. Frontend Flow

### Router-Level Page Groups

Assets:
- `/assets`
- `/assets/register`
- `/assets/details`
- `/assets/new`
- `/assets/:id/edit`

Reports:
- `/reports`
- `/reports/evtx`
- `/reports/form-templates`
- `/reports/form-report`

Settings:
- locations
- groups
- OS
- AV
- persons
- departments
- equipment types
- DB viewer

### Frontend API Modules

- `assetsApi.js`
- `hardwareApi.js`
- `softwareApi.js`
- `customFieldsApi.js`
- `collectApi.js`
- `catalogsApi.js`
- `locationsApi.js`
- `groupsApi.js`
- `personsApi.js`
- `layoutsApi.js`
- `reportsApi.js`
- `formTemplatesApi.js`
- `evtxApi.js`
- `adminApi.js`

### Frontend Stores

- `assetStore.js`
- `assetHwStore.js`
- `assetSwStore.js`
- `catalogStore.js`
- `locationStore.js`
- `groupStore.js`
- `personStore.js`
- `layoutStore.js`
- `formTemplateStore.js`

### Key Frontend Flows

#### A. `/assets`

Primary page:
- `frontend/src/pages/assets/AssetListPage.vue`

Data source:
- `GET /api/assets/enriched`

Behavior:
- Renders flattened asset rows.
- Column config is driven by actual API keys.
- Column groups are organized by source table/domain.
- Multi-value fields render as stacked values inside a cell.

Important current groups:
- assets
- asset_custom_fields
- asset_hw_nics
- asset_sw_accounts
- group_nodes
- location_nodes
- equipment_types
- persons

#### B. `/assets/details`

Primary page:
- `frontend/src/pages/assets/AssetDetailPage.vue`

List source:
- `GET /api/assets/detail-list`

Modal sources:
- `GET /api/assets/{id}`
- `GET /api/assets/{id}/hardware`
- `GET /api/assets/{id}/software`
- custom field APIs
- collect APIs
- change-log API

Tabs:
- Common info
- Collected hardware
- Collected software
- Custom fields
- Collect upload
- Change log

Role:
- Operate as one-asset review and correction workspace.
- Support representative NIC/account selection.
- Support unused NIC/account editing.
- Support dynamic custom-field keys and values.
- Expose collected optical drive rows alongside other hardware domains.

#### C. `/assets/register` and `/assets/new`

Primary pages:
- `AssetRegisterPage.vue`
- `AssetFormPage.vue`

Role:
- Register assets and edit asset master data.
- Use master tables for groups, locations, persons, equipment types.
- Use asset code preview/issuance flow.

#### D. Settings Pages

Role:
- Maintain master tables used by asset registration, grouping, and default selections.
- Keep `groups` and `locations` tree structures authoritative.
- Keep person-group mapping authoritative for manager defaults.

#### E. Report Pages

Role:
- Manage report templates and form mappings.
- Trigger report generation and preview.
- Use workbook-style preview for both template mapping context and filled form-report output where fidelity matters.
- Keep template assignment and selection behavior aligned with equipment-type compatibility rules.
- For report preview and generation actions, show visible in-progress feedback and prevent duplicate triggering while the request is running.

## 4. End-to-End Reference Flows

### Flow 1: Asset List

DB:
- `assets`
- master tables
- NIC/account/custom-field snapshots

Backend:
- `GET /api/assets/enriched`
- `data_fetchers.fetch_asset_rows`

Frontend:
- `AssetListPage.vue`

### Flow 2: Asset Detail Review

DB:
- `assets`
- detail child tables

Backend:
- `GET /api/assets/detail-list`
- `GET /api/assets/{id}`
- detail APIs per tab

Frontend:
- `AssetDetailPage.vue`
- tab components under `frontend/src/pages/assets/tabs`

### Flow 3: Collection Upload

DB:
- `collect_scripts`
- `asset_collect_runs`
- hardware/software/account/connection tables

Backend:
- `collect.py`
- `script_generator.py`
- `collect_parser.py`

Frontend:
- `AssetCollectUploadTab.vue`

### Flow 4: Custom Field to Asset List

DB:
- `asset_custom_fields`
- `assets.custom_fields_json`

Backend:
- `custom_fields.py`
- `assets.py`
- `data_fetchers.py`

Frontend:
- `AssetDetailPage.vue`
- `AssetListPage.vue`

### Flow 5: Representative NIC and Account

DB:
- `assets.representative_nic_id`
- `assets.representative_account_id`
- `asset_hw_nics`
- `asset_sw_accounts`

Backend:
- `assets.py`
- `hardware.py`
- `software.py`
- `collect_parser.py`

Frontend:
- `AssetBasicInfoTab.vue`
- `AssetDetailPage.vue`

## 5. Current Practical Rule

When changing any important domain, trace it through all three layers:

1. database table or column
2. backend model/schema/route/service
3. frontend api/store/page or tab

If the change touches collection, also verify:

1. script definition
2. parser normalization
3. normalized storage
4. asset summary synchronization
5. list/detail rendering
