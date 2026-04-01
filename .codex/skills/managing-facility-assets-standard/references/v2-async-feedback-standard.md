# v2 Async Feedback Standard

This v2 frontend standard defines how Codex should handle user-triggered actions that take noticeable time.

## Scope

- Frontend actions started by a click, submit, preview, upload, download, save, generate, or similar command
- Pages, modals, tables, and repeated list items that can trigger async work

## Rule

- Show immediate visible feedback when an async action starts.
- Prevent accidental duplicate triggering while the action is in progress.
- Keep the feedback attached to the control or area the user interacted with whenever possible.

## Expected UX

- Buttons that start async work should switch to a loading state or be disabled immediately.
- If the result opens in a modal or side panel, open that container promptly and show a loading state there instead of waiting silently.
- Avoid leaving the user in a state where repeated clicks feel necessary.

## Implementation Guidance

- Prefer per-row or per-item loading state for actions started from tables or lists.
- If stale output would be misleading, clear the old result before starting the new request.
- Use page-level loading only when a more local loading state is not practical.

## Example

- If a report preview is started from a row button, put that button into loading immediately, block duplicate clicks, open the preview modal, and show a spinner until the workbook is ready.
