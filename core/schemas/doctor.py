from pydantic import BaseModel, ConfigDict
"""
3-1. 의사 목록 조회
기능: 병원의 전체 의사 목록을 조회합니다.
옵션: 진료과로 필터링 가능
"""
class DoctorRead(BaseModel):
    id: int
    name: str
    department: str

    model_config = ConfigDict(from_attributes=True)

class DoctorCreate(BaseModel):
    name: str
    department: str

class DoctorUpdate(BaseModel):
    name: str | None = None
    department: str | None = None