from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, Integer, JSON, String, Text

from core.db import Base


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 논리적 이벤트 타입 (예: appointment.requested)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # 확장 시 Kafka topic으로 그대로 사용 가능
    topic: Mapped[str] = mapped_column(String(200), nullable=False)

    # 파티션 키(여기서는 job_id)
    key: Mapped[str] = mapped_column(String(200), nullable=False)

    # 처리에 필요한 데이터
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    # PENDING / PUBLISHED / FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="PENDING")

    publish_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    published_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)
