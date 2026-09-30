# Project Handover

- Updated: 2026-09-30
- Version: 0.1.2 (0.2.0 in progress)
- Shared branch: `main`

## Current state

The project owner approved `docs/PRODUCT_BRIEF.md`. Ghost Fleet is now a
**map-first "Hidden Supply Monitor" for commodity and energy traders**, built
for a hackathon submission due 2026-09-30. The concept-definition pause is
lifted, but only for work inside the brief.

The work follows the plan phases:

| Phase | Scope | Status |
|---|---|---|
| 0 | Record decisions, lift guardrail, mark old docs historical | Done |
| 1 | Real data: GFW + OpenSanctions pipeline, positions, monthly trend | Waiting for GFW token and `maritime.csv` |
| 2 | Trader-focused dashboard polish | Not started |
| 3 | Deploy live link | Not started |
| 4 | Write-up, demo script, pitch deck, video shot list | Not started |
| 5 | Version 0.2.0, changelog, log, handover | Not started |

`dashboard/data/vessels.json` still holds **fictional** demo vessels, and the
dashboard still places them at random positions.

## Immediate next work

1. Owner: create a Global Fishing Watch API token and download the OpenSanctions
   maritime CSV as `maritime.csv`.
2. Extend `dark_fleet_pipeline.py` with a tanker filter, encounter positions and
   dates, a monthly series, the UNKNOWN cargo path, and provenance.
3. Generate the real snapshot and move the fictional data to `vessels.demo.json`.

## Setup

See `README.md`. You need Python 3.10+, `GFW_API_TOKEN` in the environment, and
`maritime.csv` in the repo root. Both are git-ignored.

## Known risks

- GFW token approval delays or rate limits. The fallback is the labelled
  fictional demo data.
- OpenSanctions and GFW terms are non-commercial. Credit both.
- GFW identity data rarely includes draft, so many cargo states will honestly be
  UNKNOWN.
- Value figures depend on assumed capacity and a static Brent price. Always
  show them as ranges.
- Encounters, identity changes, and risk scores do not prove wrongdoing.
