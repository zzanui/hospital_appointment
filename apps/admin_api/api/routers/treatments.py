from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from core.models import Treatment
from core.schemas.treatment import TreatmentCreate, TreatmentUpdate, TreatmentRead

router = APIRouter(prefix="/treatments", tags=["treatments"])


def _validate_duration(minutes: int) -> None:
    if minutes % 30 != 0:
        raise HTTPException(400, "duration_minutes must be a multiple of 30")

"""
진료 항목 CRUD
진료 항목의 생성, 조회, 수정, 삭제 기능
"""
@router.post("", response_model=TreatmentRead, status_code=status.HTTP_201_CREATED)
def create_treatment(payload: TreatmentCreate, db: Session = Depends(get_db)):
    _validate_duration(payload.duration_minutes)
    t = Treatment(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("", response_model=list[TreatmentRead])
def list_treatments(db: Session = Depends(get_db)):
    return db.query(Treatment).order_by(Treatment.id.desc()).all()


@router.get("/{treatment_id}", response_model=TreatmentRead)
def get_treatment(treatment_id: int, db: Session = Depends(get_db)):
    t = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not t:
        raise HTTPException(404, "Treatment not found")
    return t


@router.put("/{treatment_id}", response_model=TreatmentRead)
def update_treatment(treatment_id: int, payload: TreatmentUpdate, db: Session = Depends(get_db)):
    t = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not t:
        raise HTTPException(404, "Treatment not found")

    data = payload.model_dump(exclude_unset=True)
    if "duration_minutes" in data:
        _validate_duration(data["duration_minutes"])

    for k, v in data.items():
        setattr(t, k, v)

    db.commit()
    db.refresh(t)
    return t


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment(treatment_id: int, db: Session = Depends(get_db)):
    t = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not t:
        raise HTTPException(404, "Treatment not found")
    db.delete(t)
    db.commit()
    return None
