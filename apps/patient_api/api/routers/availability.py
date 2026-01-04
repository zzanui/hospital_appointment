from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.db import get_db
from core.schemas import AvailabilityResponse
from core.business.availability import get_available_start_times

router = APIRouter(prefix="/availability", tags=["availability"])
"""
3-2. 예약 가능 시간 조회
기능: 특정 의사의 예약 가능한 시간대를 조회합니다.
요구사항:
병원 운영 시간 내의 예약 가능 시간대만 노출
선택한 날짜 기준으로 15분 간격 시간대 제공
이미 예약된 시간, 병원 수용 인원 초과 시간은 제외
"""
@router.get("/{doctor_id}/availability", response_model=AvailabilityResponse)
def doctor_availability(
    doctor_id: int,
    date: date = Query(..., description="YYYY-MM-DD 형식의 날짜"),
    treatment_id: int = Query(..., description="시술 ID"),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/patient/availability/{doctor_id}/availability?date=2023-10-15&treatment_id=1
    """
    times = get_available_start_times(db, doctor_id, treatment_id, date)
    return AvailabilityResponse(
        doctor_id=doctor_id,
        treatment_id=treatment_id,
        dete=date,
        available_start_times=times,
    )