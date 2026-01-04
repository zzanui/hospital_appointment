from pydantic import BaseModel

class AppointmentStatusUpdate(BaseModel):
    status: str
