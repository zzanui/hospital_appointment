from fastapi import FastAPI

from core.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시
    init_db()
    yield
    # 앱 종료 시
    print("🛑 Patient API shutdown")

app = FastAPI(title="Derm Clinic - Patient API", version="0.1.0", lifespan=lifespan)

from apps.patient_api.api.routers.doctor import router as doctors_router
from apps.patient_api.api.routers.availability import router as availability_router
from apps.patient_api.api.routers.appointments import router as appointments_router
from apps.patient_api.api.routers.auth import router as auth_router
from apps.patient_api.api.routers.appointments import router as appointments_router

app.include_router(doctors_router, prefix="/api/v1/patient")
app.include_router(availability_router, prefix="/api/v1/patient")
app.include_router(appointments_router, prefix="/api/v1/patient")
app.include_router(auth_router, prefix="/api/v1/patient")
app.include_router(appointments_router, prefix="/api/v1/patient")


