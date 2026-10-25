import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Loader2, RefreshCw } from "lucide-react";
import { errorMessage } from "../services/api";
import { RISK } from "../utils/format";

// Fetch helper that gives loading / error / retry for free.
export function useApi(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  const load = useCallback(() => {
    setState((s) => ({ ...s, loading: true, error: null }));
    fn()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((e) => setState({ data: null, loading: false, error: errorMessage(e) }));
    // eslint-disable-next-line
  }, deps);
  useEffect(load, [load]);
  return { ...state, retry: load };
}

export const Card = ({ title, subtitle, children, className = "" }) => (
  <section className={`rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200 ${className}`}>
    {title && <h3 className="text-base font-semibold text-navy-900">{title}</h3>}
    {subtitle && <p className="mb-3 text-xs text-slate-500">{subtitle}</p>}
    {!subtitle && title && <div className="mb-3" />}
    {children}
  </section>
);

export const Stat = ({ icon: Icon, label, value, note, tone = "text-sky-600" }) => (
  <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-200">
    <div className="flex items-center gap-2 text-sm text-slate-500">
      {Icon && <Icon size={16} className={tone} />} {label}
    </div>
    <div className="mt-1 text-2xl font-bold text-navy-900">{value}</div>
    {note && <div className="mt-1 text-xs text-slate-500">{note}</div>}
  </div>
);

export const RiskBadge = ({ category, label }) => {
  const r = RISK[category] || RISK.unknown;
  return (
    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-sm font-semibold ${r.bg} ${r.fg}`}>
      <span className="h-2.5 w-2.5 rounded-full" style={{ background: r.dot }} />
      {label || r.text}
    </span>
  );
};

export const Loading = ({ text = "Loading data…" }) => (
  <div className="flex items-center gap-2 p-6 text-slate-500">
    <Loader2 className="animate-spin" size={18} /> {text}
  </div>
);

export const ErrorBox = ({ message, onRetry }) => (
  <div className="flex flex-wrap items-center gap-3 rounded-xl bg-red-50 p-4 text-sm text-red-800 ring-1 ring-red-200">
    <AlertTriangle size={18} /> <span className="flex-1">{message}</span>
    {onRetry && (
      <button onClick={onRetry} className="inline-flex items-center gap-1 rounded-lg bg-red-600 px-3 py-1.5 text-white hover:bg-red-700">
        <RefreshCw size={14} /> Retry
      </button>
    )}
  </div>
);

export const Empty = ({ text = "No data available for this selection." }) => (
  <div className="p-6 text-center text-sm text-slate-500">{text}</div>
);

// Wrap any fetch result: shows loading / error / content.
export const Async = ({ res, children }) => {
  if (res.loading) return <Loading />;
  if (res.error) return <ErrorBox message={res.error} onRetry={res.retry} />;
  if (!res.data) return <Empty />;
  return children(res.data);
};

export const Limitations = ({ items }) => (
  <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-slate-500">
    {items.map((t) => <li key={t}>{t}</li>)}
  </ul>
);

export const FreshnessBadge = ({ status }) => {
  if (!status) return null;
  const live = status.mode === "live";
  const text = live
    ? `Data up to date through ${status.latest_complete_day}`
    : `Offline mode: showing saved data through ${status.latest_complete_day}`;
  return (
    <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium ${live ? "bg-emerald-100 text-emerald-800" : "bg-amber-100 text-amber-800"}`}>
      <span className={`h-2 w-2 rounded-full ${live ? "animate-pulse bg-emerald-500" : "bg-amber-500"}`} /> {text}
    </span>
  );
};
