# Ghost Fleet

Ghost Fleet is a proposed maritime intelligence platform for identifying ships
that may be hiding sanctioned or suspicious activity, explaining the evidence,
and estimating the operational and economic significance.

The current project version is **0.1.2**. The shared repository is
[`aaaditt/ghost-fleet`](https://github.com/aaaditt/ghost-fleet).

## Start here

- [Product brief](docs/PRODUCT_BRIEF.md): the approved direction. A map-first
  "Hidden Supply Monitor" for commodity and energy traders.
- [Concept overview](docs/CONCEPT_OVERVIEW.md): the full plain-language
  background on the problem, evidence, and limitations.

**Status:** hackathon build (trader-focused). Risk scores, cargo states, and
value figures are directional estimates, not proof of wrongdoing.

## What the pipeline does

1. Loads the OpenSanctions maritime export, merges rows by IMO, and keeps
   vessels on its **shadow-fleet list** (`mare.shadow`). Sanctioned vessels and
   vessels named by the most lists come first.
2. Resolves each IMO against Global Fishing Watch and records every AIS and
   registry identity (names, flags, MMSIs) it has used.
3. Pulls dated, positioned behaviour events for all of those identities: AIS
   gaps, loitering, port visits, and encounters.
4. Produces a transparent 0–100 risk score with a per-factor breakdown.
5. Estimates capacity and value **ranges** from tonnage or length, plus a
   monthly activity trend for the trader view.

Cargo state (loaded or ballast) needs a draft reading. The public GFW data has
none, so it is reported as `UNKNOWN` rather than guessed.

## Setup

Requirements: Python 3.10 or newer and a Global Fishing Watch API token.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GFW_API_TOKEN = "your-token"
```

Download the current export from the
[OpenSanctions maritime dataset](https://www.opensanctions.org/datasets/maritime/)
and save it as `maritime.csv` in the repository root.

## Run

```powershell
python dark_fleet_pipeline.py --max 120            # last 12 months by default
python dark_fleet_pipeline.py --offline            # rebuild from cached responses
python -m pytest -q                                # offline unit tests
```

Outputs:

- `dashboard/data/vessels.json` and `dashboard/data/signal.json` hold the
  dashboard snapshot. They are committed deliberately, so the hosted demo works
  without a token.
- `dark_fleet_risk_scores.csv` is a flat per-vessel table (git-ignored).
- `.cache/gfw/` holds raw API responses (git-ignored).

`dashboard/data/vessels.demo.json` contains **fictional** vessels, kept only
as an offline fallback.

## Data and licensing

- Global Fishing Watch API access has usage and licensing conditions. Confirm
  the terms before commercial use.
- OpenSanctions bulk data is offered under terms that may require a commercial
  license for business use.

## Collaboration

Repository working conventions live in [AGENTS.md](AGENTS.md). At the end of
each working session, update the version, append the [session log](docs/SESSION_LOG.md),
and refresh the [handover](docs/HANDOVER.md). User-visible changes also belong
in [CHANGELOG.md](CHANGELOG.md).
