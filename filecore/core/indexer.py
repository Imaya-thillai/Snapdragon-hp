"""
FileCore Background File Indexer
Walks user-selected directories, hashes files, extracts metadata,
and stores everything in the local SQLite database.
"""
import hashlib
import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List

from filecore.db.database import upsert_file, init_db
from filecore.core.security import classify_file
from filecore.core.document_intel import extract_text

SKIP_DIRS = {
    "Windows", "Program Files", "Program Files (x86)",
    "$Recycle.Bin", "System Volume Information",
    "__pycache__", ".git", "node_modules", "venv", "env",
    ".chroma", "target"
}

def sha256_file(path: str, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError):
        return "unreadable"

def get_permissions(path: str) -> str:
    try:
        stat = os.stat(path)
        return oct(stat.st_mode)
    except Exception:
        return "unknown"

def index_directory(root_path: str, progress_callback=None) -> dict:
    """Index a directory tree and store metadata into the local DB."""
    init_db()
    count = 0
    errors = 0

    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip protected/system directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]

        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            try:
                stat = os.stat(full_path)
                ext = Path(filename).suffix.lower()
                mime, _ = mimetypes.guess_type(full_path)

                # Extract text from supported documents
                text = extract_text(full_path, ext)

                meta = {
                    "path": full_path,
                    "filename": filename,
                    "extension": ext,
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_hash": sha256_file(full_path),
                    "mime_type": mime or "unknown",
                    "permissions": get_permissions(full_path),
                    "extracted_text": text[:5000] if text else "",  # cap at 5KB
                    "security_class": classify_file(filename, full_path, text),
                    "indexed_at": datetime.now().isoformat(),
                }
                upsert_file(meta)
                count += 1

                if progress_callback:
                    progress_callback(count, full_path)

            except (PermissionError, OSError, Exception) as e:
                errors += 1
                continue

    return {"indexed": count, "errors": errors, "root": root_path}

def find_duplicates() -> list:
    """Detect duplicate files by SHA-256 hash."""
    from filecore.db.database import get_all_files, get_connection
    files = get_all_files()
    
    hash_map = {}
    for f in files:
        h = f.get("file_hash", "unreadable")
        if h and h != "unreadable":
            hash_map.setdefault(h, []).append(f["path"])
    
    duplicates = [
        {"hash": h, "paths": paths, "count": len(paths)}
        for h, paths in hash_map.items()
        if len(paths) > 1
    ]
    return duplicates
