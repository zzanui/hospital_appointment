from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, String
from core.db import Base
"""
2-4. 환자 정보 (Patient)
필수 필드: 이름, 연락처
설명: 예약을 진행하는 환자의 기본 정보
"""
class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)