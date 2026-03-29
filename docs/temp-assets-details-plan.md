# Temp Plan: `/assets/details` Re-definition

This is a temporary implementation planning document.

Do not promote this into the Codex skill yet.
Move validated parts into the skill only after the feature is implemented and confirmed in the repository.

## Goal

Redefine `/assets/details` from a single-record manual entry page into an asset-specific review and exception-handling workspace.

The page should support:

- selecting one asset and reviewing its current state
- verifying auto-collected and already-registered data
- editing only the fields that require human correction or supplemental input
- showing different detail sections depending on asset type

## Product Direction

### Current problem

- Entering all detailed data one asset at a time does not scale for large asset inventories.
- Different asset types require different detail fields.
- A single fixed detail form pushes too much manual effort onto users.

### Recommended direction

- Keep `/assets/register` responsible for initial registration and bulk entry.
- Make `/assets/details` responsible for review, exception correction, and type-specific detail management.
- Prefer automatic collection wherever possible.
- Use manual entry only for fields that cannot be collected or require human judgment.

## Role Split

### `/assets/register`

- create assets
- bulk upload from spreadsheets
- set shared/common fields
- assign asset type

### `/assets/details`

- select an existing asset
- inspect common asset information
- inspect collected hardware/software data
- supplement missing type-specific fields
- manage notes and operational history
- review change logs

## Target UX

### Left panel

- searchable asset list
- current selection context
- basic filters if needed later

### Right panel

- asset identity header
  - asset code
  - asset name
  - current status
  - asset type
  - location/group summary
- tabbed workspace

## Proposed Tab Structure

### 1. Common Information

Purpose:

- show and edit shared fields used by all asset types

Example fields:

- asset code
- asset name
- group
- location
- equipment type
- status
- importance
- manager
- supervisor
- install date
- purpose
- notes summary

### 2. Type-Specific Details

Purpose:

- show fields that depend on the asset type

Design rule:

- render different sub-sections depending on `equipment_type`
- avoid showing irrelevant fields for other asset types

Examples:

- Server
  - service role
  - virtualization usage
  - storage characteristics
  - backup/redundancy notes
- PC
  - assigned user
  - department usage
  - office/security compliance notes
- Network device
  - management IP
  - firmware
  - port/capacity notes
  - topology-related notes
- Controller / security / specialized devices
  - device-specific operational fields

### 3. Collected Data

Purpose:

- display imported or auto-collected hardware/software data
- keep this data mostly read-oriented with limited corrective workflows

Candidate sections:

- hardware
- software
- collection metadata
- last collected timestamp
- collection source/status

### 4. Notes / Supplemental Fields

Purpose:

- store operational notes and small user-defined values not covered by formal schema

Candidate sections:

- user memo entries
- custom key/value fields
- optional attachments later

### 5. Change History

Purpose:

- provide an audit trail of meaningful edits

Candidate sections:

- changed field
- old value
- new value
- changed by
- changed at
- reason

## Data Strategy

### Principle 1: common vs type-specific split

- common fields should remain stable and minimal
- type-specific fields should be isolated so schema growth is controlled

### Principle 2: auto-collected vs manually maintained split

- collected fields should not be treated the same as manual master data
- users should correct exceptions, not rewrite entire collected records

### Principle 3: scalable input model

- bulk and template-driven workflows should handle initial volume
- detail page should handle review and cleanup

## Recommended Implementation Phases

### Phase A: functional re-definition without large schema change

Goal:

- keep current route and most current structure
- reposition the page around review and exception handling

Tasks:

- revise page copy and structure to emphasize review, not full manual entry
- group existing tabs into clearer conceptual categories
- add stronger asset summary/header context
- identify which existing fields are common vs collected vs supplemental

Expected result:

- `/assets/details` becomes easier to understand without a large migration

### Phase B: type-specific detail model

Goal:

- introduce asset-type-aware detail sections

Tasks:

- define supported asset-type categories
- define which fields belong to each type
- design backend schema strategy
  - separate per-type tables, or
  - one flexible detail payload, or
  - hybrid approach
- render tabs/sections conditionally by asset type

Expected result:

- users see only relevant detailed fields

### Phase C: manual input reduction

Goal:

- reduce repetitive detail entry

Tasks:

- identify fields that can be derived or auto-collected
- identify fields that can be bulk-updated by asset type/group/location
- move high-volume repeated editing out of `/assets/details`

Expected result:

- `/assets/details` is reserved for exceptions and verification

### Phase D: auditability and operations fit

Goal:

- make the page reliable for real operational use

Tasks:

- tighten change history coverage
- require reason fields for important edits if needed
- make collected/manual boundaries visible in UI

Expected result:

- users can trust the page as an operational workspace

## Open Design Questions

These need to be answered before final implementation design:

1. What are the official asset-type categories that must be supported?
2. Which type-specific fields are mandatory per category?
3. Should type-specific fields live in separate tables or a flexible schema?
4. Which fields are authoritative from collection vs manual input?
5. Which bulk-edit workflows should exist outside `/assets/details`?

## Implementation Recommendation

Start with Phase A first.

Reason:

- it improves usability immediately
- it does not require a full schema redesign
- it creates a clean base for Phase B type-specific modeling

After Phase A is stable, implement Phase B with a deliberate schema choice.

## Promotion Rule

Only promote this plan into the Codex skill after:

- the direction is accepted
- code implementation is merged
- the repository structure reflects the new operating model
