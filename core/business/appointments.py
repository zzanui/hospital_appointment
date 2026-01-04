from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from core.models import Doctor, Treatment, Appointment, HospitalSlot, Patient
"""
요구사항:

중복 예약 방지 로직 구현 (동일 의사에게 동일 시간대 중복 불가)
병원 시간대별 최대 인원수 제한 검증
초진/재진 자동 판단 및 저장
시간대 검증 규칙:

예약 시작 시간부터 종료 시간까지 걸치는 모든 30분 슬롯을 확인
모든 해당 슬롯에 수용 인원 여유가 있어야 예약 가능
예시: 10:1510:45 예약(30분)은 10:0010:30, 10:30~11:00 슬롯 모두 확인 필요
"""

#추후에 환경변수로 변경
OPEN_TIME = time(9, 0)   # 병원 운영 시작 시간
CLOSE_TIME = time(18, 0) # 병원 운영 종료 시간
LUNCH_START = time(12, 0) # 점심시간 시작
LUNCH_END = time(13, 0)   # 점심시간 종료

START_STEP_MINUTES = 15  # 예약 간격

#datetime으로 변환
def _dt(d: date, t: time) -> datetime:
    return datetime.combine(d, t)

#예약 가능 시간대(오픈시간 < 점심시간 and 점심시간 < 닫는시간)
def _overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    return start1 < end2 and start2 < end1

def _is_multiple_of_30(x: int) -> bool:
    return x % 30 == 0

def _is_15min_grid(dt: datetime) -> bool:
    return dt.minute in (0, 15, 30, 45) and dt.second == 0 and dt.microsecond == 0

def _in_operating_hours(start_dt: datetime, end_dt: datetime) -> bool:
    d = start_dt.date()
    day_open = _dt(d, OPEN_TIME)
    day_close = _dt(d, CLOSE_TIME)
    if start_dt < day_open or end_dt > day_close:
        return False
    
    lunch_start = _dt(d, LUNCH_START)
    lunch_end = _dt(d, LUNCH_END)
    if _overlap(start_dt, end_dt, lunch_start, lunch_end):
        return False
    
    return True

def _check_capacity(db: Session, start_dt: datetime, end_dt: datetime) -> bool:
    """
    예약 구간이 겹치는 모든 HospitalSlot(30분)에 대해
    해당 slot과 겹치는 전체 예약 수 < max_capacity 이어야 함.
    """

    slots = db.query(HospitalSlot).all()
    if not slots:
        # 개발 초기에 slot 미구성 시 무제한 처리(테스트시 db에 적제하기)
        return True
    
    target_date = start_dt.date()
    day_open = _dt(target_date, OPEN_TIME)
    day_close = _dt(target_date, CLOSE_TIME)
    
    appts_all = (
        db.query(Appointment)
        .filter(Appointment.start_datetime < day_close)
        .filter(Appointment.end_datetime > day_open)
        .filter(Appointment.status != "canceled")
        .all()
    )

    for s in slots:
        slot_start_dt = _dt(target_date, s.start_time)
        slot_end_dt = _dt(target_date, s.end_time)

        if not _overlap(start_dt, end_dt, slot_start_dt, slot_end_dt):
            continue

        used = 0
        for a in appts_all:
            if _overlap(a.start_datetime, a.end_datetime, slot_start_dt, slot_end_dt):
                used += 1
        
        if used >= s.max_capacity:
            return False
    return True

def _check_doctor_conflict(db: Session, doctor_id: int, start_dt: datetime, end_dt: datetime) -> bool:
    """
    해당 의사의 예약 중 겹치는 예약이 없어야 함.
    """
    conflict = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .filter(Appointment.status != "canceled")
        .filter(Appointment.start_datetime < end_dt)
        .filter(Appointment.end_datetime > start_dt)
        .first()
    )
    return conflict is None

def _get_or_create_patient(db: Session, name: str, phone: str) -> Patient:
    patient = db.query(Patient).filter(Patient.phone == phone).one_or_none()
    if patient:
        return patient
    
    patient = Patient(name=name, phone=phone)
    db.add(patient)
    db.flush()  # id 확보
    return patient

def _determine_first_visit(db: Session, patient_id: int) -> str:
    """
    초진/재진 자동 판단:
    - 해당 patient로 '취소가 아닌 예약'이 과거에 하나라도 있으면 followup(재진)
    - 아니면 first(초진)
    """
    exists = (
        db.query(Appointment.id)
        .filter(Appointment.patient_id == patient_id)
        .filter(Appointment.status != "canceled")
        .limit(1)
        .first()
    )
    return "followup" if exists else "first"

def create_appointment( #// 404에러 처리예정
        db: Session,
        *,  # 키워드인자 전용
        patient_name: str,
        patient_phone: str,
        doctor_id: int,
        treatment_id: int,
        start_dt: datetime,
        memo: str,
) -> Appointment:
    # 1. 시작시간 15분 그리드 검증
    if not _is_15min_grid(start_dt):
        # 15분 그리드 아님 
        raise ValueError("start_datetime must be on a 15-minute grid (00/15/30/45).")
    
    #2. doctor/treatment 존재 검증
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise ValueError("Doctor not found.")
    
    treatment = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not treatment:
        raise ValueError("Treatment not found.")
    
    if not _is_multiple_of_30(treatment.duration_minutes):
        raise ValueError("Treatment duration must be a multiple of 30 minutes.")
    
    end_dt = start_dt + timedelta(minutes=treatment.duration_minutes)

    #3. 영업시간, 점심시간 검증
    if not _in_operating_hours(start_dt, end_dt):
        raise ValueError("Appointment time is outside operating hours or overlaps with lunch break.")
    
    #4. 의사 중복진료 검증
    if not _check_doctor_conflict(db, doctor_id, start_dt, end_dt):
        raise ValueError("Doctor has a conflicting appointment.")
    
    #5. 병원 수용인원 검증
    if not _check_capacity(db, start_dt, end_dt):
        raise ValueError("Hospital capacity exceeded for the requested time.")
    
    #6. 환자 조회/생성
    patient = _get_or_create_patient(db, patient_name, patient_phone)

    #7. 초진/재진 판단
    is_first_visit = _determine_first_visit(db, patient.id)

    #8. 예약 생성 
    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        treatment_id=treatment_id,
        start_datetime=start_dt,
        end_datetime=end_dt,
        status="pending",
        is_first_visit=is_first_visit,
        memo=memo,
    )
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt