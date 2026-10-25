import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../services/api";
import { Async, Card, useApi } from "../components/ui";
import { MONTHS } from "../utils/format";

const COLORS = ["#0ea5e9", "#6366f1", "#10b981", "#f59e0b", "#ef4444", "#0f2547"];

const labelled = (a) => ({
  ...a,
  points: a.points.map((p) => ({ ...p, period: p.partial_year ? `${p.period}*` : p.period })),
});

const shift = (d, days) => {
  const x = new Date(d + "T00:00:00");
  x.setDate(x.getDate() + days);
  return x.toISOString().slice(0, 10);
};

function DailyCard({ first, last }) {
  const [start, setStart] = useState(shift(last, -60));
  const [end, setEnd] = useState(last);
  const daily = useApi(() => api.trends("daily", start, end), [start, end]);
  return (
    <Card title="Daily rainfall" subtitle={`Choose a date range (data covers ${first} to ${last}; default = last 60 days)`}>
      <div className="mb-3 flex flex-wrap gap-3 text-sm">
        <label>From <input type="date" value={start} min={first} max={last} onChange={(e) => e.target.value && setStart(e.target.value)} className="rounded border px-2 py-1" /></label>
        <label>To <input type="date" value={end} min={first} max={last} onChange={(e) => e.target.value && setEnd(e.target.value)} className="rounded border px-2 py-1" /></label>
      </div>
      <Async res={daily}>
        {(d) => (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={d.points}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="period" fontSize={11} minTickGap={40} />
              <YAxis fontSize={12} unit=" mm" width={55} />
              <Tooltip formatter={(v) => [`${v} mm`, "Rainfall"]} />
              <Bar dataKey="rainfall_mm" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </Async>
    </Card>
  );
}

export default function Analytics() {
  const monthly = useApi(() => api.trends("monthly"), []);
  const annual = useApi(() => api.trends("annual"), []);
  const summary = useApi(api.summary, []);

  // Flat monthly list -> one row per month with a column per year.
  const byYear = (points) => {
    const rows = MONTHS.map((m) => ({ month: m }));
    const years = new Set();
    points.forEach((p) => {
      const [y, m] = p.period.split("-");
      years.add(y);
      rows[Number(m) - 1][y] = p.rainfall_mm;
    });
    return { rows, years: [...years] };
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-navy-900">Rainfall analytics</h1>

      <Async res={summary}>{(s) => <DailyCard first={s.period.start} last={s.period.end} />}</Async>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Annual rainfall total" subtitle="Sum of daily values per year. * = year not yet complete">
          <Async res={annual}>
            {(a0) => { const a = labelled(a0); return (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={a.points}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="period" fontSize={12} />
                  <YAxis fontSize={12} unit=" mm" width={60} />
                  <Tooltip formatter={(v) => [`${v} mm`, "Rainfall"]} />
                  <Bar dataKey="rainfall_mm" fill="#0f2547" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ); }}
          </Async>
        </Card>

        <Card title="Heavy-rain and rainy days per year" subtitle="Heavy ≥ 64.5 mm/day; rainy ≥ 2.5 mm/day (project-defined). * = partial year">
          <Async res={annual}>
            {(a0) => { const a = labelled(a0); return (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={a.points}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="period" fontSize={12} />
                  <YAxis fontSize={12} width={40} allowDecimals={false} />
                  <Tooltip /><Legend />
                  <Bar dataKey="rainy_days" name="Rainy days" fill="#38bdf8" />
                  <Bar dataKey="heavy_days" name="Heavy days" fill="#ef4444" />
                </BarChart>
              </ResponsiveContainer>
            ); }}
          </Async>
        </Card>
      </div>

      <Card title="Monthly rainfall — comparison across years" subtitle="Total rainfall for each month, one line per year">
        <Async res={monthly}>
          {(m) => {
            const { rows, years } = byYear(m.points);
            return (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={rows}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="month" fontSize={12} />
                  <YAxis fontSize={12} unit=" mm" width={60} />
                  <Tooltip /><Legend />
                  {years.map((y, i) => <Line key={y} type="monotone" dataKey={y} stroke={COLORS[i % COLORS.length]} dot={false} strokeWidth={2} />)}
                </LineChart>
              </ResponsiveContainer>
            );
          }}
        </Async>
      </Card>

      <Card title="Seasonal pattern" subtitle="Average rainfall per year in each Indian meteorological season">
        <Async res={summary}>
          {(s) => (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={s.seasonal}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="season" fontSize={12} />
                <YAxis fontSize={12} unit=" mm" width={60} />
                <Tooltip formatter={(v) => [`${v} mm`, "Avg per year"]} />
                <Bar dataKey="avg_total_mm_per_year" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Async>
      </Card>
    </div>
  );
}
