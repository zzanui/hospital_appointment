from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.db import get_db
from core.schemas.auth import PatientLoginRequest, PatientLoginResponse
from core.business.patient_auth import issue_patient_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/patient/login", response_model=PatientLoginResponse)
def login(payload: PatientLoginRequest, db: Session = Depends(get_db)):
    try:
        token = issue_patient_token(db, patient_phone=payload.phone_number, patient_name=payload.name)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=404, detail="Patient not found")
