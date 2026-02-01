from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

from common.logging_utils import TRACE_ID, now_ms, setup_json_logger
from core.db import init_db

logger = setup_json_logger("patient_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 테이블 생성 (개발 편의)
    init_db()
    yield
    logger.info("patient_api shutdown", extra={"event": "app.shutdown"})


app = FastAPI(title="Derm Clinic - Patient API", version="0.3.0", lifespan=lifespan)

# Routers
from apps.patient_api.api.routers.doctor import router as doctors_router
from apps.patient_api.api.routers.availability import router as availability_router
from apps.patient_api.api.routers.appointments import router as appointments_router
from apps.patient_api.api.routers.auth import router as auth_router
from apps.patient_api.api.routers.jobs import router as jobs_router

app.include_router(doctors_router, prefix="/api/v1/patient")
app.include_router(availability_router, prefix="/api/v1/patient")
app.include_router(appointments_router, prefix="/api/v1/patient")  # 예약 생성은 202 job 방식 단일화
app.include_router(jobs_router, prefix="/api/v1/patient")  # job 조회
app.include_router(auth_router, prefix="/api/v1/patient")


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
