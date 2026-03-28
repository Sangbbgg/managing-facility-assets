# Versioning Rules

## Rule 1: Current state is v1

- The repository as it exists now is the official `v1` baseline.
- Do not describe already-implemented repository features as upcoming `v2` work.
- Do not rewrite `v1` documents when adding future concepts unless the baseline itself was incorrect.

## Rule 2: New standards become v2

Use `v2` when introducing any of the following after the baseline declaration:

- new architecture rules
- new domain concepts
- new workflow standards for Codex
- new cross-cutting naming conventions
- new major backend or frontend feature areas

## Rule 3: Preserve baseline and delta separately

When implementing a `v2` change:

1. Keep `references/v1-baseline.md` as the historical baseline.
2. Add or update a `v2` reference document describing the new rule or concept.
3. Update `SKILL.md` only enough to tell Codex that `v1` is baseline and `v2` holds future additions.
4. If the repository code changes, document whether the change:
   - extends `v1` behavior safely, or
   - establishes a new `v2` standard.

## Rule 4: Prefer additive versioning

- Prefer adding `v2` guidance over renaming existing structures.
- Only refactor `v1` structure when the user explicitly wants structural cleanup.
- If a `v2` rule supersedes `v1`, document the supersession explicitly instead of silently replacing the older rule.

## Rule 5: Codex workflow expectation

When a future Codex session starts work in this repository, it should:

1. Read `SKILL.md`
2. Read `references/v1-baseline.md`
3. Read this file
4. Read any `v2` reference files that exist for the task at hand
