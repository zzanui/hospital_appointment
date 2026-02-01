from __future__ import annotations

import json
import logging
import os
import sys
import time
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

TRACE_ID: ContextVar[str | None] = ContextVar("trace_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": os.getenv("SERVICE_NAME", "unknown"),
            "env": os.getenv("ENV", "local"),
            "event": getattr(record, "event", None),
            "trace_id": TRACE_ID.get(),
            "message": record.getMessage(),
        }

        keys = (
            "job_id",
            "appointment_id",
            "doctor_id",
            "slot_id",
            "http_method",
            "http_path",
            "http_status",
            "duration_ms",
        )
        for k in keys:
            if hasattr(record, k):
                payload[k] = getattr(record, k)

        if record.exc_info:
            payload["error"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
            }

        return json.dumps(payload, ensure_ascii=False)


def setup_json_logger(name: str = "app") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def now_ms() -> int:
    return int(time.time() * 1000)
