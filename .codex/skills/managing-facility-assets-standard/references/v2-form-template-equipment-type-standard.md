# v2 Form Template Equipment Type Standard

This v2 standard defines how report form templates are assigned to equipment types.

## Scope

- `/reports/form-templates`
- `/reports/form-report`
- backend `report_form_templates` domain

## Rule

- A form template may target zero, one, or many equipment types.
- The assignment is stored as a template-to-equipment-type link set, not as a single column on the template row.
- Multiple equipment types such as `SERVER` and `PC` may intentionally share one template.

## Meaning of Empty Assignment

- When a template has no assigned equipment types, treat it as a global template.
- Global templates remain selectable for any asset equipment type.
- This preserves compatibility with older templates created before equipment-type assignment existed.

## Backend Expectations

- Keep template CRUD aligned across model, schema, and route serialization.
- Validate submitted equipment type ids against `equipment_types`.
- Form report preview and XLSX generation must reject templates that do not match the selected asset's equipment type.

## Frontend Expectations

- Template create/edit UI must support multi-select equipment types.
- Template list UI should show which equipment types a template applies to.
- Form report generation UI should only offer templates compatible with the selected asset, plus global templates.

## Practical Example

- If `SERVER` and `PC` use the same worksheet, register one template and assign both equipment types to that single template.
