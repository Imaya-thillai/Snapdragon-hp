"""
FileCore Hardware Security Abstraction Layer (HSAL)

IMPORTANT: This is a SOFTWARE SIMULATION / DEVELOPMENT MODE implementation.
The API is designed so that a future hardware Secure Element, TPM, or custom
ASIC/MCU security controller can replace this mock without rewriting any
application code.

Hardware Security Module: SIMULATION / DEVELOPMENT MODE
"""

import hashlib
import os
import json
import uuid
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)


SIMULATION_LABEL = "Hardware Security Module: SIMULATION / DEVELOPMENT MODE"
CHIP_CONCEPT_NAME = "FileCore Secure Element (FSE-1)"

# Persistent key storage path (software simulation only)
KEY_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "filecore_data", "sim_keys.json")


class HardwareSecurityAbstractionLayer:
    """
    HSAL Interface.
    Future implementation: replace this class with a real TPM/Secure Element backend.
    The interface must remain identical.
    """

    def __init__(self):
        self.mode = "SIMULATION"
        self.device_id = self._get_or_create_device_id()
        self._private_key = self._load_or_generate_key()
        print(f"[HSAL] WARNING: {SIMULATION_LABEL}")
        print(f"[HSAL] Device ID: {self.device_id}")

    def _get_or_create_device_id(self) -> str:
        """Persistent simulated hardware device identity."""
        os.makedirs(os.path.dirname(KEY_STORE_PATH), exist_ok=True)
        if os.path.exists(KEY_STORE_PATH):
            try:
                with open(KEY_STORE_PATH) as f:
                    data = json.load(f)
                    if "device_id" in data:
                        return data["device_id"]
            except Exception:
                pass
        dev_id = str(uuid.uuid4())
        self._persist({"device_id": dev_id})
        return dev_id

    def _load_or_generate_key(self):
        """Load or generate a simulated Ed25519 signing key."""
        try:
            with open(KEY_STORE_PATH) as f:
                data = json.load(f)
                if "private_key_bytes" in data:
                    key_bytes = bytes.fromhex(data["private_key_bytes"])
                    return Ed25519PrivateKey.from_private_bytes(key_bytes)
        except Exception:
            pass

        key = Ed25519PrivateKey.generate()
        key_bytes = key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
        self._persist_key(key_bytes)
        return key

    def _persist(self, data: dict):
        os.makedirs(os.path.dirname(KEY_STORE_PATH), exist_ok=True)
        existing = {}
        if os.path.exists(KEY_STORE_PATH):
            try:
                with open(KEY_STORE_PATH) as f:
                    existing = json.load(f)
            except Exception:
                pass
        existing.update(data)
        with open(KEY_STORE_PATH, "w") as f:
            json.dump(existing, f)

    def _persist_key(self, key_bytes: bytes):
        self._persist({"private_key_bytes": key_bytes.hex()})

    # ---- Public HSAL API (identical interface for future hardware) ----

    def get_device_identity(self) -> dict:
        """Returns the hardware-backed device identity."""
        return {
            "device_id": self.device_id,
            "mode": self.mode,
            "chip_name": CHIP_CONCEPT_NAME,
            "simulation": True
        }

    def sign_data(self, data: bytes) -> str:
        """Sign data with the device private key."""
        signature = self._private_key.sign(data)
        return signature.hex()

    def verify_signature(self, data: bytes, signature_hex: str) -> bool:
        """Verify a signature using the device public key."""
        try:
            pub_key = self._private_key.public_key()
            pub_key.verify(bytes.fromhex(signature_hex), data)
            return True
        except Exception:
            return False

    def get_public_key(self) -> str:
        """Returns the simulated hardware public key."""
        pub = self._private_key.public_key()
        return pub.public_bytes(Encoding.Raw, PublicFormat.Raw).hex()

    def secure_hash(self, data: bytes) -> str:
        """Hardware-backed secure hash (simulated via SHA-256)."""
        return hashlib.sha256(data).hexdigest()

    def get_status(self) -> dict:
        return {
            "status": "SIMULATION",
            "label": SIMULATION_LABEL,
            "chip_concept": CHIP_CONCEPT_NAME,
            "device_id": self.device_id,
            "secure_boot_verified": False,
            "anti_tamper": False,
            "note": (
                "In production, this layer connects to a physical Secure Element "
                "integrated into the laptop hardware. The API interface is identical."
            )
        }


# Singleton instance
hsal = HardwareSecurityAbstractionLayer()
