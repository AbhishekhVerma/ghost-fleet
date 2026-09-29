# Project Handover

- Updated: 2026-09-29
- Version: 0.1.0
- Shared branch: `main`

## Current state

The repository contains a runnable Python MVP in `dark_fleet_pipeline.py`. It
loads a local OpenSanctions maritime export, queries Global Fishing Watch for
identity and encounter information, calculates vessel risk, estimates cargo
economics, and writes CSV and JSON outputs.

The module compiles with Python 3.11.9. Its declared dependencies install cleanly
in an isolated virtual environment, and focused risk-score and cargo-value checks
pass. A live end-to-end run has not been made because the required OpenSanctions
CSV and Global Fishing Watch token are local operator inputs.

## Immediate next work

1. Add a small anonymized fixture and focused tests for scoring and aggregation.
2. Move hard-coded dates, vessel limits, and Brent price into command-line or
   environment configuration.
3. Add explicit API error reporting, retry behavior, and response validation.
4. Run a licensed demo dataset end to end and validate output assumptions.
5. Replace static capacity heuristics where trustworthy tonnage data is present.

## Run requirements

- Python 3.10+
- Packages in `requirements.txt`
- `GFW_API_TOKEN` in the environment
- A current OpenSanctions export at `maritime.csv`

Run `python dark_fleet_pipeline.py` from the repository root. Generated output
and the source dataset are intentionally excluded from version control.

## Known risks and decisions

- The Brent price and event date range are hard-coded and become stale.
- Missing GFW matches still receive a sanctions-only score and heuristic cargo
  estimate.
- API failures currently collapse to missing matches or zero encounters, which
  can hide data quality problems.
- Encounter counts are only a proxy for transfers. Economic values are demo
  estimates and require validation before any operational use.
- Global Fishing Watch and OpenSanctions licensing must be reviewed before
  commercial use.
