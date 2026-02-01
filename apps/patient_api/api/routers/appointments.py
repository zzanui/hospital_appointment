from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from common.logging_utils import TRACE_ID, setup_json_logger
from core.db import get_db
from core.models import Appointment, Job, OutboxEvent
from core.schemas import AppointmentCreate, AppointmentRead, JobAccepted
from apps.patient_api.dependencies import get_current_patient_id

logger = setup_json_logger("patient_api")

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=JobAccepted, status_code=status.HTTP_202_ACCEPTED)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db), patient_id: int = Depends(get_current_patient_id)):
    """예약 생성 요청을 비동기 Job으로 접수한다.

    - 응답은 202 + job_id
    - 실제 예약 확정은 worker가 outbox_events를 처리하면서 수행

    기존 동기(201) 생성 엔드포인트를 제거하고, 이 엔드포인트를 단일 진입점으로 고정한다.
    """

    job_id = str(uuid.uuid4())
    trace_id = TRACE_ID.get()

    logger.info(
        "appointment requested",
        extra={
            "event": "appointment.requested",
            "job_id": job_id,
            "doctor_id": payload.doctor_id,
        },
    )

    try:
        db.begin()
        db.add(Job(id=job_id, status="QUEUED", result=None))
        db.add(
            OutboxEvent(
                event_type="appointment.requested",
                topic="appointment.requested",
                key=job_id,
                payload={
                    "job_id": job_id,
                    "trace_id": trace_id,
                    "patient_id": patient_id,
                    "patient_name": payload.patient_name,
                    "patient_phone": payload.patient_phone,
                    "doctor_id": payload.doctor_id,
                    "treatment_id": payload.treatment_id,
                    "start_datetime": payload.start_datetime.isoformat(),
                    "memo": payload.memo,
                },
                status="PENDING",
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return JobAccepted(job_id=job_id)


@router.get("", response_model=list[AppointmentRead])
def list_my_appointments(
    db: Session = Depends(get_db),
    patient_id: int = Depends(get_current_patient_id),
):
    """환자 본인의 예약 목록"""

    appts = (
        db.query(Appointment)
        .filter(Appointment.patient_id == patient_id)
        .order_by(Appointment.start_datetime.desc())
        .all()
    )
    return appts


@router.patch("/{appointment_id}/cancel", response_model=AppointmentRead)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    patient_id: int = Depends(get_current_patient_id),
):
    """예약 취소"""

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

    appt.status = "canceled"
    db.commit()
    db.refresh(appt)
    return appt
