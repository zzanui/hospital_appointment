from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobAccepted(BaseModel):
    """비동기 작업 접수(HTTP 202) 응답."""

    job_id: str


class AppointmentCreate(BaseModel):
    patient_name: str = Field(..., min_length=1)
    patient_phone: str = Field(..., min_length=5)
    doctor_id: int
    treatment_id: int
    start_datetime: datetime
    memo: str = ""


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    treatment_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    is_first_visit: str
    memo: str

    model_config = ConfigDict(from_attributes=True)
