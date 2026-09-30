# Collaboration Instructions

This repository is the source of truth for Ghost Fleet. Its canonical remote is
`https://github.com/aaaditt/ghost-fleet.git`.

## Product direction guardrail

The project owner approved `docs/PRODUCT_BRIEF.md` on 2026-09-30. Work only
within that brief: a map-first tracker for commodity and energy traders, built
on real OpenSanctions and Global Fishing Watch data, for the hackathon
submission. Read `docs/CONCEPT_OVERVIEW.md` for background. Features outside
the brief need the owner's explicit request. Never present estimates, risk
scores, or heuristic classifiers as proof or as validated performance. Older
planning documents marked "historical" are not requirements.

## Start of a session

1. Run `git status --short --branch` and preserve work already in progress.
2. Run `git fetch origin` and inspect divergence before integrating remote work.
3. Read `README.md`, `docs/PRODUCT_BRIEF.md`, `docs/HANDOVER.md`, and the
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
