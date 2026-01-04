from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, String, Text
from core.db import Base
"""
2-2. 진료 항목 (Treatment)
필수 필드: 시술명, 소요시간(30분 단위), 가격, 설명
설명: 병원에서 제공하는 진료/시술 메뉴
"""
class Treatment(Base):
    __tablename__ = "treatments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)