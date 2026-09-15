"""
FileCore Hybrid Search Engine
Combines exact filename search, path search, metadata filtering, and SQLite FTS5.
"""

from filecore.db.database import search_files, get_all_files
from datetime import datetime


SECURITY_CLASSES = ["PUBLIC", "PERSONAL", "CONFIDENTIAL", "HIGHLY_SENSITIVE", "SYSTEM"]


def search(query: str, limit: int = 20, filter_ext: str = None,
           filter_class: str = None) -> list:
    """
    Hybrid search:
    1. Exact filename match
    2. SQLite FTS5 full-text over filename + extracted text + path
    """
    results = search_files(query, limit=limit * 2)

    # Apply filters
    if filter_ext:
        results = [r for r in results if r.get("extension", "").lstrip(".") == filter_ext.lstrip(".")]

    if filter_class:
        results = [r for r in results if r.get("security_class") == filter_class.upper()]

    # Score and rank
    scored = []
    ql = query.lower()
    for r in results:
        score = 0
        fname = (r.get("filename") or "").lower()
        path = (r.get("path") or "").lower()
        text = (r.get("extracted_text") or "").lower()

        if ql == fname:
            score += 100
        elif ql in fname:
            score += 80
        elif ql in path:
            score += 60
        if ql in text:
            score += 40

        r["relevance_score"] = score
        scored.append(r)

    scored.sort(key=lambda x: x["relevance_score"], reverse=True)
    return scored[:limit]


def find_sensitive_files() -> list:
    """Return all files classified as CONFIDENTIAL or HIGHLY_SENSITIVE."""
    all_files = get_all_files()
    return [f for f in all_files if f.get("security_class") in ("CONFIDENTIAL", "HIGHLY_SENSITIVE")]


def find_recent_files(limit: int = 20) -> list:
    """Return files sorted by modification date."""
    all_files = get_all_files()
    sorted_files = sorted(
        all_files,
        key=lambda x: x.get("modified_at") or "",
        reverse=True
    )
    return sorted_files[:limit]
