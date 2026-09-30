# Project Handover

- Updated: 2026-09-30
- Version: 0.4.0
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
  Watch v3). There are 20 offline tests: pipeline, snapshot, dashboard
  consistency and video media.
- **Dashboard:** a map landing page with a sidebar (trend, figures including
  "Cargo state known", ports, list with no-position tags) and per-vessel
  dossiers with OpenSanctions and Global Fishing Watch links.
- **README:** a showcase with the demo GIF (`scripts/record_demo.py`
  regenerates it), the video poster, figures, the WOLF story and a Mermaid
  diagram.
- **Pitch video:** https://ghost-fleet.vercel.app/watch.html. It runs 3 min
  9 s, with the ElevenLabs voice "Eric" (American), subtitles and chapters.
  It is built by `video/make_voice.py` → `record_scenes.py` → `assemble.py`.
  The outputs are in `dashboard/media/`; intermediates are in `video/build/`
  (git-ignored).

| Deliverable | Status |
|---|---|
| Live link | Done |
| Repository (public, MIT) | Done |
| Write-up | Done: `docs/submission/WRITEUP.md` |
| Demo script | Done: `docs/submission/DEMO_SCRIPT.md` |
| Pitch deck | Done and shared by link (https://claude.ai/artifact/9SscVdcfFiNjFdTEaZLmeL). Team names still needed |
| Demo video | Done: https://ghost-fleet.vercel.app/watch.html (MP4 also downloadable) |

## Immediate next work

1. Owner: add `[Team names]` on the deck cover and submit. If the form
   needs YouTube or Loom, upload `dashboard/media/ghost-fleet-demo.mp4`.
2. Owner: **rotate the ElevenLabs API key.** It was pasted into the chat
   transcript. It is stored only as a Windows user environment variable and
   is in no file.
3. After the hackathon:
   - Screen all 892 listed vessels.
   - Validate the trend against published export estimates.
   - Add licensed draft data.
   - Pursue commercial data licences (OpenSanctions, a licensed AIS
     provider).

## Setup

- Python 3.10+, `python -m pip install -r requirements.txt`.
- For GIF and video regeneration: Playwright for Python with Chromium, and
  ffmpeg.
- For the voice: `ELEVENLABS_API_KEY` (free tier, 10,000 characters a
  month; the script uses about 2,600). The free tier needs ElevenLabs
  attribution, which is in the video's end card, the watch page and the
  README.
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
