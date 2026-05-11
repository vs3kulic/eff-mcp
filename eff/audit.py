# -*- coding: utf-8 -*-
"""Append-only audit log for EFF invocations.

When `EFF_AUDIT_LOG_PATH` is set, every successful `score_story()` call writes
a single JSON line to that file (JSONL format). The log is intended as an
auditable trail — one row per evaluation, immutable and append-only.

Disabled by default: if the env var is unset, `log_invocation()` is a no-op.

Failures while writing the log are logged to stderr but never propagate — an
audit failure must not break the scoring pipeline.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger("eff.audit")

ENV_VAR = "EFF_AUDIT_LOG_PATH"


def log_invocation(payload: dict[str, Any]) -> None:
    """Append one JSONL row capturing this scoring invocation.

    No-op if `EFF_AUDIT_LOG_PATH` is unset. Errors are logged but never raised.
    """
    path = os.getenv(ENV_VAR)
    if not path:
        return

    record = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        **payload,
    }

    try:
        log_path = Path(path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        logger.warning("audit log write failed: %s: %s", type(exc).__name__, exc)