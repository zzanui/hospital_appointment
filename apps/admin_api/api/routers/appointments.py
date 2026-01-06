from datetime import date, datetime, time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.db import get_db
from core.models import Appointment
from core.schemas.appointment import AppointmentRead
from core.schemas.admin_appointment import AppointmentStatusUpdate

router = APIRouter(prefix="/appointments", tags=["appointments"])

_ALLOWED_NEXT = {
    "pending": {"confirmed", "canceled"},
    "confirmed": {"completed", "canceled"},
    "completed": set(),
    "canceled": set(),
}

_VALID_STATUS = {"pending", "confirmed", "completed", "canceled"}

"""
4-4. 전체 예약 조회
기능: 모든 예약을 조회합니다.
요구사항: 날짜, 의사, 상태 등 다양한 조건으로 필터링 가능
"""
@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    db: Session = Depends(get_db),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    doctor_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    patient_id: int | None = Query(default=None),
    treatment_id: int | None = Query(default=None),
):
    query = db.query(Appointment)
    # 필터링
    if doctor_id is not None:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id is not None:
        query = query.filter(Appointment.patient_id == patient_id)
    if treatment_id is not None:
        query = query.filter(Appointment.treatment_id == treatment_id)
    if status is not None:
        if status not in _VALID_STATUS:
            raise HTTPException(400, "Invalid status filter")
        query = query.filter(Appointment.status == status)

    if date_from is not None:
        query = query.filter(Appointment.start_datetime >= datetime.combine(date_from, time.min))
    if date_to is not None:
        # inclusive 느낌을 주려면 time.max 사용
        query = query.filter(Appointment.start_datetime <= datetime.combine(date_to, time.max))

    return query.order_by(Appointment.start_datetime.desc()).all()

"""
4-5. 예약 상태 수정
기능: 예약의 상태를 변경합니다.
가능한 상태: 예약대기 → 확정 → 완료 또는 취소
"""
@router.patch("/{appointment_id}/status", response_model=AppointmentRead)
def update_appointment_status(
    appointment_id: int,
    payload: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
):  
    #변경사항이 있는내용
    appt = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(404, "Appointment not found")

    new_status = payload.status
    if new_status not in _VALID_STATUS:
        raise HTTPException(400, "Invalid status")

    if new_status == appt.status:
        return appt  # 멱등 처리

    allowed = _ALLOWED_NEXT.get(appt.status, set())
    if new_status not in allowed:
        raise HTTPException(400, f"Invalid transition: {appt.status} -> {new_status}")

    appt.status = new_status
    db.commit()
    db.refresh(appt)
    return appt
