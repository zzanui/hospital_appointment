from datetime import time
from pydantic import BaseModel, Field

class HospitalSlotCreate(BaseModel):
    starttime: time = Field(..., description="시간대 시작 (30분 단위)")
    endtime: time = Field(..., description="시간대 종료 (30분 단위)")
    maxcapacity: int = Field(..., description="최대 인원수")

class HospitalSlotRead(BaseModel):
    id: int
    starttime: time
    endtime: time
    maxcapacity: int

    class Config:
        from_attributes = True

class HospitalSlotUpdate(BaseModel):
    starttime: time | None = None
    endtime: time | None = None
    maxcapacity: int | None = None