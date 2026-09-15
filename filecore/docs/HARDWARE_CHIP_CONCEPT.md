# FileCore Secure Element (FSE-1) — Hardware Chip Concept

## Overview
The **FileCore Secure Element (FSE-1)** is a dedicated hardware security chip concept designed for integration into Snapdragon-powered laptops alongside the existing CPU/NPU.

> **IMPORTANT:** The FSE-1 is NOT the AI processor. AI inference runs on the Snapdragon NPU. The FSE-1 is responsible exclusively for **trust, identity, cryptography, and integrity**.

## Responsibilities
| Function | Description |
|---|---|
| Hardware Device Identity | Unique, factory-burned device ID (cannot be cloned in software) |
| Key Storage | Ed25519 / ECDSA P-256 private keys never leave the chip |
| Secure Key Generation | TRNG-backed key generation |
| Secure Boot Verification | Measures and attests the FileCore software stack at boot |
| Integrity Measurement | TPM-style PCR registers for runtime integrity |
| Signed Audit Events | Every audit record is hardware-signed |
| Encrypted Storage Key | Wraps the SQLite database encryption key |
| Anti-Tamper State | Detects physical probing or key extraction attempts |

## Interface (Current HSAL API — identical for hardware replacement)
```python
hsal.get_device_identity()    # → hardware device ID
hsal.sign_data(bytes)         # → Ed25519 signature
hsal.verify_signature(bytes)  # → bool
hsal.get_public_key()         # → hex pubkey
hsal.secure_hash(bytes)       # → hardware-backed SHA-256
hsal.get_status()             # → chip status dict
```

## Current State
**⚠ SIMULATION / DEVELOPMENT MODE**
The software mock implementation uses Python's `cryptography` library to simulate the chip API identically. Replacing the software mock with a real FSE-1 driver requires only changing `hsal/hsal.py` — all application code remains the same.
