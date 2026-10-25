# RainSafe Pune

Rainfall analytics, an interactive map and a transparent **rule-based rainfall concern indicator** for Pune.
Built with Python (Pandas, FastAPI) and React (Vite, Tailwind, Recharts, Leaflet). No machine learning.

> **Honest scope:** rainfall is not flooding. The indicator uses project-defined thresholds and one
> city-centre data point. It is an awareness tool, not a flood forecast or official warning.

## Run it on your computer (Windows)

You need Python 3.10+ and Node.js (you already have both). Open **two** terminals in this folder.

**Terminal 1 – backend**
```
run_backend.bat
```
(or manually: `cd backend`, `python -m venv .venv`, `.venv\Scripts\activate`, `pip install -r requirements.txt`, `uvicorn app.main:app --reload`)
Check: http://localhost:8000/health shows `"status": "ok"`. API docs: http://localhost:8000/docs

**Terminal 2 – frontend**
```
run_frontend.bat
```
(or manually: `cd frontend`, `npm install`, `npm run dev`)
Open http://localhost:5173

Run the tests: `cd backend`, activate the venv, then `python -m pytest -q` (14 tests).

## Live data
The backend refreshes itself about every 30 minutes (free Open-Meteo APIs, no key):
saved CSV (2020 to 2025) + archive API (up to ~3 days ago) + forecast API `past_days` (last days) + `current` (live conditions).
It recalculates the 3-day / 7-day totals, so charts, summary and the risk indicator stay up to date. Today's unfinished day is never used.
If Open-Meteo cannot be reached, the site falls back to the CSV and shows an "Offline mode" badge.
Settings (optional env vars): `LIVE_DATA=false` to disable, `LIVE_CACHE_MINUTES=30`.
Check it: http://localhost:8000/api/weather/live

## Project layout
- `ml/download_weather.py` – downloads Open-Meteo history -> `data/raw/`
- `ml/analyze_weather.py` – cleaning + EDA -> `data/processed/`, `docs/*.png`
- `ml/build_features.py` – rolling 3-day / 7-day totals -> `data/processed/pune_features.csv`
- `backend/app/services/risk_service.py` – the risk rules; thresholds live in `backend/app/core/config.py`
- `backend/app/services/advisory_service.py` – safety advice (separate from calculations)
- `frontend/src/pages/` – Dashboard, Analytics, Risk Map, Advisories, About

To refresh the data pipeline: `python ml/download_weather.py`, `python ml/analyze_weather.py`, `python ml/build_features.py`
(run from the project root with your root `.venv` active).

## Risk rules
| Level | Daily | 3-day | 7-day |
|---|---|---|---|
| Moderate | ≥ 35 mm | ≥ 60 mm | ≥ 100 mm |
| High | ≥ 64.5 mm | ≥ 100 mm | ≥ 150 mm |

If **any** measure reaches a level, that level is assigned (highest wins). Missing values are never treated as zero.
These are project-defined values, not validated flood boundaries.

## API
`GET /health`, `/api/weather/current`, `/api/weather/history?start=&end=`, `/api/rainfall/summary`,
`/api/rainfall/trends?granularity=daily|monthly|annual`, `/api/areas`, `/api/areas/{id}`,
`/api/risk/assessment?date=YYYY-MM-DD`, `/api/advisories`. Full interactive docs at `/docs`.

## Deploy
**Backend (Render, free web service)** – connect the GitHub repo.
Root directory: `backend` · Build: `pip install -r requirements.txt` · Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
Env var: `CORS_ORIGINS` = your Vercel URL (no trailing slash). The CSV files in `data/processed/` must be committed.
Check `https://YOUR-API.onrender.com/health`. Free instances sleep; the first request can take ~1 minute.

**Frontend (Vercel)** – import the repo, Root directory: `frontend`, framework Vite.
Env var: `VITE_API_BASE_URL` = your Render URL (no trailing slash). Redeploy after setting it.

## Limitations
Single city-centre point · values are model-based Open-Meteo estimates, not IMD gauge readings · approximate marker coordinates ·
thresholds not validated against Pune flood incidents · no drainage, terrain or official-warning data.

## Future scope
Recent-data downloader, IMD warnings, ward boundaries, elevation/drainage layers, validated model only if real incident labels are found.
