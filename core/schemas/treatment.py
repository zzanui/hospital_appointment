from pydantic import BaseModel, Field

class TreatmentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., ge=30)  # 30분 단위
    price: int = Field(..., ge=0)
    description: str
    is_active: bool = True

class TreatmentUpdate(BaseModel):
    name: str | None = None
    duration_minutes: int | None = Field(default=None, ge=30)
    price: int | None = Field(default=None, ge=0)
    description: str | None = None
    is_active: bool | None = None

class TreatmentRead(BaseModel):
    id: int
    name: str
    duration_minutes: int
    price: int
    description: str
    is_active: bool
    class Config:
        from_attributes = True
