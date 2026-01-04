from datetime import date, datetime, time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from core.db import get_db
from core.models import Appointment, HospitalSlot
from core.schemas.stats import AdminStatsResponse, StatusCount, DailyCount, TimeSlotCount, VisitTypeRatio

router = APIRouter(prefix="/stats", tags=["stats"])

"""
4-6. 예약 통계
기능: 다양한 통계 정보를 제공합니다.
필수 통계 항목:
상태별 예약 건수
일별 예약 현황
시간대별 예약 현황
초진/재진 비율
"""

@router.get("", response_model=AdminStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
):
    q = db.query(Appointment)

    if date_from is not None:
        q = q.filter(Appointment.start_datetime >= datetime.combine(date_from, time.min))
    if date_to is not None:
        q = q.filter(Appointment.start_datetime <= datetime.combine(date_to, time.max))

    # 1) 상태별 예약 건수
    status_rows = (
        q.with_entities(Appointment.status, func.count(Appointment.id))
        .group_by(Appointment.status)
        .all()
    )
    status_counts = [StatusCount(status=s, count=c) for s, c in status_rows]

    # 2) 일별 예약 현황
    daily_rows = (
        q.with_entities(func.date(Appointment.start_datetime).label("d"), func.count(Appointment.id))
        .group_by("d")
        .order_by("d")
        .all()
    )
    daily_counts = [DailyCount(date=str(d), count=c) for d, c in daily_rows]

    # 3) 시간대별 예약 현황 (HospitalSlot 30분 슬롯 기준, overlap 카운트)
    slots = db.query(HospitalSlot).order_by(HospitalSlot.start_time.asc()).all()
    time_slot_counts: list[TimeSlotCount] = []
    if slots:
        appts = q.filter(Appointment.status != "canceled").all()
        for s in slots:
            key = f"{s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')}"
            used = 0
            for a in appts:
                # 예약 날짜 기준으로 슬롯 datetime 구성
                slot_start = datetime.combine(a.start_datetime.date(), s.start_time)
                slot_end = datetime.combine(a.start_datetime.date(), s.end_time)
                if a.start_datetime < slot_end and slot_start < a.end_datetime:
                    used += 1
            time_slot_counts.append(TimeSlotCount(time_slot=key, count=used))

    # 4) 초진/재진 비율
    vt_rows = (
        q.with_entities(Appointment.visit_type, func.count(Appointment.id))
        .group_by(Appointment.visit_type)
        .all()
    )
    vt_map = {vt: c for vt, c in vt_rows}
    visit_type_ratio = VisitTypeRatio(
        first=int(vt_map.get("first", 0)),
        followup=int(vt_map.get("followup", 0)),
    )

    return AdminStatsResponse(
        status_counts=status_counts,
        daily_counts=daily_counts,
        time_slot_counts=time_slot_counts,
        visit_type_ratio=visit_type_ratio,
    )
