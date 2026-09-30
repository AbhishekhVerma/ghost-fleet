"""The dashboard must agree with the snapshot and with the figures quoted in the docs."""

import calendar
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import dark_fleet_pipeline as p  # noqa: E402

APP = (ROOT / "dashboard" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "dashboard" / "index.html").read_text(encoding="utf-8")
VESSELS = json.loads((ROOT / "dashboard" / "data" / "vessels.json").read_text(encoding="utf-8"))["vessels"]
SIGNAL = json.loads((ROOT / "dashboard" / "data" / "signal.json").read_text(encoding="utf-8"))


def js_codes(block_name):
    body = re.search(block_name + r"\s*=\s*(?:new Set\(\[)?\{?(.*?)(?:\]\)|\});", APP, re.S).group(1)
    return set(re.findall(r'\b([A-Z]{3})\b', body))


def test_every_current_flag_has_a_readable_name():
    names = js_codes("const FLAG_NAMES")
    missing = {v["current_flag"] for v in VESSELS if v.get("current_flag")} - names
    assert not missing, f"flags shown as raw codes: {sorted(missing)}"


def test_dashboard_landlocked_list_covers_the_quoted_landlocked_flags():
    from figures import LAND  # the list behind the docs' landlocked count
    quoted = {v["current_flag"] for v in VESSELS if v.get("current_flag") in LAND}
    assert quoted <= js_codes("const LANDLOCKED"), sorted(quoted - js_codes("const LANDLOCKED"))


def test_default_run_rebuilds_the_committed_snapshot_size():
    # a bare `python dark_fleet_pipeline.py` must not silently shrink the live snapshot
    assert p.MAX_VESSELS == SIGNAL["vessels_screened"]


def test_port_call_label_does_not_claim_full_months_when_the_last_is_partial():
    end = datetime.date.fromisoformat(SIGNAL["window"]["end"])
    last_is_partial = end.day < calendar.monthrange(end.year, end.month)[1]
    if last_is_partial:
        assert "full months" not in HTML
