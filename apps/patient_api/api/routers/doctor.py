from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.db import get_db
from core.models.doctor import Doctor
from core.schemas import DoctorRead

router = APIRouter(prefix="/doctors", tags=["doctors"])

"""
3-1. 의사 목록 조회
기능: 병원의 전체 의사 목록을 조회합니다.
옵션: 진료과로 필터링 가능
"""
@router.get("/", response_model=List[DoctorRead])
def list_doctors(
    specialty: Optional[str] = Query(None, description="진료과로 필터링"), 
    db: Session = Depends(get_db),
    ):
    
    """
    GET /api/v1/patient/doctors
    GET /api/v1/patient/doctors?department=피부과
    """
  
    if specialty:
        query = db.query(Doctor).filter(Doctor.specialty == specialty)
    else:
        query = db.query(Doctor)

    return query.all()
