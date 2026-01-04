from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from core.models import Patient, PatientSessionToken
from core.utils.tokens import generate_token
#토큰유효기간(7일)
TOKEN_TTL_DAYS = 7
#토근발급
def issue_patient_token(
        db: Session,
        patient_phone: str,
        patient_name: str | None = None
        ) -> PatientSessionToken:
    query = db.query(Patient).filter(Patient.phone == patient_phone)
    
    # 이름이 들어온 경우에만 추가 검증
    if patient_name is not None:
        query = query.filter(Patient.name == patient_name)

    patient = query.first()
    if not patient:
        # 여기까지도 "없으면 에러"로 처리 
        raise ValueError("Patient not found (phone/name mismatch)")

    token_str = generate_token(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=TOKEN_TTL_DAYS)

    token = PatientSessionToken(
        patient_id = patient.id,
        token=token_str,
        is_active=True,
        expires_at=expires_at.replace(tzinfo=None),
    )
    db.add(token)
    db.commit()
    return token_str

    