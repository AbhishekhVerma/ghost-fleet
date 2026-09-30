"""Every figure quoted in the submission materials, from the committed snapshot."""
import json
import statistics
from collections import Counter

V = json.load(open("dashboard/data/vessels.json", encoding="utf-8"))["vessels"]
S = json.load(open("dashboard/data/signal.json", encoding="utf-8"))
LAND = {"MLI", "MWI", "ZWE", "MNG", "SWZ", "BOL", "AFG", "AND", "ARM", "AUT", "AZE", "BDI", "BFA", "BLR",
        "BTN", "BWA", "CAF", "CHE", "CZE", "ETH", "HUN", "KAZ", "KGZ", "LAO", "LIE", "LSO", "LUX", "MDA",
        "MKD", "NER", "NPL", "PRY", "RWA", "SMR", "SRB", "SSD", "SVK", "TCD", "TJK", "TKM", "UGA", "UZB",
        "VAT", "ZMB", "XKX"}
ch = [v.get("identity_changes", 0) for v in V]
m = S["monthly"]
recent = sum(x["active_vessels"] for x in m[-4:-1])
prior = sum(x["active_vessels"] for x in m[-7:-4])
out = {
    "screened": S["vessels_screened"], "matched": S["vessels_matched"], "located": S["vessels_located"],
    "high_risk": S["high_risk_vessels"],
    "trend_pct": S["activity_trend_3m_pct"], "recent_3m": recent, "prior_3m": prior,
    "trend_check_pct": round((recent - prior) / prior * 100, 1),
    "monthly_active": [x["active_vessels"] for x in m],
    "switched_any": sum(c >= 1 for c in ch), "switched_5plus": sum(c >= 5 for c in ch),
    "median_switches": statistics.median(ch),
    "flags_used": len({h["flag"] for v in V for h in v["identity_history"] if h["flag"]}),
    "landlocked_now": dict(Counter(v.get("current_flag") for v in V if v.get("current_flag") in LAND)),
    "russia_now": sum(v.get("current_flag") == "RUS" for v in V),
    "median_lists": statistics.median(len(v["sanction_programs"].split(";")) for v in V),
    "port_calls_full_months": sum(x["port_visits"] for x in m),
    "top_ports": [(p["port"], p["calls"]) for p in S["top_ports"][:6]],
    "flow_bn": [round(S["est_annual_flow_usd"]["low"] / 1e9), round(S["est_annual_flow_usd"]["high"] / 1e9)],
    "east1": next(({"score": v["risk_score"], "ids": sum(h["source"] == "AIS" for h in v["identity_history"])}
                   for v in V if v["imo"] == "9240885"), None),
}
print(json.dumps(out, indent=1, ensure_ascii=False))
