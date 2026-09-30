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

**Phase 1a (code done, waiting for token):** Rewrote `dark_fleet_pipeline.py`
against the real GFW v3 schema, verified against the official
`gfw-api-python-client` 1.4.0 models, and the real OpenSanctions export
(2026-09-29, 23,453 rows).
- Found: GFW vessel records carry no draft, speed, or vessel type. Public
  encounter types cover fishing, carrier, support, and bunker vessels only, so
  tanker-to-tanker transfers are unlikely to appear.
- Found: the OpenSanctions export has one row per source entity, with an
  `IMO` prefix. Rows are now merged by IMO and filtered on the `mare.shadow`
  tag (892 vessels, 772 sanctioned).
- Changed: evidence now comes from AIS gaps, loitering, port visits, encounters,
  and identity history across all AIS identities. Capacity and value are
  ranges from tonnage or length. Cargo state is `UNKNOWN` without draft. This
  fixes a bug where zero evidence reported 50% confidence. Added a monthly
  trend and provenance, a response cache, CLI flags, and `tests/test_pipeline.py`
  (7 offline tests). The fictional data is saved as `vessels.demo.json`.
- Validation: `python -m pytest -q` passed 7/7, and the loader ran on the real
  CSV. There has been no live GFW call yet because the token is still pending.

**Phase 1b (real data run, done):** The owner set the GFW token. It was
validated with one call (HTTP 200). A 3-vessel smoke test exposed two
pipeline bugs, both fixed and covered by tests:
- GFW splits one ship's history across several search entries. Only the
  first entry was used, which dropped most identities and events. All entries
  carrying the IMO are now merged (for example, EAST 1 → 7 identities: TORM
  GERTRUD/DNK…EAST 1/HKG → LONGEVITY 7/PLW → WOLF/MWI → WOLF/ABW).
- Identity changes double-counted (flag + MMSI per re-flag, and spacing
  variants of a name). They now count chronological AIS identity switches with
  normalised names.
- Verified: GFW gap and encounter endpoints return HTTP 200 with total=0 for
  these tankers over 2023–2026. That is a coverage limit, not an error, so
  evidence rests on loitering, port visits, and identity history.
- Rescaled "meetings" (loitering) points to 1 per 4 events. The old scale
  saturated for nearly every vessel. The partial first month is now dropped
  from the trend.
- Snapshot (window 2025-09-30 → 2026-09-27, 120 most-listed shadow-fleet
  vessels): 120/120 matched, 112 located, 92 scored ≥70, 0 API errors.
  3-month active-vessel trend: −13.1% (Jun–Aug vs Mar–May, hand-checked).
- Validation: `python -m pytest -q` passed 8/8. Full live run, then an offline
  rebuild from cache.

**Phase 2 (dashboard, done):** Rebuilt `dashboard/` on the real snapshot with a
nautical-chart design (Esri Ocean basemap, chart magenta for risk 70+,
Newsreader/Public Sans). The monitor view shows the trend headline, 12-month
bars, key figures, busiest ports, and a searchable list (matching former names
too). The dossier view shows the score breakdown, the AIS identity sequence,
the last 12 dated events plotted on the map, and size and value ranges. It
honestly marks cargo state as unknown. The page has a disclaimer and source
credits, SRI on Leaflet, escaped data strings, and a `#imo=` deep link.
Bugs found in browser testing and fixed:
- Aggregates (trend, ports) were computed after trimming events to 60 per
  vessel, which undercounted early months. They are now computed from all
  events. The corrected headline is **−15.3%** (Jun–Aug 232 vs Mar–May 274,
  hand-checked).
- Missing CSV cells wrote `NaN`, which is invalid JSON and broke the page load.
  They now become `null`, and the writer uses `allow_nan=False`.
- Port names were dropped because the raw API key is `port_visit`, not the
  client model's `portVisit` alias. All 1,335 displayed calls are now named.
- Removed the straight lines between event points, which implied routes across
  land. Fixed money formatting for single vessels.
Validation: `python -m pytest -q` passed 9/9. Playwright at 1440×900 and
390×844: no console errors, no horizontal scroll. Deep link, search (including
a former name), empty state, open and back all work.
