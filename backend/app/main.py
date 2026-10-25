import logging
import threading

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import CORS_ORIGINS
from app.services import data_service

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="RainSafe Pune API", version="1.0.0",
              description="Historical rainfall analytics and a rule-based rainfall concern indicator for Pune.")

@app.on_event("startup")
def start_warm_up():
    threading.Thread(target=data_service.warm_up, daemon=True).start()


app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS,
                   allow_methods=["GET"], allow_headers=["*"])


@app.exception_handler(data_service.DataUnavailable)
async def data_missing(request: Request, exc: data_service.DataUnavailable):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.get("/")
def root():
    return {"app": "RainSafe Pune API", "status": "running", "docs": "/docs"}


@app.get("/health")
def health():
    ok = data_service.data_available()
    return {"status": "ok" if ok else "degraded", "data_file_available": ok,
            "data_status": data_service._cache["status"] or "not loaded yet"}


app.include_router(router)
