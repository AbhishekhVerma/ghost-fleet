"""
Dark Fleet Risk Score — Hackathon MVP Pipeline
================================================
Combines real, free data sources into a per-vessel risk score and
estimates the economic value of sanctioned oil flows — a signal
relevant to hedge funds, commodity desks, and energy traders.

  1. OpenSanctions maritime.csv   -> known sanctioned / watchlisted hulls (ground truth)
  2. Global Fishing Watch (GFW)   -> identity history (flag/name-hopping), encounters
                                      (ship-to-ship transfers), and AIS-unmatched SAR
                                      detections (physically-present, transponder-off vessels)
  3. Economic Intelligence Layer  -> per-vessel cargo value estimates, aggregate sanctioned
                                      oil flow index, and market-moving signal generation

BEFORE RUNNING:
  1. pip install requests pandas --break-system-packages
  2. Get a free GFW API token: https://globalfishingwatch.org/our-apis/tokens
  3. Set it below or as an env var: export GFW_API_TOKEN="..."
  4. Grab the current OpenSanctions maritime.csv link from
     https://www.opensanctions.org/datasets/maritime/  (the dated path changes daily)
     and download it locally, or point MARITIME_CSV_URL at it.

NOTE ON LICENSING (be upfront about this in your pitch):
  - GFW APIs: non-commercial use only. Fine for a hackathon demo; a commercial
    launch needs a licensed AIS provider (Spire, Kpler, etc.) or a GFW commercial deal.
  - OpenSanctions bulk data: free for non-commercial use (CC BY-NC 4.0); businesses
    need a paid data license.
"""

import os
import time
import datetime
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
GFW_TOKEN = os.environ.get("GFW_API_TOKEN", "PASTE_YOUR_TOKEN_HERE")
GFW_BASE = "https://gateway.api.globalfishingwatch.org/v3"
HEADERS = {"Authorization": f"Bearer {GFW_TOKEN}"}

# Point this at a local copy of the OpenSanctions maritime.csv you downloaded
MARITIME_CSV_PATH = "maritime.csv"

# Brent crude benchmark price (USD/barrel) — update for demo day.
# Used to estimate the dollar value of sanctioned oil each dark vessel carries.
BRENT_CRUDE_USD_PER_BARREL = 78.50

# Limit how many vessels you actually hit the API for during a hackathon demo —
# pick a narratively relevant slice (e.g. Ukraine war-sanctions dataset) rather
# than all 20k+ rows.
MAX_VESSELS = 50


# ---------------------------------------------------------------------------
# Step 1: Load ground-truth sanctioned/watchlisted vessels
# ---------------------------------------------------------------------------
def load_sanctioned_vessels(csv_path: str, max_rows: int = MAX_VESSELS) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    vessels = df[(df["type"] == "VESSEL") & df["imo"].notna()].copy()
    # Prioritize the Ukraine war-sanctions dataset if present — most narratively
    # relevant slice for a "dark fleet" hackathon pitch.
    if "datasets" in vessels.columns:
        priority = vessels[vessels["datasets"].str.contains("ua_war_sanctions", na=False)]
        vessels = pd.concat([priority, vessels]).drop_duplicates(subset="imo")
    return vessels.head(max_rows)


# ---------------------------------------------------------------------------
# Step 2: Resolve each IMO to a GFW vessel identity record
# ---------------------------------------------------------------------------
def gfw_search_vessel(imo: str) -> dict | None:
    url = f"{GFW_BASE}/vessels/search"
    params = {"query": imo, "datasets[0]": "public-global-vessel-identity:latest"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    if r.status_code != 200:
        return None
    entries = r.json().get("entries", [])
    return entries[0] if entries else None


def count_identity_changes(vessel_record: dict) -> int:
    """Flag-hopping / renaming is a documented shadow-fleet evasion pattern."""
    registry_info = vessel_record.get("registryInfo", [])
    names = {r.get("shipname") for r in registry_info if r.get("shipname")}
    flags = {r.get("flag") for r in registry_info if r.get("flag")}
    return max(len(names) - 1, 0) + max(len(flags) - 1, 0)


# ---------------------------------------------------------------------------
# Step 3: Pull ship-to-ship encounter events for that vessel
# ---------------------------------------------------------------------------
def count_encounters(gfw_vessel_id: str, start_date: str, end_date: str) -> int:
    url = f"{GFW_BASE}/events"
    params = {
        "vessels[0]": gfw_vessel_id,
        "datasets[0]": "public-global-encounters-events:latest",
        "start-date": start_date,
        "end-date": end_date,
        "limit": 1,
        "offset": 0,
    }
    r = requests.get(url, headers=HEADERS, params=params, timeout=20)
    if r.status_code != 200:
        return 0
    return r.json().get("total", 0)


# ---------------------------------------------------------------------------
# Step 4: Composite risk score
# ---------------------------------------------------------------------------
def compute_risk_score(sanctions_hit: bool, identity_changes: int, encounters: int) -> int:
    """
    Simple, explainable scoring — good for a hackathon demo where judges will
    ask "how did you weight this." Tune freely; the point is transparency,
    not a black box.
    """
    score = 0
    score += 40 if sanctions_hit else 0
    score += min(identity_changes * 10, 30)   # cap contribution at 30
    score += min(encounters * 5, 30)          # cap contribution at 30
    return min(score, 100)


# ---------------------------------------------------------------------------
# Step 5: Economic / Monetary Intelligence (Hedge Fund Signal)
# ---------------------------------------------------------------------------
# Why this matters commercially:
#   Hedge funds pay $50K–$500K/year for "alternative data" feeds.
#   If you can estimate how many barrels the dark fleet is moving RIGHT NOW,
#   that's a leading indicator for:
#     • Oil supply hitting the market (price pressure downward)
#     • Sanctions enforcement tightening (supply squeeze → price up)
#     • Geopolitical risk escalation
#   Bloomberg, Kpler, and Vortexa sell exactly this kind of signal.
# ---------------------------------------------------------------------------

# Typical cargo capacity by vessel type (deadweight tonnage → barrels).
# 1 metric ton of crude ≈ 7.33 barrels.  These are conservative midpoints.
VESSEL_TYPE_CAPACITY = {
    "oil_or_chemical_tanker": 500_000,   # ~70K DWT Aframax
    "tanker":                700_000,    # ~95K DWT Suezmax
    "crude_oil_tanker":      1_400_000,  # ~200K DWT VLCC
    "oil_tanker":            700_000,
    "chemical_tanker":       200_000,
    "lng_tanker":            500_000,
    "product_tanker":        350_000,
    "unknown":               500_000,    # conservative default
}


def estimate_cargo_barrels(vessel_record: dict) -> int:
    """
    Estimate how many barrels of crude a vessel can carry in one voyage,
    using GFW vessel-type metadata.  Falls back to a conservative default.
    """
    vessel_type = "unknown"
    registry_info = vessel_record.get("registryInfo", [])
    for entry in registry_info:
        vt = (entry.get("vesselType") or "").lower().replace(" ", "_")
        if vt in VESSEL_TYPE_CAPACITY:
            vessel_type = vt
            break
    # Also check selfReportedInfo
    if vessel_type == "unknown":
        for entry in vessel_record.get("selfReportedInfo", []):
            vt = (entry.get("vesselType") or "").lower().replace(" ", "_")
            if vt in VESSEL_TYPE_CAPACITY:
                vessel_type = vt
                break
    return VESSEL_TYPE_CAPACITY.get(vessel_type, 500_000)


def estimate_cargo_value_usd(barrels: int, price_per_barrel: float = BRENT_CRUDE_USD_PER_BARREL) -> float:
    """Dollar value of a single full cargo at current Brent crude price."""
    return barrels * price_per_barrel


def estimate_annual_flow_usd(
    barrels_per_voyage: int,
    encounters_per_year: int,
    price_per_barrel: float = BRENT_CRUDE_USD_PER_BARREL,
) -> float:
    """
    Rough annual sanctioned-oil revenue estimate for one vessel.
    Each ship-to-ship encounter is treated as one cargo transfer.
    A vessel with zero detected encounters gets a baseline of 4 voyages/year
    (industry average for a tanker on a long-haul route).
    """
    transfers = max(encounters_per_year, 4)
    return barrels_per_voyage * transfers * price_per_barrel


def generate_market_signal(results_df: pd.DataFrame) -> dict:
    """
    Aggregate per-vessel economics into a single "Sanctioned Oil Flow Index"
    — the kind of one-number signal a quant desk would subscribe to.
    """
    high_risk = results_df[results_df["risk_score"] >= 70]
    total_vessels = len(high_risk)
    total_barrels = high_risk["est_cargo_barrels"].sum() if "est_cargo_barrels" in high_risk.columns else 0
    total_single_cargo_value = high_risk["est_cargo_value_usd"].sum() if "est_cargo_value_usd" in high_risk.columns else 0
    total_annual_flow = high_risk["est_annual_flow_usd"].sum() if "est_annual_flow_usd" in high_risk.columns else 0

    return {
        "signal_date": datetime.date.today().isoformat(),
        "brent_crude_usd": BRENT_CRUDE_USD_PER_BARREL,
        "high_risk_vessels": total_vessels,
        "est_combined_cargo_barrels": int(total_barrels),
        "est_single_cargo_value_usd": round(total_single_cargo_value, 2),
        "est_annual_sanctioned_flow_usd": round(total_annual_flow, 2),
        "risk_tier": (
            "CRITICAL" if total_annual_flow > 5_000_000_000 else
            "HIGH" if total_annual_flow > 1_000_000_000 else
            "ELEVATED" if total_annual_flow > 500_000_000 else
            "MODERATE"
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    vessels = load_sanctioned_vessels(MARITIME_CSV_PATH)
    results = []

    for _, row in vessels.iterrows():
        imo = str(row["imo"]).split(";")[0].strip()  # some rows have multiple IMOs
        name = row.get("caption", "UNKNOWN")

        record = gfw_search_vessel(imo)
        if record is None:
            results.append({
                "imo": imo, "name": name, "gfw_match": False,
                "risk_score": 40,
                "est_cargo_barrels": 500_000,
                "est_cargo_value_usd": estimate_cargo_value_usd(500_000),
                "est_annual_flow_usd": estimate_annual_flow_usd(500_000, 0),
            })
            continue

        identity_changes = count_identity_changes(record)
        self_reported = record.get("selfReportedInfo", [])
        gfw_vessel_id = self_reported[0]["id"] if self_reported else None

        encounters = 0
        if gfw_vessel_id:
            encounters = count_encounters(gfw_vessel_id, "2025-01-01", "2026-09-27")

        score = compute_risk_score(True, identity_changes, encounters)
        cargo_bbls = estimate_cargo_barrels(record)
        cargo_val = estimate_cargo_value_usd(cargo_bbls)
        annual_flow = estimate_annual_flow_usd(cargo_bbls, encounters)

        results.append({
            "imo": imo,
            "name": name,
            "gfw_match": True,
            "identity_changes": identity_changes,
            "encounters": encounters,
            "risk_score": score,
            "est_cargo_barrels": cargo_bbls,
            "est_cargo_value_usd": cargo_val,
            "est_annual_flow_usd": annual_flow,
        })

        time.sleep(0.3)  # be polite to the API / stay under rate limits

    out = pd.DataFrame(results).sort_values("risk_score", ascending=False)
    out.to_csv("dark_fleet_risk_scores.csv", index=False)
    print(out.to_string(index=False))
    print("\nSaved -> dark_fleet_risk_scores.csv")

    # ── Economic Intelligence Summary ──────────────────────────────────────
    signal = generate_market_signal(out)
    print("\n" + "=" * 70)
    print("  📊  SANCTIONED OIL FLOW INDEX  —  HEDGE FUND SIGNAL")
    print("=" * 70)
    print(f"  Date:                        {signal['signal_date']}")
    print(f"  Brent Crude (USD/bbl):       ${signal['brent_crude_usd']:.2f}")
    print(f"  High-Risk Vessels (≥70):     {signal['high_risk_vessels']}")
    print(f"  Est. Combined Cargo:         {signal['est_combined_cargo_barrels']:,} barrels")
    print(f"  Est. Single-Cargo Value:     ${signal['est_single_cargo_value_usd']:,.0f}")
    print(f"  Est. Annual Sanctioned Flow: ${signal['est_annual_sanctioned_flow_usd']:,.0f}")
    print(f"  Risk Tier:                   {signal['risk_tier']}")
    print("=" * 70)
    print("\n  💡 Signal interpretation for trading desks:")
    print("     • Rising flow → more sanctioned oil reaching market → bearish pressure on Brent")
    print("     • Falling flow → enforcement tightening → supply squeeze → bullish pressure")
    print("     • Sudden spike in high-risk vessels → geopolitical escalation indicator")

    # Save the signal as a separate JSON for dashboard / API consumption
    import json
    with open("sanctioned_oil_flow_signal.json", "w") as f:
        json.dump(signal, f, indent=2)
    print("\n  Saved -> sanctioned_oil_flow_signal.json")


if __name__ == "__main__":
    main()
