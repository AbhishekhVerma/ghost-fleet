# Project Handover

- Updated: 2026-09-30
- Version: 0.3.0
- Shared branch: `main`
- Licence: MIT (code). Data stays under OpenSanctions CC BY-NC 4.0 and Global
  Fishing Watch non-commercial terms.

## Current state

Ghost Fleet is a **map-first "hidden supply monitor" for commodity and energy
traders** (see `docs/PRODUCT_BRIEF.md`). It is built for a hackathon
submission due 2026-09-30.

- **Live:** https://ghost-fleet.vercel.app. The demo vessel is
  `#imo=9240885` (EAST 1 → WOLF, 7 identities, score 75).
- **Data:** a real snapshot of the 300 most-listed shadow-fleet vessels,
  30 Sep 2025 – 27 Sep 2026.
  - 276 located; 234 scored 70+.
  - Headline: active vessels −10.1% (595 vs 662, Jun–Aug vs Mar–May).
  - 289 switched identity; 81 flags; 11 flagged to landlocked countries;
    115 Russian-flagged.
  - `python scripts/figures.py` prints every quoted figure.
- **Pipeline:** `dark_fleet_pipeline.py` (OpenSanctions + Global Fishing
  Watch v3), 16 offline tests.
- **Dashboard:** a map landing page with a sidebar (trend, figures including
  "Cargo state known", ports, list with no-position tags) and per-vessel
  dossiers with OpenSanctions and Global Fishing Watch links.
- **README:** a showcase with the demo GIF (`scripts/record_demo.py`
  regenerates it), figures, the WOLF story and a Mermaid diagram.

| Deliverable | Status |
|---|---|
| Live link | Done |
| Repository (public, MIT) | Done |
| Write-up | Done: `docs/submission/WRITEUP.md` |
| Demo script | Done: `docs/submission/DEMO_SCRIPT.md` |
| Pitch deck | Done and shared by link (https://claude.ai/artifact/9SscVdcfFiNjFdTEaZLmeL). Team names still needed |
| Demo video | **Owner to record**, following the script |

## Immediate next work

1. Owner: add `[Team names]` on the deck cover, record the demo video, and
   submit.
2. After the hackathon:
   - Screen all 892 listed vessels.
   - Validate the trend against published export estimates.
   - Add licensed draft data.
   - Pursue commercial data licences (OpenSanctions, a licensed AIS
     provider).

## Setup

- Python 3.10+, `python -m pip install -r requirements.txt`.
- For GIF regeneration: Playwright for Python with Chromium, and ffmpeg.
- `GFW_API_TOKEN` in the environment. The owner's is set as a Windows user
  variable.
- `maritime.csv` in the repo root, from the OpenSanctions maritime dataset.
- Rebuild offline from the cache with
  `python dark_fleet_pipeline.py --max 300 --offline --start 2025-09-30 --end 2026-09-27`.
- Deploy with `vercel deploy --prod --cwd dashboard`. The project is linked in
  `dashboard/.vercel` (git-ignored).

## Known risks

- Global Fishing Watch has almost no tanker encounter or AIS-gap events, and
  no draft data. The evidence rests on identity history, loitering and port
  calls, and cargo state is always unknown.
- The trend counts active listed vessels, not barrels. Value figures are a
  capacity upper bound.
- The data covers 300 of 892 listed vessels. The ranking prefers the
  most-listed ships.
- A listing or score is not proof of wrongdoing. Keep that wording in any
  pitch.
- `dashboard/.env.local` holds a Vercel OIDC token. It is git-ignored and
  excluded from deploys by `.vercelignore`.
