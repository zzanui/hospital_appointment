from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.db import get_db
from core.models.doctor import Doctor
from core.schemas.doctor import DoctorCreate, DoctorRead, DoctorUpdate

router = APIRouter(prefix="/doctors", tags=["doctors"])
"""
4-1. 의사 정보 CRUD
의사 정보의 생성(Create), 조회(Read), 수정(Update), 삭제(Delete) 기능
"""
@router.post("", response_model=DoctorRead, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    new_doctor = Doctor(**payload.model_dump())
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    return new_doctor

@router.get("", response_model=list[DoctorRead])
def list_doctors(db: Session = Depends(get_db)):
    doctors = db.query(Doctor).order_by(Doctor.id.desc()).all()
    return doctors

@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    return doctor

@router.put("/{doctor_id}", response_model=DoctorRead)
def update_doctor(doctor_id: int, payload: DoctorUpdate, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    return doctor

@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doctor not found")
    
    db.delete(doctor)
    db.commit()
    return