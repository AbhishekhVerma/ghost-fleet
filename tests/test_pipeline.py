"""Offline tests for dark_fleet_pipeline. Run: python -m pytest -q"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import dark_fleet_pipeline as p  # noqa: E402

# Shaped like GFW v3 responses (field names from the official gfw-api-python-client models).
VESSEL = {
    "selfReportedInfo": [
        {"id": "aaa", "ssvid": "273000001", "shipname": "OLD NAME", "flag": "RUS", "imo": "9000001",
         "transmissionDateFrom": "2023-01-01T00:00:00Z", "transmissionDateTo": "2025-02-01T00:00:00Z"},
        {"id": "bbb", "ssvid": "626000002", "shipname": "NEW NAME", "flag": "GAB", "imo": "9000001",
         "transmissionDateFrom": "2025-03-01T00:00:00Z", "transmissionDateTo": "2026-09-01T00:00:00Z"},
    ],
    "registryInfo": [{"shipname": "NEW NAME", "flag": "GAB", "imo": "9000001", "tonnageGt": 60000, "lengthM": 250}],
}
EVENTS = {
    "public-global-gaps-events:latest": [
        {"start": "2026-05-03T10:00:00Z", "position": {"lat": 45.0, "lon": 36.5},
         "gap": {"durationHours": 30, "intentionalDisabling": True}},
    ],
    "public-global-loitering-events:latest": [
        {"start": "2026-06-10T00:00:00Z", "position": {"lat": 36.4, "lon": 22.9},
         "loitering": {"totalTimeHours": 12}},
    ],
    "public-global-port-visits-events:latest": [
        {"start": "2026-08-20T00:00:00Z", "position": {"lat": 44.7, "lon": 37.8},
         "port_visit": {"startAnchorage": {"name": "NOVOROSSIYSK", "flag": "RUS"}}},
    ],
    "public-global-encounters-events:latest": [],
}


def fake_gfw_get(path, params, offline=False):
    if path == "vessels/search":
        return {"entries": [VESSEL]}
    entries = EVENTS[params["datasets[0]"]]
    return {"entries": entries if params["offset"] == 0 else []}


def test_identity_changes_counts_names_flags_and_mmsi():
    # one switch: OLD NAME/RUS/273.. -> NEW NAME/GAB/626..
    assert p.count_identity_changes(VESSEL) == 1


def test_risk_score_is_capped_and_explained():
    score, breakdown = p.compute_risk_score(True, 10, 10, 10, 10)
    assert score == 100 and breakdown == {"sanctions": 40, "identity": 30, "ais_gaps": 15, "meetings": 15}
    assert p.compute_risk_score(False, 0, 0, 0)[0] == 30  # shadow-fleet listing only


def test_cargo_state_is_unknown_without_draft():
    assert p.cargo_classifier.classify(None, None) == (
        "UNKNOWN", 0.0, {"draft_m": None, "speed_knots": None, "vessel_type": "unknown"})
    assert p.cargo_classifier.classify(19.0, 10.0, "crude_oil_tanker")[0] == "LOADED"
    assert p.cargo_classifier.classify(7.0, 14.5, "oil_tanker")[0] == "BALLAST"


def test_capacity_prefers_tonnage_then_length_then_default():
    assert p.estimate_cargo_barrels(60000, 250)["basis"].startswith("gross tonnage")
    assert p.estimate_cargo_barrels(None, 330)["low"] == 1_900_000
    assert p.estimate_cargo_barrels(None, None) == {"low": 300_000, "high": 1_100_000,
                                                    "basis": "no size data (wide default range)"}


def test_monthly_series_covers_window_and_counts_active_vessels():
    vessels = [{"imo": "1", "events": [{"kind": "gap", "start": "2026-05-03T10:00"},
                                       {"kind": "port_visit", "start": "2026-05-20T00:00"}]},
               {"imo": "2", "events": [{"kind": "gap", "start": "2026-05-09T00:00"}]}]
    series = p.monthly_series(vessels, "2026-03-15", "2026-07-01")
    assert [m["month"] for m in series] == ["2026-04", "2026-05", "2026-06", "2026-07"]  # partial March skipped
    may = series[1]
    assert may["active_vessels"] == 2 and may["ais_gaps"] == 2 and may["port_visits"] == 1


def test_analyse_vessel_end_to_end(monkeypatch):
    monkeypatch.setattr(p, "gfw_get", fake_gfw_get)
    row = pd.Series({"imo": "9000001", "caption": "NEW NAME", "id": "os-1", "datasets": "ua_war_sanctions",
                     "_sanctioned": True})
    v = p.analyse_vessel(row, "2025-10-01", "2026-09-27", offline=False)

    assert v["gfw_match"] and v["current_name"] == "NEW NAME"
    assert (v["_lat"], v["_lng"], v["last_seen"][:10]) == (44.7, 37.8, "2026-08-20")  # latest event wins
    assert v["ais_gaps"] == 1 and v["loitering_events"] == 1 and v["port_visits"] == 1
    assert v["events"][-1]["port"] == "NOVOROSSIYSK"
    assert v["risk_score"] == 40 + 10 + 5 + 0  # 1 loitering event < 4
    assert v["cargo_status"] == "UNKNOWN" and v["cargo_confidence"] == 0.0
    assert v["est_annual_flow_usd"]["low"] < v["est_annual_flow_usd"]["high"]

    signal = p.generate_market_signal([v], "2025-10-01", "2026-09-27")
    assert signal["top_ports"] == [{"port": "NOVOROSSIYSK", "calls": 1}]
    assert signal["high_risk_vessels"] == 0 and len(signal["monthly"]) == 12  # 55 < 70; Oct-2025..Sep-2026


def test_loader_keeps_shadow_fleet_and_strips_imo_prefix(tmp_path):
    csv = tmp_path / "m.csv"
    pd.DataFrame([
        {"type": "VESSEL", "caption": "A", "imo": "IMO9000001", "risk": "mare.shadow;poi", "datasets": "ua", "id": "a1"},
        {"type": "VESSEL", "caption": "A", "imo": "IMO9000001", "risk": "sanction", "datasets": "ofac", "id": "a2"},
        {"type": "VESSEL", "caption": "B", "imo": "IMO9000002", "risk": "mare.detained", "datasets": "x", "id": "b"},
        {"type": "VESSEL", "caption": "C", "imo": "IMO8000003", "risk": "mare.shadow;poi", "datasets": "x", "id": "c"},
        {"type": "ORGANIZATION", "caption": "D", "imo": None, "risk": "sanction", "datasets": "x", "id": "d"},
    ]).assign(flag="ru", url="https://example").to_csv(csv, index=False)
    out = p.load_sanctioned_vessels(str(csv))
    assert out["imo"].tolist() == ["9000001", "8000003"]  # merged, sanctioned first
    first = out.iloc[0]
    assert first["_sanctioned"] and first["datasets"] == "ofac;ua" and first["id"] == "a1"


def test_search_merges_split_entries_and_drops_foreign_identities(monkeypatch):
    body = {"entries": [
        {"selfReportedInfo": [{"id": "a", "imo": "9240885", "shipname": "WOLF", "flag": "ABW", "ssvid": "1"}]},
        {"selfReportedInfo": [{"id": "b", "imo": "9240885", "shipname": "EAST 1", "flag": "HKG", "ssvid": "2"},
                              {"id": "c", "imo": None, "shipname": "OTHER SHIP", "flag": "PAN", "ssvid": "2"}],
         "registryInfo": [{"imo": "9240885", "shipname": "EAST1", "flag": "HKG"}]},
    ]}
    monkeypatch.setattr(p, "gfw_get", lambda *a, **k: body)
    rec = p.gfw_search_vessel("9240885")
    assert p.gfw_vessel_ids(rec) == ["a", "b"]
    assert p.count_identity_changes(rec) == 1  # EAST 1/HKG/2 -> WOLF/ABW/1


def test_missing_csv_cells_become_json_null(monkeypatch):
    import json
    monkeypatch.setattr(p, "gfw_get", fake_gfw_get)
    row = pd.Series({"imo": "9000001", "caption": "X", "id": "os", "datasets": "ua",
                     "_sanctioned": True, "flag": float("nan"), "url": float("nan")})
    v = p.analyse_vessel(row, "2025-10-01", "2026-09-27", offline=False)
    assert v["flag_listed"] is None
    json.dumps(v, allow_nan=False, default=str)  # raises on NaN
