# Design: 300-vessel snapshot, plan-gap fixes, licence and showcase README

- Date: 2026-09-30
- Status: design approved in chat; this spec is awaiting owner review
- Builds on: `docs/PRODUCT_BRIEF.md`, release v0.2.0

## Intent

**What the owner asked for:**
- Expand the snapshot to 300 vessels and redeploy.
- Check the dashboard against the approved plan. The map is the landing
  screen, and everything else sits in the sidebar. Fix any gaps.
- Add an open-source licence (MIT or Apache is fine).
- Push everything and make the README "super impressive": demo GIF,
  architecture diagram, stats and badges, and the hero-vessel story.

**Assumptions:**
- README readers are hackathon judges skimming GitHub for about 60 seconds.
  Success means they understand the product and open the live demo from the
  README's first screen.
- Every figure quoted anywhere comes from the 300-vessel snapshot.

**Non-goals:**
- No change to the page layout, the scoring model or the date window
  (30 Sep 2025 – 27 Sep 2026).
- No commercial data licences.

## Part 1 — Dashboard and data

The layout is kept: a full-height map, with a right-hand sidebar for the
monitor view and the dossiers.

1. **No-position tag.** List rows for vessels with no position show "No recent
   position" in their meta line. Opening such a vessel shows the dossier and
   leaves the map where it is. This behaviour already exists; the change only
   makes the tag visible.
2. **Cargo-state figure.** A fifth overview figure, "Cargo state known",
   shows `known of screened`, computed from `cargo_status !== "UNKNOWN"`. Its
   footnote reads: "Public tracking data has no draft readings, so no vessel's
   load is inferred."
3. **Global Fishing Watch link.** The dossier's sources line adds "View on
   Global Fishing Watch" →
   `https://globalfishingwatch.org/map/vessel/<gfw_vessel_id>`. The format was
   verified in a browser: it opens WOLF's profile. It is omitted when
   `gfw_vessel_id` is null.
4. **Snapshot size.** `EVENTS_PER_VESSEL` changes from 60 to 30. Aggregates are
   computed before trimming, so no figure changes. Target: `vessels.json` of
   1.8 MB or less.
5. **Snapshot.** Rebuild offline from cache: `--max 300 --start 2025-09-30
   --end 2026-09-27`. Commit `vessels.json` and `signal.json`.
6. **Tests.** Add `tests/test_snapshot.py`. It asserts that the committed
   snapshot is valid JSON with no NaN, that the vessel count matches
   `signal.vessels_screened`, that no vessel keeps more than
   `EVENTS_PER_VESSEL` events, that located vessels have numeric
   coordinates, and that `vessels.json` is 1.8 MB or less.

## Part 2 — One source for every figure

- Add `scripts/figures.py`, which prints every quoted figure from the committed
  snapshot. It is the draft from this session, with the full list of
  landlocked ISO3 codes.
- Update these from its output: `README.md`,
  `docs/submission/WRITEUP.md`, `DEMO_SCRIPT.md`, `PITCH.md`, deck slides
  `answer`, `product` and `fleet`, and `docs/HANDOVER.md`.
- Expected values (300-vessel run): trend −10.1% (595 vs 662); 276 located;
  234 scored 70+; 289 switched identity (124 of them 5+ times); 81 flags;
  11 landlocked flags (Malawi 4, Mali 3, Zimbabwe 3, Botswana 1); 115
  Russian-flagged; value $64–145 bn a year; EAST 1 unchanged (75, 7
  identities).
- Retake `docs/screenshot-overview.png` and `screenshot-dossier.png` on the
  live site after the redeploy.

## Part 3 — Licence

- Add `LICENSE` with MIT, `Copyright (c) 2026 aaaditt`.
- In the README, state that MIT covers the code only. Data remains under its
  sources' terms: OpenSanctions CC BY-NC 4.0 and Global Fishing Watch
  non-commercial.

## Part 4 — Demo GIF

- Record the live site with Playwright video at 1280×800. The scripted path:
  1. Land on the map (hold 2.5 s).
  2. Type `longevity` in the search box.
  3. Open **Wolf**, and let the map zoom to its activity.
  4. Scroll the identity list slowly.
  5. Return to the overview.
- Convert with ffmpeg (8.1.2, installed), using a two-pass palette
  (`palettegen`/`paletteuse`), 960px wide at 12 fps.
- Target: `docs/demo.gif`, 10–16 s long and 8 MB or less. If it is too
  large, lower to 10 fps or 880px.
- Keep the recording script as `scripts/record_demo.py` so the GIF can be
  regenerated.
- **Fallback:** if recording is unreliable, stitch 5 Playwright screenshots
  into a GIF with ffmpeg, one per scripted step, 2 s each.

## Part 5 — README

Order, top to bottom:

1. The title, a one-line pitch ("Hidden oil supply, seen from the sea"), and
   badges from shields.io as static images: live demo, version 0.2.0, tests
   (the passing count from the final `pytest` run), data sources, MIT
   licence.
2. The demo GIF, with links: **Try it live** and **Open WOLF's dossier**.
3. A headline figures table from Part 2.
4. **"One hull, seven identities"**: the EAST 1 → WOLF table (name, flag,
   years) and a deep link.
5. **Features**, one line each: chart-style map, trend headline, busiest
   ports, per-vessel dossier, search by former name, honest unknowns.
6. **How it works**: a Mermaid flowchart (OpenSanctions → merge by IMO →
   GFW identities and events → score/estimates/trend → snapshot JSON → static
   dashboard on Vercel), plus 3 short steps.
7. **What we show, and what we don't claim**: the limits table.
8. **Run it yourself**: setup, pipeline flags, tests, dashboard, deploy.
9. **Project docs and submission materials, data and licensing,
   acknowledgements.**

Keep the operational details (outputs, `vessels.demo.json`, `.vercelignore`)
under "Run it yourself". Remove the duplicated or older sections.

## Part 6 — Delivery and validation

- `python -m pytest -q`: all tests pass.
- Redeploy with `vercel deploy --prod --cwd dashboard`. Anonymous HTTP
  checks: `/` returns 200, `/data/signal.json` returns 200, and `.env.local`
  and `vessels.demo.json` return 404.
- Playwright on the live site at 1440×900 and 390×844: 0 console errors; the
  deep link opens WOLF; the new cargo figure, no-position tag and GFW link
  render.
- README: Mermaid and images render on GitHub (checked by viewing the pushed
  README).
- Run a secret scan. Bump the version to **0.3.0**, a feature release. Add a
  changelog entry, append the session log, rewrite the handover, commit,
  push.

## Risks

- **GIF size or flakiness:** the screenshot fallback, above.
- **Figure drift:** every figure comes from one script, and the demo script's
  spoken lines are updated with it.
- **Page weight:** the event trim, plus a size assertion in the tests.
