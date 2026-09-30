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

## 2026-09-29 — Open Datasets & Machine Learning Research (v0.1.1)

**Objective:** Research open-source datasets, machine learning models, training requirements, empirical benchmarks, and inference latency/resource load for Ghost Fleet.

**Decisions:** Document a 3-tier model framework (Tier 1: Tabular Cargo Classifier, Tier 2: Evasion GNN, Tier 3: SAR Space Radar YOLOv8). Select NOAA MarineCadastre and Danish Maritime Authority (DMA) AIS as primary open training corpora for the cargo classifier, and DIU/GFW xView3-SAR for satellite radar detection.

**Changed:** Added `docs/DATASETS_AND_ML_RESEARCH.md`, updated `docs/PLANNING.md`, `README.md`, `VERSION`, and `CHANGELOG.md`.

**Validation:** Verified dataset download portals, confirmed licensing status (public domain / open data), and documented quantitative latency and hardware resource footprints for CPU/GPU serving.

**Remaining:** Implement a trained Scikit-Learn / LightGBM cargo classifier model weights file from a sample NOAA/DMA dataset slice for v0.2.0.

## 2026-09-29 — Concept clarification and implementation pause (v0.1.2)

**Objective:** Explain Ghost Fleet from first principles in one readable Markdown
document and prevent exploratory prototypes from determining the product before
the project owner provides direction.

**Decisions:** Set the project status to concept definition. Treat existing code,
dashboards, model descriptions, and performance claims as exploratory material.
Require explicit product-owner direction before further prototype or feature
development.

**Changed:** Added `docs/CONCEPT_OVERVIEW.md`; updated `README.md`, `AGENTS.md`,
`docs/HANDOVER.md`, `CHANGELOG.md`, and `VERSION`.

**Validation:** Reviewed the concept, planning, judge-review, dataset research,
handover, session, README, and changelog documents. Checked the new Markdown for
structure, internal consistency, unsupported certainty, and formatting errors.

**Remaining:** Review the concept overview with the project owner and capture the
selected primary user, first decision, scope, evidence standard, freshness need,
and immediate project objective in an approved product brief.

## 2026-09-30 — Trader-focused hackathon build (v0.2.0, in progress)

**Objective:** Turn Ghost Fleet into a submittable hackathon project today. The
submission needs a demo video, a live link, a write-up, a demo script, and a
pitch deck.

**Decisions:** The owner chose commodity/energy traders as the first user and a
map-first tracker as the first experience, using real GFW + OpenSanctions data.
The defaults are recorded in `docs/PRODUCT_BRIEF.md`: oil tankers only, a
directional-signal evidence standard, and a historical snapshot.

**Phase 0 (done):** Added `docs/PRODUCT_BRIEF.md`. Lifted the concept-definition
guardrail in `AGENTS.md` and `README.md`. Marked `docs/PLANNING.md`,
`docs/IDEA_MAP.md`, and `docs/JUDGE_REVIEW.md` as historical. Rewrote
`docs/HANDOVER.md` with a phase tracker.

**Validation:** Documentation only. Reviewed the diff and checked for secrets.
