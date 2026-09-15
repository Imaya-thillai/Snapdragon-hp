"""
FileCore Security Engine
Classifies files by sensitivity, scans for suspicious patterns.
Never auto-deletes. Always requires confirmation for destructive actions.
"""
import os
import re
from pathlib import Path

# Patterns that indicate sensitive content
SENSITIVE_PATTERNS = {
    "HIGHLY_SENSITIVE": [
        r"password", r"passwd", r"secret", r"private.?key", r"api.?key",
        r"token", r"credential", r"auth", r"\.pem$", r"\.key$", r"\.pfx$",
        r"\.p12$", r"id_rsa", r"id_ed25519", r"\.env$", r"wallet", r"seed.?phrase"
    ],
    "CONFIDENTIAL": [
        r"salary", r"payslip", r"bank.?statement", r"tax.?return", r"aadhaar",
        r"pan.?card", r"passport", r"ssn", r"credit.?card", r"resume",
        r"cv\.pdf", r"offer.?letter", r"nda", r"agreement", r"contract",
        r"medical", r"health.?record", r"prescription"
    ],
    "PERSONAL": [
        r"photo", r"selfie", r"diary", r"personal", r"private", r"family"
    ],
    "SYSTEM": [
        r"\.sys$", r"\.dll$", r"\.exe$", r"\.bat$", r"registry", r"system32"
    ]
}

# Suspicious file signatures
SUSPICIOUS_EXTENSIONS = {
    ".exe", ".scr", ".com", ".vbs", ".ps1", ".jar", ".hta", ".pif", ".cmd"
}

DOUBLE_EXTENSION_RE = re.compile(r"\.(pdf|doc|docx|txt)\.(exe|bat|vbs|scr)$", re.IGNORECASE)


def classify_file(filename: str, path: str, content: str = "") -> str:
    """Classify a file into a security category."""
    name_lower = filename.lower()
    path_lower = path.lower()
    content_lower = (content or "").lower()

    for level in ["HIGHLY_SENSITIVE", "CONFIDENTIAL", "PERSONAL", "SYSTEM"]:
        for pattern in SENSITIVE_PATTERNS[level]:
            if re.search(pattern, name_lower) or re.search(pattern, path_lower) or re.search(pattern, content_lower):
                return level

    return "PUBLIC"


def is_suspicious(filename: str, path: str) -> dict:
    """Detect suspicious files. Returns explanation, never auto-deletes."""
    ext = Path(filename).suffix.lower()
    reasons = []

    if ext in SUSPICIOUS_EXTENSIONS:
        reasons.append(f"Executable extension ({ext}) — verify source before opening.")

    if DOUBLE_EXTENSION_RE.search(filename):
        reasons.append("Double extension detected (e.g., document.pdf.exe) — common malware trick.")

    if len(filename) > 150:
        reasons.append("Unusually long filename — may indicate obfuscation.")

    is_susp = len(reasons) > 0
    return {
        "is_suspicious": is_susp,
        "filename": filename,
        "path": path,
        "reasons": reasons,
        "recommendation": "Review manually before opening." if is_susp else "No obvious issues detected."
    }


def scan_file(file_path: str) -> dict:
    """Run a local security scan on a single file."""
    filename = os.path.basename(file_path)
    susp = is_suspicious(filename, file_path)

    try:
        size = os.path.getsize(file_path)
    except Exception:
        size = -1

    return {
        "file": file_path,
        "filename": filename,
        "security_class": classify_file(filename, file_path),
        "suspicious": susp["is_suspicious"],
        "reasons": susp["reasons"],
        "recommendation": susp["recommendation"],
        "size_bytes": size,
        "processed_locally": True
    }
