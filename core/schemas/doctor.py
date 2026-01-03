from pydantic import BaseModel

class DoctorRead(BaseModel):
    id: int
    name: str
    specialty: str

    class Config:
        from_attributes = True