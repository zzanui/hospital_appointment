from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import DateTime, String, Text

from core.db import Base


class Job(Base):
    __tablename__ = "jobs"

    # UUID 문자열 (SQLite 테스트 호환)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

    # QUEUED/RUNNING/SUCCEEDED/FAILED
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="QUEUED")

    # 성공 시 결과(예: appointment_id), 실패 시 에러 메시지
    result: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
