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
| 1 | Real data: GFW + OpenSanctions pipeline, positions, monthly trend | Done (120 vessels, snapshot 2026-09-30) |
| 2 | Trader-focused dashboard polish | Done |
| 3 | Deploy live link | Done: https://ghost-fleet.vercel.app |
| 4 | Write-up, demo script, pitch deck, video shot list | Not started |
| 5 | Version 0.2.0, changelog, log, handover | Not started |

`dashboard/data/vessels.json` and `signal.json` hold a **real** snapshot
(120 shadow-fleet vessels). The redesigned dashboard reads it: a nautical-chart
map, the trader headline, a monthly trend, and per-vessel dossiers. The hero
demo vessel is `#imo=9240885` (EAST 1 → WOLF, 7 identities).

## Immediate next work

1. Phase 4: write-up, demo script, pitch deck, video shot list.

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
