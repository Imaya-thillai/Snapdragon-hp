"""
FileCore Policy & Action Control Engine

The AI must NEVER have unrestricted filesystem access.
Every action flows through this policy engine:

User Command → Policy Engine → Permission Check → Confirmation (if needed) → Execute → Audit
"""

import os
import shutil
from enum import Enum
from filecore.core.audit import audit


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Action registry with risk levels and confirmation requirements
ACTION_REGISTRY = {
    "open_file":          {"risk": RiskLevel.LOW,      "confirm": False},
    "open_folder":        {"risk": RiskLevel.LOW,      "confirm": False},
    "copy_path":          {"risk": RiskLevel.LOW,      "confirm": False},
    "summarize":          {"risk": RiskLevel.LOW,      "confirm": False},
    "analyze":            {"risk": RiskLevel.LOW,      "confirm": False},
    "search":             {"risk": RiskLevel.LOW,      "confirm": False},
    "index":              {"risk": RiskLevel.LOW,      "confirm": False},
    "move_file":          {"risk": RiskLevel.HIGH,     "confirm": True},
    "delete_file":        {"risk": RiskLevel.CRITICAL, "confirm": True},
    "rename_file":        {"risk": RiskLevel.MEDIUM,   "confirm": True},
    "overwrite_file":     {"risk": RiskLevel.HIGH,     "confirm": True},
    "change_permissions": {"risk": RiskLevel.CRITICAL, "confirm": True},
}

# Prompt injection guard: file content must never be treated as an instruction
INJECTION_PATTERNS = [
    "ignore previous", "disregard", "system:", "you are now",
    "delete all", "rm -rf", "format c:", "shutdown", "execute",
    "bypass security", "disable protection"
]


def check_injection(content: str) -> bool:
    """Returns True if potential prompt injection is detected in file content."""
    lower = content.lower()
    return any(p in lower for p in INJECTION_PATTERNS)


def request_action(action: str, target: str, confirmed: bool = False,
                   extra: dict = None) -> dict:
    """
    Main policy gate. All actions must pass through here.
    Returns a result dict with status, message, and whether confirmation is needed.
    """
    if action not in ACTION_REGISTRY:
        audit(action, target, "UNKNOWN", "DENIED", "Action not in allowlist")
        return {"status": "denied", "reason": f"Action '{action}' is not in the allowlist."}

    spec = ACTION_REGISTRY[action]
    risk = spec["risk"]
    needs_confirm = spec["confirm"]

    # Validate target path exists for filesystem operations
    if action not in ("search", "index") and not os.path.exists(target):
        # Don't raise for move/delete if target was already given
        if action != "delete_file":
            return {"status": "error", "reason": f"Path does not exist: {target}"}

    # Require confirmation for destructive/high-risk actions
    if needs_confirm and not confirmed:
        return {
            "status": "needs_confirmation",
            "action": action,
            "target": target,
            "risk_level": risk,
            "message": f"This action is {risk}. Please confirm to proceed."
        }

    # --- Execute safe actions ---
    result = _execute_action(action, target, extra or {})
    audit(action, target, risk, result["status"], result.get("message", ""))
    return result


def _execute_action(action: str, target: str, extra: dict) -> dict:
    try:
        if action == "open_file":
            os.startfile(target)
            return {"status": "success", "message": f"Opened: {target}"}

        elif action == "open_folder":
            folder = os.path.dirname(target) if os.path.isfile(target) else target
            os.startfile(folder)
            return {"status": "success", "message": f"Opened folder: {folder}"}

        elif action == "copy_path":
            return {"status": "success", "message": target, "copied_path": target}

        elif action == "delete_file":
            os.remove(target)
            return {"status": "success", "message": f"Deleted: {target}"}

        elif action == "move_file":
            dest = extra.get("destination")
            if not dest:
                return {"status": "error", "message": "No destination specified."}
            shutil.move(target, dest)
            return {"status": "success", "message": f"Moved {target} → {dest}"}

        elif action == "rename_file":
            new_name = extra.get("new_name")
            if not new_name:
                return {"status": "error", "message": "No new name specified."}
            folder = os.path.dirname(target)
            new_path = os.path.join(folder, new_name)
            os.rename(target, new_path)
            return {"status": "success", "message": f"Renamed to: {new_path}"}

        else:
            return {"status": "success", "message": f"Action '{action}' acknowledged."}

    except PermissionError:
        return {"status": "denied", "message": f"Permission denied: {target}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
