from datetime import date, time, datetime, timedelta
from sqlalchemy.orm import Session

from core.models import Doctor, Treatment, Appointment, HospitalSlot
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

def get_available_start_times(db: Session, doctor_id: int, treatment_id: int, target_date: date) -> list[str]:
    doctor = (db.query(Doctor).filter(Doctor.id == doctor_id).first())
    if not doctor:
        return []
    
    treatment = (db.query(Treatment).filter(Treatment.id == treatment_id).first())
    if not treatment:
        return []

    if not _is_multiple_of_30(treatment.duration_minutes):
        #시술 소요시간이 30분 단위가 아님
        return []
    #시술 소요시간
    duration = timedelta(minutes=treatment.duration_minutes)

    day_open = _dt(target_date, OPEN_TIME)
    day_close = _dt(target_date, CLOSE_TIME)
    lunch_start = _dt(target_date, LUNCH_START)
    lunch_end = _dt(target_date, LUNCH_END)

    #해당 의사의 해당 날짜 예약된 모든 예약 조회
    appts_doctor = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == doctor_id)
        .filter(Appointment.start_datetime < day_close)
        .filter(Appointment.end_datetime > day_open)
        .filter(Appointment.status != "canceled")
        .all()
    )

    #병원 전체 예약 조회 (병원 수용 인원 초과 체크용)
    appts_all = (
        db.query(Appointment)
        .filter(Appointment.start_datetime < day_close)
        .filter(Appointment.end_datetime > day_open)
        .filter(Appointment.status != "canceled")
        .all()
    )

    slots = db.query(HospitalSlot).all()
    # 슬롯이 비어있으면 capacity 제한을 적용할 수 없으니 “무제한”으로 처리(개발 초기 편의)
    # 테스트시 반드시 slot seed설정
    enforce_capacity = len(slots) > 0

    candidates: list[datetime] = []
    cur = day_open
    step = timedelta(minutes=START_STEP_MINUTES)

    # 영업시간 내 모든 예약 시간대 생성
    while cur + duration <= day_close:
        candidates.append(cur)
        cur += step

    #검증
    availale: list[str] = []
    for start_dt in candidates:
        end_dt = start_dt + duration

        #점심시간 겹침 체크
        if _overlap(start_dt, end_dt, lunch_start, lunch_end):
            continue

        #이미 예약된 시간 체크
        if any(_overlap(start_dt, end_dt, appt.start_datetime, appt.end_datetime) for appt in appts_doctor):
            continue
        
        #병원 capacity: 예약구간이 걸치는 모든 30분 HospitalSlot이 여유 있어야 함
        if enforce_capacity and not _check_capacity(db, appts_all, slots, start_dt, end_dt):
            continue

        availale.append(start_dt.strftime("%H:%M"))
    return availale

def _check_capacity(
        db: Session,
        target_date: date,
        start_dt: datetime,
        end_dt: datetime,
        slots: list[HospitalSlot],
        appts_all: list[Appointment],
) -> bool:
    #HospitalSlot은 30분 단위로 정의되므로 예약 구간이 걸치는 모든 30분 HospitalSlot이 여유 있어야 함
    #예약정원이 다 찼는지 확인
    for s in slots:
        slot_start_dt = _dt(target_date, s.start_time)
        slot_end_dt = _dt(target_date, s.end_time)

        if not _overlap(start_dt, end_dt, slot_start_dt, slot_end_dt):
            continue

        #이 슬롯에 예약된 전체 예약 수 계산
        used = 0
        for a in appts_all:
            if _overlap(a.start_datetime, a.end_datetime, slot_start_dt, slot_end_dt):
                used += 1
        
        if used >= s.max_capacity:
            return False
        
    return True