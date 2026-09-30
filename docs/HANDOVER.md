# Project Handover

- Updated: 2026-09-30
- Version: 0.2.0
- Shared branch: `main`

## Current state

Ghost Fleet is a **map-first "hidden supply monitor" for commodity and energy
traders** (see `docs/PRODUCT_BRIEF.md`). It is built for a hackathon
submission due 2026-09-30.

- **Live:** https://ghost-fleet.vercel.app. The demo vessel is
  `#imo=9240885` (EAST 1 → WOLF, 7 identities).
- **Data:** a real snapshot of 120 of the most-listed shadow-fleet vessels,
  30 Sep 2025 – 27 Sep 2026. Headline: active vessels −15.3% (Jun–Aug vs
  Mar–May).
- **Pipeline:** `dark_fleet_pipeline.py` (OpenSanctions + Global Fishing
  Watch v3) with 9 offline tests.
- **Submission materials:** `docs/submission/` (write-up, demo script,
  pitch outline). The slide deck is a private claude.ai artifact linked in
  `PITCH.md`.

| Deliverable | Status |
|---|---|
| Live link | Done |
| Repository (public) | Done |
| Write-up | Done: `docs/submission/WRITEUP.md` |
| Demo script | Done: `docs/submission/DEMO_SCRIPT.md` |
| Pitch deck | Done. The owner must add team names and share it |
| Demo video | **Owner to record**, following the script |

## Immediate next work

1. Owner: fill in `[Team names]` on the deck cover, share or export the deck,
   record the demo video, and submit.
2. Optional before judging: widen the snapshot beyond 120 vessels
   (`--max 300`) if time allows. The response cache makes reruns cheap, but
   new vessels cost roughly 5 API calls each.
3. After the hackathon: validate the trend against published export
   estimates, and add licensed draft data.

## Setup

- Python 3.10+, `python -m pip install -r requirements.txt`.
- `GFW_API_TOKEN` in the environment. The owner's is set as a Windows user
  variable.
- `maritime.csv` in the repo root, from the OpenSanctions maritime dataset.
- Rebuild offline from the cache with
  `python dark_fleet_pipeline.py --offline --start 2025-09-30 --end 2026-09-27`.
- Deploy with `vercel deploy --prod --cwd dashboard`. The project is linked in
  `dashboard/.vercel` (git-ignored).

## Known risks

- Global Fishing Watch has almost no tanker encounter or AIS-gap events, and
  no draft data. The evidence rests on identity history, loitering and port
  calls, and cargo state is always unknown.
- The trend counts active listed vessels, not barrels. Value figures are a
  capacity upper bound.
- The data covers 120 of 892 listed vessels. The ranking prefers the
  most-listed ships.
- OpenSanctions and Global Fishing Watch are non-commercial licences, and
  both are credited on the page.
- A listing or score is not proof of wrongdoing. Keep that wording in any
  pitch.
- `dashboard/.env.local` holds a Vercel OIDC token. It is git-ignored and
  excluded from deploys by `.vercelignore`.
