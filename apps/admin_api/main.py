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

app = FastAPI(title="Derm Clinic - Admin API", version="0.1.0", lifespan=lifespan)

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

