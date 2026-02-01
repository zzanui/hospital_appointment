from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from common.logging_utils import TRACE_ID, setup_json_logger
from core.db import get_sessionmaker
from core.models import Job, OutboxEvent
from core.business.appointments import create_appointment

logger = setup_json_logger("worker")

POLL_INTERVAL_SEC = float(os.getenv("WORKER_POLL_INTERVAL_SEC", "0.5"))
BATCH_SIZE = int(os.getenv("WORKER_BATCH_SIZE", "10"))
MAX_ATTEMPTS = int(os.getenv("WORKER_MAX_ATTEMPTS", "10"))


def _process_event(db: Session, event: OutboxEvent) -> None:
    payload = event.payload or {}
    job_id = payload.get("job_id") or event.key

    # trace_id를 worker 로깅 컨텍스트에 주입
    trace_token = TRACE_ID.set(payload.get("trace_id"))

    try:
        job = db.get(Job, job_id)
        if not job:
            # job이 없으면 이벤트만 실패 처리 (데이터 불일치)
            raise RuntimeError(f"job not found for job_id={job_id}")

        # idempotency: 이미 성공/실패한 job이면 이벤트만 PUBLISHED로 마킹하고 종료
        if job.status in ("SUCCEEDED", "FAILED"):
            event.status = "PUBLISHED"
            event.published_at = datetime.now(timezone.utc)
            return

        job.status = "RUNNING"

        if event.event_type == "appointment.requested":
            appt = create_appointment(
                db,
                patient_name=payload["patient_name"],
                patient_phone=payload["patient_phone"],
                doctor_id=int(payload["doctor_id"]),
                treatment_id=int(payload["treatment_id"]),
                start_dt=datetime.fromisoformat(payload["start_datetime"]),
                memo=payload.get("memo") or "",
            )
            job.status = "SUCCEEDED"
            job.result = f"appointment_id={appt.id}"
            logger.info(
                "appointment created",
                extra={
                    "event": "appointment.created",
                    "job_id": job_id,
                    "appointment_id": appt.id,
                    "doctor_id": payload.get("doctor_id"),
                },
            )
        else:
            raise RuntimeError(f"unknown event_type={event.event_type}")

        event.status = "PUBLISHED"
        event.published_at = datetime.now(timezone.utc)
        event.last_error = None

    except Exception as e:
        logger.exception(
            "event processing failed",
            extra={"event": "outbox.process.failed", "job_id": job_id},
        )

        # Job은 실패 상태로 마킹
        job = db.get(Job, job_id)
        if job and job.status not in ("SUCCEEDED", "FAILED"):
            job.status = "FAILED"
            job.result = str(e)

        event.status = "FAILED"
        event.publish_attempts = (event.publish_attempts or 0) + 1
        event.last_error = str(e)

        # 너무 많이 실패하면 더 이상 재시도하지 않음(여기서는 FAILED 유지, 운영에서는 DEAD-LETTER로 이동)
        if event.publish_attempts >= MAX_ATTEMPTS:
            logger.error(
                "event exceeded max attempts",
                extra={"event": "outbox.max_attempts", "job_id": job_id},
            )

    finally:
        TRACE_ID.reset(trace_token)


def run() -> None:
    logger.info("worker started", extra={"event": "worker.started"})
    SessionLocal = get_sessionmaker()

    while True:
        db: Session = SessionLocal()
        try:
            # PENDING 먼저, 그 다음 FAILED(재시도)
            events = (
                db.query(OutboxEvent)
                .filter(
                    OutboxEvent.status.in_(["PENDING", "FAILED"]),
                    OutboxEvent.publish_attempts < MAX_ATTEMPTS,
                )
                .order_by(OutboxEvent.id.asc())
                .limit(BATCH_SIZE)
                .all()
            )

            if not events:
                db.close()
                time.sleep(POLL_INTERVAL_SEC)
                continue

            for event in events:
                _process_event(db, event)
                db.commit()

        except Exception:
            db.rollback()
            logger.exception("worker loop error", extra={"event": "worker.loop.error"})
            time.sleep(1.0)
        finally:
            db.close()


if __name__ == "__main__":
    run()
