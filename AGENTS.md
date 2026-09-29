# Collaboration Instructions

This repository is the source of truth for Ghost Fleet. Its canonical remote is
`https://github.com/aaaditt/ghost-fleet.git`.

## Product direction guardrail

The project is in concept definition. Read `docs/CONCEPT_OVERVIEW.md` before
planning any product work. Do not create or extend a prototype, dashboard,
pipeline, model, or product feature unless the project owner explicitly requests
that implementation. Existing technical artifacts and performance claims are
exploratory and are not validated product requirements. Prioritize the owner's
decisions and documentation over inferred implementation work.

## Start of a session

1. Run `git status --short --branch` and preserve work already in progress.
2. Run `git fetch origin` and inspect divergence before integrating remote work.
3. Read `README.md`, `docs/CONCEPT_OVERVIEW.md`, `docs/HANDOVER.md`, and the
   latest entry in `docs/SESSION_LOG.md` before changing the project.
4. Read `VERSION` and use it as the current project version.

## End of a session

1. Complete and validate the requested work. Do not commit secrets, downloaded
   datasets, generated output, or local environment files.
2. Increment `VERSION` once per implementation session. Use semantic versioning:
   patch for fixes and internal/docs work, minor for backward-compatible
   features, and major for incompatible changes.
3. Keep the version shown in `README.md` synchronized with `VERSION`.
4. Add user-visible or operational changes under the new version in
   `CHANGELOG.md`.
5. Append a dated entry to `docs/SESSION_LOG.md` with the objective, decisions,
   changed files, validation, and remaining work.
6. Rewrite `docs/HANDOVER.md` so it describes the current state, immediate next
   tasks, setup requirements, and known risks. It is a living snapshot, not an
   append-only history.
7. Commit coherent work with a descriptive message and push the current branch
   to `origin`. Never rewrite shared history.

If a session only inspects or discusses the project and makes no repository
changes, do not create an empty commit or version bump.

## Engineering conventions

- Keep credentials in environment variables.
- Prefer small, reviewable commits.
- Update setup and usage instructions when commands, inputs, or outputs change.
- Record the exact validation performed; do not claim checks that were not run.
- Preserve unrelated local changes and call out incomplete work in the handover.
