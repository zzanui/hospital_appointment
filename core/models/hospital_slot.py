from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Time
from core.db import Base
"""
2-3. 병원 시간대별 인원 설정 (HospitalSlot)
필수 필드: 시간대_시작, 시간대_종료(30분 단위), 최대_인원수
설명: 병원 전체의 시간대별 동시 수용 가능 인원. 모든 날짜에 동일하게 적용됩니다.
예시: 시간대_시작: 10:00, 시간대_종료: 10:30, 최대_인원수: 3
"""
class HospitalSlot(Base):
    __tablename__ = "hospital_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    start_time: Mapped[Time] = mapped_column(Time, nullable=False)  
    end_time: Mapped[Time] = mapped_column(Time, nullable=False)    
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=False)

    