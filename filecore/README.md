# FileCore 🔐

> **Hardware-rooted, offline local file intelligence.**
> Local • Private • Offline — No cloud. No API keys. No data leaves your machine.

FileCore is a production-quality, offline-first Windows desktop system — a secure local file intelligence and security layer that works directly with your real Windows File Explorer and local filesystem.

---

## Quick Start

```powershell
# 1. Install Python dependencies
cd filecore
pip install -r requirements.txt

# 2. Index a folder
python -m filecore.cli.vault index "C:\Users\YourName\Documents"

# 3. Search instantly
python -m filecore.cli.vault find my project report

# 4. Open in Explorer
python -m filecore.cli.vault open resume

# 5. Summarize a document (locally)
python -m filecore.cli.vault summarize "C:\path\to\file.pdf"

# 6. Check system status
python -m filecore.cli.vault status
```

---

## CLI Commands

| Command | Description |
|---|---|
| `vault find <query>` | Search indexed files |
| `vault open <query>` | Find and open in Windows File Explorer |
| `vault analyze <path>` | Local security scan |
| `vault summarize <path>` | Summarize locally (PDF, DOCX, TXT, code...) |
| `vault duplicates` | Detect duplicate files |
| `vault sensitive` | Show confidential/sensitive files |
| `vault index <path>` | Index a directory |
| `vault audit` | View tamper-evident audit log |
| `vault status` | System status, HSAL, AI runtime |

---

## Web Dashboard API

```powershell
python filecore/filecore_api.py
# → http://127.0.0.1:8001
```

---

## Architecture

```
User Command (vault CLI / Web Dashboard)
        ↓
FileCore Command Parser
        ↓
Policy Engine (action allowlist, risk levels, confirmation)
        ↓
Security Layer (classification, suspicious file scan)
        ↓
Local AI / Search Engine (SQLite FTS5, offline-first)
        ↓
Real Filesystem (NTFS, actual Windows paths)
        ↓
Audit Logger (tamper-evident SHA-256 chained events)
        ↓
Hardware Security Abstraction Layer (HSAL)
   [SIMULATION MODE → Future: FileCore Secure Element chip]
```

---

## Hardware Security Module

The **FileCore Secure Element (FSE-1)** concept is a future laptop-integrated chip responsible for:
- Hardware-backed device identity
- Cryptographic key storage (Ed25519)
- Secure audit event signing
- Anti-tamper state

Current status: **⚠ SIMULATION / DEVELOPMENT MODE**
See `docs/HARDWARE_CHIP_CONCEPT.md` for the full hardware architecture.

---

## AI Model Attribution

| Model | Source | Used For |
|---|---|---|
| ONNX Runtime (abstracted) | Microsoft (open-source) | Local inference runtime |
| Extractive Summarization | Local (no model needed) | Default summarization |
| SentenceTransformers (optional) | HuggingFace (open-source) | Future semantic search |

---

## Running Tests

```powershell
python filecore/tests/test_all.py
```

---

## Offline Guarantee

FileCore's core engine makes **zero network calls**. The web dashboard communicates only with `127.0.0.1:8001` (localhost). The system tray shows `OFFLINE / LOCAL MODE` status at all times.
