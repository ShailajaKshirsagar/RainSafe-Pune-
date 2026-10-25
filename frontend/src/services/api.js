import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const http = axios.create({ baseURL: BASE, timeout: 30000 });

const get = (url, params) => http.get(url, { params }).then((r) => r.data);

export const api = {
  baseUrl: BASE,
  current: () => get("/api/weather/current"),
  live: () => get("/api/weather/live"),
  summary: () => get("/api/rainfall/summary"),
  trends: (granularity, start, end) =>
    get("/api/rainfall/trends", { granularity, start, end }),
  areas: () => get("/api/areas"),
  area: (id) => get(`/api/areas/${id}`),
  risk: (date) => get("/api/risk/assessment", date ? { date } : undefined),
  advisories: () => get("/api/advisories"),
};

export function errorMessage(err) {
  if (err.response) return err.response.data?.detail || `Server error (${err.response.status})`;
  return "Cannot reach the RainSafe backend. Is it running? (Free hosting may need ~1 minute to wake up.)";
}
