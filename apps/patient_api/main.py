from fastapi import FastAPI

from core.db import init_db
from apps.patient_api.api.routers.doctor import router as doctors_router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시
    init_db()
    yield
    # 앱 종료 시
    print("🛑 Patient API shutdown")

app = FastAPI(title="Derm Clinic - Patient API", version="0.1.0", lifespan=lifespan)

app.include_router(doctors_router, prefix="/api/v1/patient")

@app.get("/ping")
def ping():
    return {"service": "patient_api", "message": "pong"}



