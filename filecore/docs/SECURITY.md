# FileCore Security Model

## Assets
- User files (documents, code, personal data)
- FileCore index database (SQLite)
- HSAL cryptographic keys
- Audit log
- Configuration

## Trust Boundaries
- **Trusted:** User commands, FileCore policy engine
- **Untrusted:** File contents, filenames (may be adversarially crafted)
- **Isolated:** AI processing layer (cannot directly modify filesystem)

## Threat Actors
| Actor | Description |
|---|---|
| Malicious file | PDF/DOCX with injected instructions |
| Local process | Other applications attempting to access FileCore DB |
| Stolen laptop | Physical access to device |
| Tampered index | Modified SQLite database |
| Compromised model | Manipulated local AI model |

## Mitigations
- **Prompt Injection Guard:** File content is NEVER treated as an instruction
- **Policy Engine:** AI can only REQUEST actions; policy engine approves/denies
- **Confirmation Required:** All CRITICAL/HIGH actions require explicit user confirmation
- **Audit Logs:** SHA-256 chained, tamper-evident
- **HSAL Signing:** Audit events signed by simulated (future: hardware) key
- **No Auto-Delete:** AI predictions alone never trigger destructive operations
- **Least Privilege:** Indexer skips system/protected directories by default

## Residual Risks
- Software simulation does not provide hardware-level tamper resistance
- Local model files could be replaced by a privileged adversary
- SQLite database is not encrypted at rest (future: AES-256 via HSAL key)
