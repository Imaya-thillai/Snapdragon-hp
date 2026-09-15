import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "filecore_data", "filecore.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize all database tables."""
    conn = get_connection()
    c = conn.cursor()

    # File metadata table
    c.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE NOT NULL,
        filename TEXT,
        extension TEXT,
        size_bytes INTEGER,
        created_at TEXT,
        modified_at TEXT,
        file_hash TEXT,
        mime_type TEXT,
        permissions TEXT,
        extracted_text TEXT,
        security_class TEXT DEFAULT 'PUBLIC',
        indexed_at TEXT,
        embedding_ref TEXT
    )
    """)

    # FTS5 virtual table for full-text search
    c.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
        filename,
        extracted_text,
        path,
        content='files',
        content_rowid='id'
    )
    """)

    # Duplicate file groups
    c.execute("""
    CREATE TABLE IF NOT EXISTS duplicate_groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_hash TEXT,
        paths TEXT,
        detected_at TEXT
    )
    """)

    # Audit events
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        action TEXT,
        target TEXT,
        user TEXT,
        risk_level TEXT,
        result TEXT,
        details TEXT,
        signed_hash TEXT
    )
    """)

    # Security events
    c.execute("""
    CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        file_path TEXT,
        severity TEXT,
        description TEXT,
        resolved INTEGER DEFAULT 0
    )
    """)

    # Indexing jobs
    c.execute("""
    CREATE TABLE IF NOT EXISTS index_jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        root_path TEXT,
        started_at TEXT,
        completed_at TEXT,
        files_indexed INTEGER,
        status TEXT
    )
    """)

    # Settings
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("[DB] Initialized FileCore database.")

def upsert_file(meta: dict):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO files (path, filename, extension, size_bytes, created_at, modified_at, 
                       file_hash, mime_type, permissions, extracted_text, security_class, indexed_at)
    VALUES (:path, :filename, :extension, :size_bytes, :created_at, :modified_at,
            :file_hash, :mime_type, :permissions, :extracted_text, :security_class, :indexed_at)
    ON CONFLICT(path) DO UPDATE SET
        filename=excluded.filename, extension=excluded.extension, size_bytes=excluded.size_bytes,
        modified_at=excluded.modified_at, file_hash=excluded.file_hash, mime_type=excluded.mime_type,
        extracted_text=excluded.extracted_text, security_class=excluded.security_class, indexed_at=excluded.indexed_at
    """, meta)

    # Update FTS index
    row = c.execute("SELECT id FROM files WHERE path=?", (meta["path"],)).fetchone()
    if row:
        c.execute("INSERT OR REPLACE INTO files_fts(rowid, filename, extracted_text, path) VALUES (?,?,?,?)",
                  (row["id"], meta.get("filename",""), meta.get("extracted_text",""), meta.get("path","")))

    conn.commit()
    conn.close()

def search_files(query: str, limit: int = 20) -> list:
    conn = get_connection()
    c = conn.cursor()
    
    # 1) Exact filename match
    exact = c.execute(
        "SELECT * FROM files WHERE filename LIKE ? LIMIT ?", (f"%{query}%", limit)
    ).fetchall()

    # 2) FTS full-text search
    try:
        fts = c.execute(
            "SELECT f.* FROM files_fts ft JOIN files f ON f.id = ft.rowid WHERE files_fts MATCH ? LIMIT ?",
            (query, limit)
        ).fetchall()
    except Exception:
        fts = []

    # Merge and deduplicate
    seen = set()
    results = []
    for row in list(exact) + list(fts):
        if row["path"] not in seen:
            seen.add(row["path"])
            results.append(dict(row))

    conn.close()
    return results[:limit]

def get_all_files():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM files").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def log_audit(action, target, risk_level, result, details="", user="local_user"):
    from filecore.core.audit import compute_event_hash
    conn = get_connection()
    ts = datetime.now().isoformat()
    signed = compute_event_hash(ts, action, target, result)
    conn.execute(
        "INSERT INTO audit_events (timestamp, action, target, user, risk_level, result, details, signed_hash) VALUES (?,?,?,?,?,?,?,?)",
        (ts, action, target, user, risk_level, result, details, signed)
    )
    conn.commit()
    conn.close()

def get_audit_log(limit=50):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    init_db()
