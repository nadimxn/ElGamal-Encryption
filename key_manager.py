"""
key_manager.py
==============

Educational key handling: in-memory storage of the active key pair and
optional export/import of keys as JSON files.

SECURITY NOTICE
---------------
Keys are written as plain, unencrypted JSON. This is adequate for a
classroom demonstration and for reproducing test evidence, but it is NOT a
secure key store. Anyone who can read the private-key file can decrypt every
message encrypted under the matching public key. A real system would protect
the private key with a password-based key derivation function and an
authenticated cipher, restrict file permissions, or delegate storage to an
operating-system keystore or hardware security module. This limitation is
stated explicitly rather than hidden.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from elgamal import (
    ElGamalError,
    InvalidParameterError,
    KeyPair,
    PrivateKey,
    PublicKey,
    generate_keypair,
    validate_public_key,
)

PUBLIC_KEY_FIELDS = ("p", "g", "y")
PRIVATE_KEY_FIELDS = ("p", "g", "x")


class KeyManagerError(ElGamalError):
    """Raised when a key cannot be stored, loaded or validated."""


class KeyManager:
    """Holds the key pair currently in use by the application."""

    def __init__(self) -> None:
        self._keypair: Optional[KeyPair] = None

    # -- state -------------------------------------------------------------

    @property
    def has_keys(self) -> bool:
        """True if a key pair has been generated or loaded."""
        return self._keypair is not None

    @property
    def keypair(self) -> KeyPair:
        if self._keypair is None:
            raise KeyManagerError(
                "No key pair is available. Generate or load a key pair first."
            )
        return self._keypair

    @property
    def public_key(self) -> PublicKey:
        return self.keypair.public

    @property
    def private_key(self) -> PrivateKey:
        return self.keypair.private

    # -- generation --------------------------------------------------------

    def generate(self, bits: int = 512) -> KeyPair:
        """Generate and store a new key pair of the requested size."""
        self._keypair = generate_keypair(bits)
        return self._keypair

    def clear(self) -> None:
        """Discard the in-memory key pair."""
        self._keypair = None

    def set_keypair(self, keypair: KeyPair) -> None:
        """Install an externally supplied key pair after validating it."""
        validate_public_key(keypair.public)
        if keypair.public.p != keypair.private.p:
            raise KeyManagerError(
                "Public and private keys use different moduli."
            )
        self._keypair = keypair

    # -- export ------------------------------------------------------------

    def export_public(self, path: str) -> None:
        """Write the public key (p, g, y) to *path* as JSON."""
        self._write_json(path, {
            "type": "elgamal-public-key",
            "bits": self.public_key.bit_length,
            **self.public_key.as_dict(),
        })

    def export_private(self, path: str) -> None:
        """Write the private key (p, g, x) to *path* as **unencrypted** JSON.

        See the module-level security notice.
        """
        self._write_json(path, {
            "type": "elgamal-private-key",
            "warning": "UNENCRYPTED private key - educational use only.",
            "bits": self.private_key.p.bit_length(),
            **self.private_key.as_dict(),
        })

    @staticmethod
    def _write_json(path: str, payload: dict) -> None:
        try:
            directory = os.path.dirname(os.path.abspath(path))
            os.makedirs(directory, exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)
        except OSError as exc:
            raise KeyManagerError(f"Could not write key file: {exc}")

    # -- import ------------------------------------------------------------

    @staticmethod
    def _read_json(path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except OSError as exc:
            raise KeyManagerError(f"Could not read key file: {exc}")
        except json.JSONDecodeError as exc:
            raise KeyManagerError(f"Key file is not valid JSON: {exc.msg}")

    @classmethod
    def load_public(cls, path: str) -> PublicKey:
        """Load and validate a public key from a JSON file."""
        data = cls._read_json(path)
        missing = [f for f in PUBLIC_KEY_FIELDS if f not in data]
        if missing:
            raise KeyManagerError(
                f"Public key file is missing field(s): {', '.join(missing)}."
            )
        try:
            key = PublicKey(p=int(data["p"]), g=int(data["g"]),
                            y=int(data["y"]))
        except (TypeError, ValueError):
            raise KeyManagerError("Public key file contains non-numeric values.")
        try:
            validate_public_key(key)
        except InvalidParameterError as exc:
            raise KeyManagerError(f"Public key failed validation: {exc}")
        return key

    @classmethod
    def load_private(cls, path: str) -> PrivateKey:
        """Load a private key from a JSON file."""
        data = cls._read_json(path)
        missing = [f for f in PRIVATE_KEY_FIELDS if f not in data]
        if missing:
            raise KeyManagerError(
                f"Private key file is missing field(s): {', '.join(missing)}."
            )
        try:
            key = PrivateKey(p=int(data["p"]), g=int(data["g"]),
                             x=int(data["x"]))
        except (TypeError, ValueError):
            raise KeyManagerError(
                "Private key file contains non-numeric values."
            )
        if not (1 < key.x < key.p - 1):
            raise KeyManagerError("Private exponent x is out of range.")
        return key

    def load_pair(self, public_path: str, private_path: str) -> KeyPair:
        """Load a public and private key file and check that they match."""
        public = self.load_public(public_path)
        private = self.load_private(private_path)
        if public.p != private.p or public.g != private.g:
            raise KeyManagerError(
                "The public and private key files do not share the same "
                "domain parameters (p, g)."
            )
        if pow(private.g, private.x, private.p) != public.y:
            raise KeyManagerError(
                "The private key does not correspond to the public key "
                "(g^x mod p does not equal y)."
            )
        keypair = KeyPair(public=public, private=private)
        self._keypair = keypair
        return keypair
