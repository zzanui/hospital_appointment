from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, ForeignKey, String, Boolean, Integer, func
from core.db import Base

#환자인증을위해 생성된 토큰모델
class PatientSessionToken(Base):
    __tablename__ = "patient_session_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    #인증토큰
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    #토큰활성화 여부
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    #만료시간
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    