from pydantic import BaseModel
"""
3-1. 의사 목록 조회
기능: 병원의 전체 의사 목록을 조회합니다.
옵션: 진료과로 필터링 가능
"""
class DoctorRead(BaseModel):
    id: int
    name: str
    specialty: str

    class Config:
        from_attributes = True

class DoctorCreate(BaseModel):
    name: str
    specialty: str

class DoctorUpdate(BaseModel):
    name: str | None = None
    specialty: str | None = None