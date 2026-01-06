from datetime import time
from pydantic import BaseModel, Field, ConfigDict

class HospitalSlotCreate(BaseModel):
    start_time: time = Field(..., description="시간대 시작 (30분 단위)")
    end_time: time = Field(..., description="시간대 종료 (30분 단위)")
    max_capacity: int = Field(..., description="최대 인원수")

class HospitalSlotRead(BaseModel):
    id: int
    start_time: time
    end_time: time
    max_capacity: int

    model_config = ConfigDict(from_attributes=True)

class HospitalSlotUpdate(BaseModel):
    start_time: time | None = None
    end_time: time | None = None
    max_capacity: int | None = None