from datetime import datetime
from pydantic import BaseModel, Field

class AppointmentCreate(BaseModel):
    patient_name: str  = Field(..., min_length=1)
    patient_phone: str  = Field(..., min_length=5)
    doctor_id: int 
    treatment_id: int
    start_datetime: datetime
    memo: str = ""

class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    teatment_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    is_first_visit: str
    memo: str

    class Config:
        from_attributes = True