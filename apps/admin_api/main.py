from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

from common.logging_utils import TRACE_ID, now_ms, setup_json_logger
from core.db import init_db

logger = setup_json_logger("admin_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    logger.info("admin_api shutdown", extra={"event": "app.shutdown"})


app = FastAPI(title="Derm Clinic - Admin API", version="0.2.0", lifespan=lifespan)

from apps.admin_api.api.routers.doctors import router as doctors_router
from apps.admin_api.api.routers.treatments import router as treatments_router
from apps.admin_api.api.routers.hospital_slots import router as hospital_slots_router
from apps.admin_api.api.routers.appointments import router as appointments_router
from apps.admin_api.api.routers.stats import router as stats_router

API_PREFIX = "/api/v1/admin"
app.include_router(doctors_router, prefix=API_PREFIX)
app.include_router(treatments_router, prefix=API_PREFIX)
app.include_router(hospital_slots_router, prefix=API_PREFIX)
app.include_router(appointments_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=API_PREFIX)


@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id") or str(uuid.uuid4())
    token = TRACE_ID.set(trace_id)
    start = now_ms()
    try:
        response: Response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
    finally:
        duration = now_ms() - start
        logger.info(
            "http request finished",
            extra={
                "event": "http.request.finished",
                "http_method": request.method,
                "http_path": request.url.path,
                "duration_ms": duration,
            },
        )
        TRACE_ID.reset(token)
