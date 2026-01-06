from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, String
from core.db import Base

"""
2-1. 의사 정보 (Doctor)
필수 필드: 이름, 진료과
설명: 병원에 근무하는 의사의 기본 정보
"""
class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100),nullable=False)
