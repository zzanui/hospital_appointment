from pydantic import BaseModel
from typing import List

class StatusCount(BaseModel):
    status: str
    count: int

class DailyCount(BaseModel):
    date: str
    count: int

class TimeSlotCount(BaseModel):
    time_slot: str
    count: int

class VisitTypeRatio(BaseModel):
    first: int
    followup: int

class AdminStatsResponse(BaseModel):
    status_counts: List[StatusCount]
    daily_counts: List[DailyCount]
    time_slot_counts: List[TimeSlotCount]
    visit_type_ratio: VisitTypeRatio
