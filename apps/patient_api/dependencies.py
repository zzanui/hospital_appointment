from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from core.db import get_db
from core.models import PatientSessionToken

#Authorization Bearer 토큰 검증
bearer_scheme = HTTPBearer(auto_error=False)

def get_current_patient_id(
        creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: Session = Depends(get_db),
    ) -> int:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    token_str = creds.credentials
    token = (
        db.query(PatientSessionToken)
        .filter(PatientSessionToken.token == token_str)
        .filter(PatientSessionToken.is_active == True) 
        .first()
    )
    #토큰유효성 검사
    #토큰있는지 확인
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    #토큰만료시간 확인
    if token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    
    return token.patient_id
    
    

