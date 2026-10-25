export const RISK = {
  low: { text: "Low", bg: "bg-emerald-100", fg: "text-emerald-800", dot: "#10b981" },
  moderate: { text: "Moderate", bg: "bg-amber-100", fg: "text-amber-800", dot: "#f59e0b" },
  high: { text: "High", bg: "bg-red-100", fg: "text-red-800", dot: "#ef4444" },
  unknown: { text: "Unknown", bg: "bg-slate-200", fg: "text-slate-700", dot: "#94a3b8" },
};

export const mm = (v) => (v === null || v === undefined ? "—" : `${v} mm`);
export const deg = (v) => (v === null || v === undefined ? "—" : `${v}°C`);

export const fmtDate = (s) =>
  new Date(s + "T00:00:00").toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" });

export const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
