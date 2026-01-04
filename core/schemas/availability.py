from datetime import date
from pydantic import BaseModel
from typing import List
"""
3-2. 예약 가능 시간 조회
기능: 특정 의사의 예약 가능한 시간대를 조회합니다.
요구사항:
    병원 운영 시간 내의 예약 가능 시간대만 노출
    선택한 날짜 기준으로 15분 간격 시간대 제공
    이미 예약된 시간, 병원 수용 인원 초과 시간은 제외
"""
class AvailabilityResponse(BaseModel):
    doctor_id: int
    treatment_id: int
    dete: date
    available_start_times: List[str]