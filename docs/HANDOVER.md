# Project Handover

- Updated: 2026-09-29
- Version: 0.1.1
- Shared branch: `main`

## Current state

The repository contains:
1. A runnable Python pipeline in `dark_fleet_pipeline.py` (with 6 steps: OpenSanctions parsing, GFW identity resolution, STS encounter tracking, 0-100 explainable risk scoring, economic valuation, and ML-based draft/speed cargo load classification).
2. A live interactive Maritime Tracker dashboard in `dashboard/` with dark ocean basemaps, risk markers, SAR watch zones, STS encounter links, and hedge fund economic signal panels.
3. Complete dataset and ML research documentation in `docs/DATASETS_AND_ML_RESEARCH.md` evaluating open AIS corpora (NOAA MarineCadastre, Danish Maritime Authority), SAR radar data (DIU/GFW xView3-SAR), model feasibility, accuracy benchmarks, and sub-millisecond inference profiles.

## Immediate next work

1. **Train & Export ML Weights**: Extract a 20,000-voyage sample from open NOAA/DMA AIS data to train a Scikit-Learn `RandomForestClassifier` or `LightGBM` model and save to `models/cargo_load_model.joblib`.
2. **Move hard-coded parameters**: Parameterize date ranges, vessel limits, and Brent crude price via CLI flags or `.env`.
3. **API Reliability**: Add explicit retry behavior and response schema validation for GFW API queries.
4. **End-to-End Live Run**: Run against a full `maritime.csv` dataset once an operator token is provided.

## Run requirements

- Python 3.10+
- Packages in `requirements.txt`
- `GFW_API_TOKEN` environment variable (for live GFW API queries)
- OpenSanctions export at `maritime.csv` (optional for local demo; demo data pre-cached in `dashboard/data/vessels.json`)

To run the pipeline:
```powershell
python dark_fleet_pipeline.py
```

To run the dashboard:
```powershell
cd dashboard
python -m http.server 8080
```

## Known risks and decisions

- Heuristic draft classifier is currently active in `dark_fleet_pipeline.py`; upgrading to pre-trained weights will solidify the pitch's ML narrative.
- Encounter counts serve as a proxy for ship-to-ship transfers; true transfer volume requires verified cargo flow confirmation.
- Licensing: GFW and OpenSanctions bulk data are free for hackathon and non-commercial evaluation, but require commercial licensing for production SaaS deployment.
