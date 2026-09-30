"""Checks on the committed dashboard snapshot (what the live site serves)."""

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import dark_fleet_pipeline as p  # noqa: E402

VESSELS = ROOT / "dashboard" / "data" / "vessels.json"
SIGNAL = ROOT / "dashboard" / "data" / "signal.json"


def load(path):
    # parse_constant rejects NaN/Infinity, which browsers cannot parse
    def reject(name):
        raise ValueError(f"non-JSON constant {name} in {path.name}")
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def test_snapshot_is_valid_json_and_consistent():
    vessels = load(VESSELS)["vessels"]
    signal = load(SIGNAL)
    assert len(vessels) == signal["vessels_screened"]
    assert sum(v["_lat"] is not None for v in vessels) == signal["vessels_located"]


def test_events_are_trimmed_and_positions_numeric():
    for v in load(VESSELS)["vessels"]:
        assert len(v["events"]) <= p.EVENTS_PER_VESSEL
        if v["_lat"] is not None:
            assert isinstance(v["_lat"], float) and isinstance(v["_lng"], float)
            assert not math.isnan(v["_lat"])


def test_snapshot_stays_small_enough_for_phones():
    assert VESSELS.stat().st_size <= 1_800_000
