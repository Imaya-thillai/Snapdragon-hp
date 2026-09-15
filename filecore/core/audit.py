"""
FileCore Audit Engine
Tamper-aware, structured audit logging.
"""

import hashlib
import json
import os
from datetime import datetime


def compute_event_hash(timestamp: str, action: str, target: str, result: str) -> str:
    """Creates a tamper-evident hash chaining audit events."""
    data = f"{timestamp}:{action}:{target}:{result}"
    return hashlib.sha256(data.encode()).hexdigest()


def get_audit_viewer(limit: int = 50) -> list:
    from filecore.db.database import get_audit_log
    return get_audit_log(limit)


def audit(action: str, target: str, risk_level: str, result: str, details: str = ""):
    """Write a structured, signed audit event to the local DB."""
    from filecore.db.database import log_audit
    log_audit(action, target, risk_level, result, details)
