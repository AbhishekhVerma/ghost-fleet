# Session Log

This file is append-only. The handover document contains the latest project
snapshot; this log records how the project reached that state.

## 2026-09-29 — Repository bootstrap (v0.1.0)

**Objective:** Make `aaaditt/ghost-fleet` the shared source of truth and prepare
the existing pipeline for repeatable collaborative sessions.

**Decisions:** Use `main` as the initial shared branch, semantic versions stored
in `VERSION`, an append-only session log, and a living handover. Keep API tokens,
downloaded maritime data, Python caches, and generated outputs outside Git.

**Changed:** Added the existing `dark_fleet_pipeline.py`, repository metadata,
dependency declarations, setup and usage documentation, collaboration rules,
the changelog, and this handover system.

**Validation:** Created an isolated Python 3.11.9 virtual environment, installed
`requirements.txt`, compiled `dark_fleet_pipeline.py`, ran focused assertions for
risk scoring and cargo value, and confirmed `pip check` reports no broken
requirements in the isolated environment. Scanned tracked files for GitHub token
patterns; no credentials were found. A live API run was not possible without the
operator-provided dataset and token.

**Remaining:** An end-to-end run still needs a local Global Fishing Watch token
and current OpenSanctions maritime export. See `docs/HANDOVER.md` for prioritized
follow-up work.
