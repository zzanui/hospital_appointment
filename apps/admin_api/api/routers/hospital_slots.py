from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core.db import get_db
from core.models import HospitalSlot
from core.schemas.hospital_slot import HospitalSlotCreate, HospitalSlotUpdate, HospitalSlotRead

router = APIRouter(prefix="/hospital-slots", tags=["hospital-slots"])

"""
4-2. 병원 시간대별 진료 인원 관리
기능: HospitalSlot 데이터를 관리하는 기능
구현 방법은 자유롭게 선택 가능합니다:
CRUD 엔드포인트로 구현
설정용 단일 엔드포인트로 구현
기타 적절한 방법
예시: 10:00~10:30 시간대에 최대 3명으로 설정/수정
"""
def _validate_slot(payload: HospitalSlotCreate | HospitalSlotUpdate) -> None:
    # start < end
    if payload.start_time is not None and payload.end_time is not None:
        if payload.start_time >= payload.end_time:
            raise HTTPException(400, "start_time must be earlier than end_time")
    # 30분 단위 강제(권장)
    def ok_30(t):
        return t.minute in (0, 30) and t.second == 0 and t.microsecond == 0
    if getattr(payload, "start_time", None) is not None and not ok_30(payload.start_time):
        raise HTTPException(400, "start_time must be on 30-minute boundary")
    if getattr(payload, "end_time", None) is not None and not ok_30(payload.end_time):
        raise HTTPException(400, "end_time must be on 30-minute boundary")


@router.post("", response_model=HospitalSlotRead, status_code=status.HTTP_201_CREATED)
def create_slot(payload: HospitalSlotCreate, db: Session = Depends(get_db)):
    _validate_slot(payload)

    # 동일 시간대 중복 방지(권장)
    exists = (
        db.query(HospitalSlot.id)
        .filter(and_(HospitalSlot.start_time == payload.start_time, HospitalSlot.end_time == payload.end_time))
        .first()
    )
    if exists:
        raise HTTPException(409, "Slot already exists for the same time range")

    s = HospitalSlot(**payload.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("", response_model=list[HospitalSlotRead])
def list_slots(db: Session = Depends(get_db)):
    return db.query(HospitalSlot).order_by(HospitalSlot.start_time.asc()).all()


@router.put("/{slot_id}", response_model=HospitalSlotRead)
def update_slot(slot_id: int, payload: HospitalSlotUpdate, db: Session = Depends(get_db)):
    s = db.query(HospitalSlot).filter(HospitalSlot.id == slot_id).first()
    if not s:
        raise HTTPException(404, "Slot not found")

    _validate_slot(payload)

    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)

    db.commit()
    db.refresh(s)
    return s


@router.delete("/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slot(slot_id: int, db: Session = Depends(get_db)):
    s = db.query(HospitalSlot).filter(HospitalSlot.id == slot_id).first()
    if not s:
        raise HTTPException(404, "Slot not found")
    db.delete(s)
    db.commit()
    return None
