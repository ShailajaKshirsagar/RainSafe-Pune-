import { useState } from "react";
import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import { api } from "../services/api";
import { Async, Card, Limitations, Loading, ErrorBox, RiskBadge, useApi } from "../components/ui";
import { RISK, fmtDate, mm } from "../utils/format";

export default function RiskMap() {
  const areas = useApi(api.areas, []);
  const summary = useApi(api.summary, []);
  const [selected, setSelected] = useState(null);
  const [date, setDate] = useState("");
  const detail = useApi(() => (selected ? api.area(selected) : Promise.resolve(null)), [selected]);
  const risk = useApi(() => api.risk(date || undefined), [date]);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy-900">Risk map</h1>
      <p className="max-w-3xl text-sm text-slate-600">
        The markers are representative Pune locations. All of them use the <b>same</b> Pune city-centre rainfall
        record, so they share one indicator. This map does <b>not</b> show which streets will flood.
      </p>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="overflow-hidden rounded-2xl shadow-sm ring-1 ring-slate-200 lg:col-span-2">
          {areas.loading && <Loading text="Loading map…" />}
          {areas.error && <ErrorBox message={areas.error} onRetry={areas.retry} />}
          {areas.data && (
            <MapContainer center={[18.5204, 73.8567]} zoom={11} style={{ height: 460 }} scrollWheelZoom>
              <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {areas.data.map((a) => (
                <CircleMarker
                  key={a.id}
                  center={[a.latitude, a.longitude]}
                  radius={11}
                  pathOptions={{ color: "#0f2547", fillColor: RISK[risk.data?.category || "unknown"].dot, fillOpacity: 0.85 }}
                  eventHandlers={{ click: () => setSelected(a.id) }}
                >
                  <Popup><b>{a.name}</b><br />Details appear in the side panel</Popup>
                </CircleMarker>
              ))}
            </MapContainer>
          )}
          <div className="flex flex-wrap gap-4 bg-white p-3 text-xs text-slate-600">
            {["low", "moderate", "high"].map((k) => (
              <span key={k} className="flex items-center gap-1">
                <span className="h-3 w-3 rounded-full" style={{ background: RISK[k].dot }} /> {RISK[k].text} concern
              </span>
            ))}
            <span>Map © OpenStreetMap contributors</span>
          </div>
        </div>

        <Card title="Selected location">
          {!selected && <p className="text-sm text-slate-500">Click a marker on the map.</p>}
          {selected && (
            <Async res={detail}>
              {(d) => (
                <div className="space-y-2 text-sm">
                  <div className="text-lg font-semibold text-navy-900">{d.name}</div>
                  <div className="text-slate-500">{d.latitude}, {d.longitude} (approximate)</div>
                  <RiskBadge category={d.assessment.category} label={d.assessment.label} />
                  <div>Rainfall on {fmtDate(d.observation.date)}: <b>{mm(d.observation.rainfall_mm)}</b></div>
                  <div>3-day: <b>{mm(d.observation.rain_3d_mm)}</b> · 7-day: <b>{mm(d.observation.rain_7d_mm)}</b></div>
                  <p className="rounded-lg bg-sky-50 p-2 text-xs text-sky-900">{d.rainfall_note}</p>
                  <ul className="list-disc pl-5 text-slate-700">{d.advisories.map((t) => <li key={t}>{t}</li>)}</ul>
                </div>
              )}
            </Async>
          )}
        </Card>
      </div>

      <Card title="Try a past date" subtitle="See how the indicator behaves on historical rainfall (it also recolours the markers above)">
        <div className="mb-3 flex flex-wrap items-center gap-2 text-sm">
          <input type="date" value={date} min={summary.data?.period.start} max={summary.data?.period.end} onChange={(e) => setDate(e.target.value)} className="rounded border px-2 py-1" />
          <button onClick={() => setDate("")} className="rounded border px-2 py-1 hover:bg-slate-50">Latest</button>
          <Async res={summary}>
            {(s) => s.top_3day_events.map((e) => (
              <button key={e.date} onClick={() => setDate(e.date)} className="rounded-full bg-sky-100 px-3 py-1 text-sky-800 hover:bg-sky-200">
                {fmtDate(e.date)} ({e.rain_3d_mm} mm / 3 days)
              </button>
            ))}
          </Async>
        </div>
        <Async res={risk}>
          {(r) => (
            <div className="space-y-2 text-sm">
              <RiskBadge category={r.category} label={r.label} />
              <div>Date: <b>{fmtDate(r.assessed_for_date)}</b> — daily {mm(r.measurements.rain_1d_mm)}, 3-day {mm(r.measurements.rain_3d_mm)}, 7-day {mm(r.measurements.rain_7d_mm)}</div>
              <div><b>Triggered:</b> {r.triggered_rules.length ? r.triggered_rules.join("; ") : "none"}</div>
              <details className="text-slate-600">
                <summary className="cursor-pointer">Thresholds & methodology</summary>
                <pre className="mt-2 overflow-auto rounded bg-slate-50 p-2 text-xs">{JSON.stringify(r.thresholds_used, null, 2)}</pre>
                <p className="mt-1">{r.methodology}</p>
              </details>
              <Limitations items={r.limitations} />
            </div>
          )}
        </Async>
      </Card>
    </div>
  );
}
