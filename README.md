# Ghost Fleet

Ghost Fleet is a proposed maritime intelligence platform for identifying ships
that may be hiding sanctioned or suspicious activity, explaining the evidence,
and estimating the operational and economic significance.

The current project version is **0.1.2**. The shared repository is
[`aaaditt/ghost-fleet`](https://github.com/aaaditt/ghost-fleet).

## Start here

Read [Ghost Fleet: Concept Overview](docs/CONCEPT_OVERVIEW.md) for the complete
plain-language explanation of the idea, problem, potential users, benefits,
limitations, and product decisions that must be made before further development.

The project is currently in **concept definition**. Existing technical artifacts
are exploratory; they do not define the final product. Further prototype work is
paused until the project owner selects the target user and product direction.

## What the pipeline does

1. Loads vessels with IMO numbers from an OpenSanctions maritime CSV export.
2. Resolves each IMO against the Global Fishing Watch vessel API.
3. Counts identity changes and ship-to-ship encounter events.
4. Produces a transparent risk score from 0 to 100.
5. Estimates cargo value and an aggregate sanctioned oil flow signal.

The output is intended for a hackathon demonstration. The economic values are
estimates based on configured vessel capacities, encounter counts, and a static
Brent price. They are not trading advice or independently verified cargo flows.

## Setup

Requirements: Python 3.10 or newer, a Global Fishing Watch API token, and a
current OpenSanctions maritime CSV export.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:GFW_API_TOKEN = "your-token"
```

Download the current maritime export from the
[OpenSanctions maritime dataset](https://www.opensanctions.org/datasets/maritime/)
and save it as `maritime.csv` in the repository root. The dataset, token, and
generated outputs are ignored by Git.

## Run

```powershell
python dark_fleet_pipeline.py
```

The pipeline writes:

- `dark_fleet_risk_scores.csv` with per-vessel scores and estimates.
- `sanctioned_oil_flow_signal.json` with the aggregate market signal.

Before a demo, review the date range and `BRENT_CRUDE_USD_PER_BARREL` in
`dark_fleet_pipeline.py`. The current pipeline limits API work to 50 vessels.

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
