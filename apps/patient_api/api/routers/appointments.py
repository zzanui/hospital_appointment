from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.models import Appointment
from core.db import get_db
from core.schemas import AppointmentCreate, AppointmentRead
from core.business.appointments import create_appointment
from apps.patient_api.dependencies import get_current_patient_id

router = APIRouter(prefix="/appointments", tags=["appointments"])
"""
3-3. 예약 생성
기능: 새로운 예약을 생성합니다.

요구사항:

중복 예약 방지 로직 구현 (동일 의사에게 동일 시간대 중복 불가)
병원 시간대별 최대 인원수 제한 검증
초진/재진 자동 판단 및 저장
시간대 검증 규칙:

예약 시작 시간부터 종료 시간까지 걸치는 모든 30분 슬롯을 확인
모든 해당 슬롯에 수용 인원 여유가 있어야 예약 가능
예시: 10:1510:45 예약(30분)은 10:0010:30, 10:30~11:00 슬롯 모두 확인 필요
"""

@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_new_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    try:
        appt = create_appointment(
            db,
            patient_name=payload.patient_name,
            patient_phone=payload.patient_phone,
            doctor_id=payload.doctor_id,
            treatment_id=payload.treatment_id,
            start_dt=payload.start_datetime,
            memo=payload.memo,
        )
        return appt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
"""
3-4. 예약 조회
기능: 환자 본인의 예약 목록을 조회합니다.
요구사항: 본인의 예약만 조회 가능
"""
@router.get("", response_model=list[AppointmentRead])
def list_my_appointments(
    db: Session = Depends(get_db),
    patiend_id: int = Depends(get_current_patient_id),
):
    """
    GET /api/v1/patient/appointments
    """
    appts = (
        db.query(Appointment)
        .filter(Appointment.patient_id == patiend_id)
        .order_by(Appointment.start_datetime.desc())
        .all()
    )
    return appts

"""
3-5. 예약 취소
기능: 예약을 취소 상태로 변경합니다.
"""
@router.patch("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    patient_id: int = Depends(get_current_patient_id),
):
    """
    PATCH /api/v1/patient/appointments/{appointment_id}/cancel
    """
    appt = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .filter(Appointment.patient_id == patient_id)
        .first()
    )
    
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if appt.status == "canceled":
        return appt

    # completed 취소 금지 등 정책은 여기서 추가 가능
    appt.status = "canceled"
    db.commit()
    db.refresh(appt)
    return appt