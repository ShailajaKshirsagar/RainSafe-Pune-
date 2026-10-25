import { CloudRain, Droplets, Thermometer, Wind, CalendarDays, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../services/api";
import { Async, Card, FreshnessBadge, Limitations, RiskBadge, Stat, useApi } from "../components/ui";
import { deg, fmtDate, mm } from "../utils/format";

export default function Dashboard({ go }) {
  const cur = useApi(api.current, []);
  const sum = useApi(api.summary, []);
  const risk = useApi(() => api.risk(), []);
  const live = useApi(api.live, []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-navy-900 md:text-3xl">Pune rainfall & waterlogging awareness</h1>
        <p className="mt-1 max-w-2xl text-slate-600">
          Historical rainfall analysis for Pune with a transparent, rule-based rainfall concern indicator.
          This is an awareness tool, not a flood forecast.
        </p>
      </header>

      <Async res={live}>
        {(l) => (
          <div className="rounded-2xl bg-gradient-to-r from-sky-600 to-cyan-500 p-5 text-white shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-sm font-medium">
                <span className="h-2.5 w-2.5 animate-pulse rounded-full bg-white" />
                {l.current ? "Live conditions now · Pune city centre" : "Live conditions unavailable right now"}
              </div>
              <FreshnessBadge status={l.data_status} />
            </div>
            {l.current ? (
              <>
                <div className="mt-3 grid grid-cols-2 gap-4 md:grid-cols-4">
                  <Big label="Temperature" v={deg(l.current.temperature_c)} />
                  <Big label="Humidity" v={`${l.current.humidity_percent ?? "—"}%`} />
                  <Big label="Rain (latest interval)" v={mm(l.current.rain_mm_last_interval)} />
                  <Big label="Wind" v={`${l.current.wind_speed_kmh ?? "—"} km/h`} />
                </div>
                <p className="mt-3 text-xs text-sky-50">
                  Observed at {l.current.observed_at?.replace("T", " ")} IST · model-based current conditions from Open-Meteo, refreshed about every 30 minutes. Not an official IMD observation.
                </p>
              </>
            ) : (
              <p className="mt-2 text-sm text-sky-50">{l.data_status.error || "The live feed could not be reached."} The charts below use saved data.</p>
            )}
          </div>
        )}
      </Async>

      <Async res={cur}>
        {(c) => (
          <div className="rounded-2xl bg-navy-900 p-5 text-white">
            <div className="flex flex-wrap items-center gap-2 text-sm text-sky-200">
              <CalendarDays size={16} /> Latest complete day: <b>{fmtDate(c.date)}</b>
              <span className="rounded-full bg-sky-400/20 px-2 py-0.5 text-xs text-sky-100">
                Daily totals (complete day)
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-4 md:grid-cols-4">
              <Big label="Daily rainfall" v={mm(c.rainfall_mm)} />
              <Big label="Max / min temp" v={`${deg(c.temperature_max_c)} / ${deg(c.temperature_min_c)}`} />
              <Big label="Max wind" v={c.wind_speed_max_kmh === null ? "—" : `${c.wind_speed_max_kmh} km/h`} />
              <Big label="Location" v="Pune city centre" />
            </div>
          </div>
        )}
      </Async>

      <Async res={sum}>
        {(s) => (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Stat icon={Droplets} label="3-day rainfall" value={mm(s.latest_rain_3d_mm)} note={`Ending ${fmtDate(s.latest_date)}`} />
            <Stat icon={Droplets} label="7-day rainfall" value={mm(s.latest_rain_7d_mm)} note={`Ending ${fmtDate(s.latest_date)}`} />
            <Stat icon={CloudRain} label="Highest daily rainfall" value={mm(s.max_daily_mm)} note={fmtDate(s.max_daily_date)} />
            <Stat icon={TrendingUp} label="Heavy-rain days" value={s.heavy_days} note={`≥ ${s.heavy_day_threshold_mm} mm, ${fmtDate(s.period.start)} – ${fmtDate(s.period.end)}`} />
            <Stat icon={Thermometer} label="Highest temperature" value={deg(s.max_temperature_c)} tone="text-orange-500" />
            <Stat icon={Thermometer} label="Lowest temperature" value={deg(s.min_temperature_c)} tone="text-blue-500" />
            <Stat icon={Wind} label="Highest wind speed" value={`${s.max_wind_kmh} km/h`} tone="text-slate-500" />
            <Stat icon={CloudRain} label="Average daily rainfall" value={mm(s.average_daily_mm)} note="All days in dataset" />
          </div>
        )}
      </Async>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Rainfall concern indicator" subtitle="Rule-based, project-defined thresholds">
          <Async res={risk}>
            {(r) => (
              <>
                <RiskBadge category={r.category} label={r.label} />
                <p className="mt-2 text-sm text-slate-600">For {fmtDate(r.assessed_for_date)} (daily {r.measurements.rain_1d_mm} mm · 3-day {r.measurements.rain_3d_mm} mm · 7-day {r.measurements.rain_7d_mm} mm)</p>
                <p className="mt-2 text-sm text-slate-600">
                  {r.triggered_rules.length ? r.triggered_rules.join("; ") : "No threshold was reached."}
                </p>
                <button onClick={() => go("map")} className="mt-3 text-sm font-medium text-sky-700 hover:underline">
                  Explore the risk map & past heavy-rain dates →
                </button>
                <Limitations items={r.limitations.slice(0, 2)} />
              </>
            )}
          </Async>
        </Card>

        <Card title="Average daily rainfall by calendar month" subtitle={sum.data ? `Average over ${sum.data.period.start} to ${sum.data.period.end}` : ""}>
          <Async res={sum}>
            {(s) => (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={s.monthly_average}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="month" fontSize={12} />
                  <YAxis fontSize={12} unit=" mm" width={55} />
                  <Tooltip formatter={(v) => [`${v} mm/day`, "Average"]} />
                  <Bar dataKey="avg_daily_mm" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Async>
        </Card>
      </div>

      <p className="text-xs text-slate-500">
        Source: Open-Meteo (archive + forecast APIs), single Pune city-centre point. History from 2020; recent days refreshed automatically.
      </p>
    </div>
  );
}

const Big = ({ label, v }) => (
  <div>
    <div className="text-xs text-sky-200">{label}</div>
    <div className="text-xl font-semibold">{v}</div>
  </div>
);
