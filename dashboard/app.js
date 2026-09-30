/* Ghost Fleet — Hidden Supply Monitor
   Reads the pipeline snapshot (data/vessels.json, data/signal.json) and draws
   a chart of shadow-fleet tankers plus a per-vessel evidence dossier.
   Open a vessel directly with #imo=<number>. */

const DATA_URL = "data/vessels.json";
const SIGNAL_URL = "data/signal.json";
const HIGH_RISK = 70;

const FLAG_NAMES = {
    RUS: "Russia", CMR: "Cameroon", OMN: "Oman", SLE: "Sierra Leone", GNQ: "Equatorial Guinea",
    PAN: "Panama", COM: "Comoros", MLI: "Mali", MOZ: "Mozambique", ABW: "Aruba", BRB: "Barbados",
    GUY: "Guyana", ZWE: "Zimbabwe", GIN: "Guinea", BES: "Bonaire", MWI: "Malawi", LBR: "Liberia",
    GMB: "Gambia", DEU: "Germany", PLW: "Palau", COK: "Cook Islands", HKG: "Hong Kong",
    SGP: "Singapore", MHL: "Marshall Islands", DNK: "Denmark", CYP: "Cyprus", GAB: "Gabon",
    MLT: "Malta", GRC: "Greece", LVA: "Latvia", LTU: "Lithuania", NOR: "Norway", TGO: "Togo",
    KNA: "St Kitts & Nevis", BHS: "Bahamas", PRT: "Portugal", VCT: "St Vincent", TZA: "Tanzania",
    HND: "Honduras", BLZ: "Belize", MNG: "Mongolia", CHN: "China", IND: "India", ARE: "UAE",
    IRN: "Iran", TUR: "Türkiye", VNM: "Vietnam", KHM: "Cambodia", MDV: "Maldives", STP: "São Tomé",
    SWZ: "Eswatini", BOL: "Bolivia", BEN: "Benin", DJI: "Djibouti", VUT: "Vanuatu", TUV: "Tuvalu",
};
const LANDLOCKED = new Set(["MLI", "MWI", "ZWE", "MNG", "SWZ", "BOL"]);

const SCORE_PARTS = [
    { key: "sanctions", label: "Sanctions or shadow-fleet listing", color: "#a3165f" },
    { key: "identity", label: "Identity switches", color: "#1c2a35" },
    { key: "meetings", label: "Loitering at sea", color: "#5d707a" },
    { key: "ais_gaps", label: "AIS switched off", color: "#9fb2ba" },
];

let vessels = [];
let markers = new Map();
let trackLayer = null;

// ── Helpers ─────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) =>
        ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function flagName(code) {
    return FLAG_NAMES[code] || code || "unknown flag";
}

function titleCase(name) {
    return String(name || "").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase());
}

function fmtDate(iso, withYear = true) {
    if (!iso) return "—";
    const d = new Date(iso.length <= 10 ? iso + "T00:00:00Z" : iso + "Z");
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: withYear ? "numeric" : undefined, timeZone: "UTC" });
}

function fmtMonth(ym) {
    return new Date(ym + "-01T00:00:00Z").toLocaleDateString("en-GB", { month: "short", timeZone: "UTC" });
}

function fmtUsdRange(low, high) {
    if (high >= 1e9) {
        const d = high >= 1e10 ? 0 : 1;
        return `$${(low / 1e9).toFixed(d)}–${(high / 1e9).toFixed(d)} bn`;
    }
    return `$${Math.round(low / 1e6)}–${Math.round(high / 1e6)}m`;
}

function fmtBarrels(n) {
    return n >= 1e6 ? (n / 1e6).toFixed(1) + "m" : Math.round(n / 1e3) + "k";
}

// ── Map ─────────────────────────────────────────────────────

const map = L.map("map", { worldCopyJump: true, zoomControl: false, minZoom: 2 })
    .setView([42, 45], 3);
L.control.zoom({ position: "topright" }).addTo(map);
L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}", {
    maxZoom: 13,
    attribution: "Esri, GEBCO, NOAA, Garmin, HERE",
}).addTo(map);

function drawVessels() {
    for (const v of vessels) {
        if (v._lat == null) continue;
        const high = v.risk_score >= HIGH_RISK;
        const m = L.circleMarker([v._lat, v._lng], {
            radius: high ? 6 : 5,
            color: high ? "#f8fafa" : "#1c2a35",
            weight: high ? 1.5 : 1.5,
            fillColor: high ? "#a3165f" : "#f8fafa",
            fillOpacity: 1,
        }).addTo(map);
        m.bindTooltip(`<b>${esc(titleCase(v.current_name || v.name))}</b><br>Score ${v.risk_score} · last seen ${fmtDate(v.last_seen)}`);
        m.on("click", () => openDossier(v.imo));
        markers.set(v.imo, m);
    }
}

function drawTrack(v) {
    clearTrack();
    const pts = v.events.filter((e) => e.lat != null);
    if (!pts.length) return;
    // Points only: events are sparse snapshots, and a line between them
    // would imply a route (often straight across land) the ship never sailed.
    trackLayer = L.layerGroup().addTo(map);
    for (const e of pts) {
        const label = eventLabel(e);
        const mk = e.kind === "port_visit"
            ? L.marker([e.lat, e.lon], { icon: L.divIcon({ className: "", html: '<i class="square"></i>', iconSize: [8, 8] }) })
            : L.circleMarker([e.lat, e.lon], { radius: 5, color: "#a3165f", weight: 2, fill: false });
        mk.bindTooltip(`${fmtDate(e.start)}<br>${esc(label)}`).addTo(trackLayer);
    }
    for (const [imo, m] of markers) m.setStyle({ opacity: imo === v.imo ? 1 : 0.25, fillOpacity: imo === v.imo ? 1 : 0.25 });
    document.body.classList.add("tracking");
    map.fitBounds(L.latLngBounds(pts.map((e) => [e.lat, e.lon])).pad(0.25), { maxZoom: 6 });
}

function clearTrack() {
    if (trackLayer) map.removeLayer(trackLayer);
    trackLayer = null;
    for (const m of markers.values()) m.setStyle({ opacity: 1, fillOpacity: 1 });
    document.body.classList.remove("tracking");
}

// ── Monitor view ────────────────────────────────────────────

function renderMonitor(signal, meta) {
    $("snapshot").textContent =
        `Snapshot of ${fmtDate(meta.window.start)} – ${fmtDate(meta.window.end)}, built ${fmtDate(meta.generated)}`;

    const trend = signal.activity_trend_3m_pct;
    if (trend == null) {
        $("headline").textContent = "Not enough months of data yet to call a trend.";
    } else {
        const dir = trend < 0 ? "fell" : "rose";
        $("headline").textContent =
            `Sanctioned tanker activity ${dir} ${Math.abs(trend).toFixed(0)}% in the last three months.`;
    }
    renderTrend(signal.monthly);

    const ports = signal.monthly.reduce((n, m) => n + m.port_visits, 0);
    $("fig-tracked").textContent = `${signal.vessels_located} of ${signal.vessels_screened}`;
    $("fig-high").textContent = signal.high_risk_vessels;
    $("fig-ports").textContent = ports.toLocaleString("en-GB");
    const flow = signal.est_annual_flow_usd;
    $("fig-value").textContent = `${fmtUsdRange(flow.low, flow.high)} a year`;
    $("fig-value-note").textContent =
        `Upper bound for the ${signal.high_risk_vessels} vessels scored ${HIGH_RISK}+: hull capacity × estimated voyages × ` +
        `Brent at $${signal.brent_crude_usd}. Loaded state is not observed, so real cargo is lower.`;

    renderPorts(signal.top_ports);
    renderList("");
}

function renderTrend(series) {
    const svg = $("trend-svg");
    const w = svg.clientWidth || 350, h = 96, top = 16, base = h - 18;
    const max = Math.max(...series.map((m) => m.active_vessels), 1);
    const bw = w / series.length;
    const n = series.length;
    // The headline compares the last 3 full months (n-4..n-2) with the 3 before.
    const recent = new Set([n - 4, n - 3, n - 2]);
    const prior = new Set([n - 7, n - 6, n - 5]);

    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = series.map((m, i) => {
        const bh = ((base - top) * m.active_vessels) / max;
        const cls = recent.has(i) ? "bar recent" : prior.has(i) ? "bar prior" : "bar";
        const x = i * bw + 2;
        return `<rect class="${cls}" x="${x}" y="${base - bh}" width="${bw - 4}" height="${bh}"><title>${fmtMonth(m.month)}: ${m.active_vessels} tankers</title></rect>` +
            (recent.has(i) || prior.has(i) ? `<text class="value" x="${x + (bw - 4) / 2}" y="${base - bh - 4}" text-anchor="middle">${m.active_vessels}</text>` : "") +
            `<text x="${x + (bw - 4) / 2}" y="${h - 4}" text-anchor="middle">${fmtMonth(m.month).slice(0, 1)}</text>`;
    }).join("");
    $("trend-caption").textContent =
        `Tankers with recorded activity each month, ${fmtMonth(series[0].month)} to ${fmtMonth(series[n - 1].month)}. ` +
        `The headline compares the dark bars with the grey ones. The latest month is incomplete.`;
}

function renderPorts(topPorts) {
    $("port-list").innerHTML = topPorts
        .map((p) => `<li><span>${esc(titleCase(p.port))}</span><span>${p.calls}</span></li>`).join("");
}

function renderList(query) {
    const q = query.trim().toLowerCase();
    const rows = vessels.filter((v) => !q || v.imo.includes(q) ||
        v.identity_history.some((h) => (h.name || "").toLowerCase().includes(q)) ||
        String(v.name).toLowerCase().includes(q));

    $("vessel-list").innerHTML = rows.length ? rows.map((v) => `
        <li><button type="button" data-imo="${esc(v.imo)}">
            <span class="v-name">${esc(titleCase(v.current_name || v.name))}</span>
            <span class="v-score ${v.risk_score >= HIGH_RISK ? "high" : ""}">${v.risk_score}</span>
            <span class="v-meta">IMO ${esc(v.imo)} · ${esc(flagName(v.current_flag))} · ${v.identity_changes} identity switches</span>
        </button></li>`).join("")
        : `<li class="empty">No vessel matches “${esc(query)}”. Try a former name or the 7-digit IMO.</li>`;
}

// ── Dossier view ────────────────────────────────────────────

function eventLabel(e) {
    if (e.kind === "port_visit") return `Port call, ${titleCase(e.port || "unnamed port")}`;
    if (e.kind === "loitering") return `Loitered at sea ${Math.round(e.hours || 0)} h`;
    if (e.kind === "gap") return `AIS off ${Math.round(e.hours || 0)} h`;
    if (e.kind === "encounter") return `Met ${titleCase(e.partner || "another vessel")}`;
    return e.kind;
}

function openDossier(imo) {
    const v = vessels.find((x) => x.imo === imo);
    if (!v) return;
    history.replaceState(null, "", "#imo=" + imo);

    const name = titleCase(v.current_name || v.name);
    $("d-name").textContent = name;
    const flag = v.current_flag;
    $("d-now").textContent = v.last_seen
        ? `IMO ${v.imo}. Now flagged to ${flagName(flag)}${LANDLOCKED.has(flag) ? ", a landlocked country" : ""}. Last seen ${fmtDate(v.last_seen)}.`
        : `IMO ${v.imo}. No position recorded in this window.`;

    const score = $("d-score");
    score.textContent = v.risk_score;
    score.className = "score-number" + (v.risk_score >= HIGH_RISK ? " high" : "");
    const b = v.risk_breakdown;
    $("d-bar").innerHTML = SCORE_PARTS.filter((p) => b[p.key] > 0)
        .map((p) => `<span style="width:${b[p.key]}%;background:${p.color}" title="${p.label}: ${b[p.key]}"></span>`).join("");
    $("d-parts").innerHTML = SCORE_PARTS.map((p) => `
        <li class="${b[p.key] ? "" : "zero"}"><span>${p.label}</span><b>${b[p.key] ? "+" + b[p.key] : "0"}</b></li>`).join("");

    const ais = v.identity_history.filter((h) => h.source === "AIS");
    $("d-identities").innerHTML = ais.length ? ais.map((h) => `
        <li><span class="id-name">${esc(titleCase(h.name))}</span>
        <span class="id-meta">${esc(flagName(h.flag))} · MMSI ${esc(h.mmsi)} · ${fmtDate(h.from)} – ${fmtDate(h.to)}</span></li>`).join("")
        : `<li>No AIS identity found for this IMO.</li>`;

    const recent = v.events.slice(-12).reverse();
    $("d-events").innerHTML = recent.length ? recent.map((e, i) => `
        <li><time datetime="${esc(e.start)}">${fmtDate(e.start)}</time>
        ${e.lat != null ? `<button type="button" data-event="${i}">${esc(eventLabel(e))}</button>` : esc(eventLabel(e))}</li>`).join("")
        : `<li>No loitering, port calls or AIS gaps recorded in this window.</li>`;
    $("d-events").onclick = (ev) => {
        const i = ev.target.dataset.event;
        if (i != null) map.setView([recent[i].lat, recent[i].lon], 7);
    };

    const cap = v.est_cargo_barrels, flow = v.est_annual_flow_usd;
    $("d-size").textContent =
        `Carries about ${fmtBarrels(cap.low)}–${fmtBarrels(cap.high)} barrels per load (from ${cap.basis}). ` +
        `At ${flow.voyages_per_year[0]}–${flow.voyages_per_year[1]} loaded voyages a year, that is ` +
        `${fmtUsdRange(flow.low, flow.high)} of oil a year if every voyage sailed full.`;
    $("d-cargo").textContent = v.cargo_status === "UNKNOWN"
        ? "unknown. Public data has no draft reading, so we do not guess whether it is loaded."
        : `${v.cargo_status.toLowerCase()} (${Math.round(v.cargo_confidence * 100)}% confidence)`;

    const programs = v.sanction_programs.split(";").filter(Boolean).length;
    $("d-sources").innerHTML =
        `Named on ${programs} lists. ` +
        (v.opensanctions_url ? `<a href="${esc(v.opensanctions_url)}" target="_blank" rel="noopener">See the listings on OpenSanctions</a>.` : "");

    $("view-monitor").hidden = true;
    $("view-dossier").hidden = false;
    $("rail").scrollTop = 0;
    drawTrack(v);
    $("d-name").focus?.();
}

function closeDossier() {
    history.replaceState(null, "", location.pathname);
    $("view-dossier").hidden = true;
    $("view-monitor").hidden = false;
    clearTrack();
    map.setView([42, 45], 3);
}

// ── Boot ────────────────────────────────────────────────────

async function load() {
    try {
        const [vr, sr] = await Promise.all([fetch(DATA_URL), fetch(SIGNAL_URL)]);
        if (!vr.ok || !sr.ok) throw new Error(`HTTP ${vr.status}/${sr.status}`);
        const data = await vr.json();
        const signal = await sr.json();
        vessels = data.vessels;
        drawVessels();
        renderMonitor(signal, data);

        const m = location.hash.match(/imo=(\d{7})/);
        if (m) openDossier(m[1]);
    } catch (err) {
        $("headline").textContent = "The snapshot could not be loaded.";
        $("view-monitor").insertAdjacentHTML("afterbegin",
            `<p class="status">Could not read ${DATA_URL} (${esc(err.message)}). Serve the dashboard folder over HTTP, ` +
            `for example <code>python -m http.server</code>, and run the pipeline if the data files are missing.</p>`);
    }
}

$("vessel-search").addEventListener("input", (e) => renderList(e.target.value));
$("vessel-list").addEventListener("click", (e) => {
    const btn = e.target.closest("button[data-imo]");
    if (btn) openDossier(btn.dataset.imo);
});
$("btn-back").addEventListener("click", closeDossier);
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !$("view-dossier").hidden) closeDossier();
});

load();
