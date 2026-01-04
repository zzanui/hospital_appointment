from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Integer, DateTime, String, Text
from sqlalchemy import ForeignKey 
from core.db import Base
"""
2-5. 예약 정보 (Appointment)
필수 필드: 환자(FK), 의사(FK), 진료 항목(FK), 예약_시작일시, 상태, 초진/재진 구분, 메모
예약 상태: 예약대기, 확정, 완료, 취소
초진/재진: 예약 생성 시 자동 판단되어 저장
예약 종료 시간: 예약_시작일시 + 진료항목의 소요시간으로 계산됩니다. 별도 필드로 저장할지는 자유롭게 선택 가능합니다.
"""
class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(Integer ,ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id: Mapped[int] = mapped_column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    treatment_id: Mapped[int] = mapped_column(Integer, ForeignKey("treatments.id"), nullable=False, index=True)
    #예약시간은 좀 더 생각해보자
    start_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    end_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    is_first_visit: Mapped[str] = mapped_column(String(20), nullable=False)
    memo: Mapped[str] = mapped_column(Text, nullable=False, default="")
