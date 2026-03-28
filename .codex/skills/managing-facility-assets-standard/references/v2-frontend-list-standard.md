# v2 Frontend List Standard

This file records the first post-baseline frontend standard update.

## Rule

Every frontend UI area that renders list-shaped data must show:

- a visible section header or title
- the total number of items currently shown
- full visible values without `...` truncation for user-facing list data unless the user explicitly requests compact mode

## Applies To

- `n-data-table`
- `DataTable.vue`
- `n-list`
- `v-for` based repeated blocks that function as a list

## Implementation Guidance

- Prefer `frontend/src/components/common/ListHeader.vue` for the title and count display.
- When using `DataTable.vue`, pass a specific `title` prop instead of relying on the generic default.
- If the list is filtered, show the count of the currently displayed items.
- If a page contains multiple list sections, each section should display its own count.
- Prefer wrapping long text over truncating it with ellipsis.

## Intent

- Make list-based UIs scan faster.
- Remove ambiguity about whether the user is seeing partial or full results.
- Keep the rule visible in code so future Codex sessions apply it consistently.
