"""
tests/test_validation.py
========================

Tests for input validation, error handling and key management. These tests
cover the defensive paths that the GUI relies on: the interface itself only
catches the exceptions raised here and turns them into messages.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_utils import (                                     # noqa: E402
    CiphertextFormatError,
    EncodingError,
    decrypt_text,
    encrypt_text,
)
from elgamal import (                                           # noqa: E402
    InvalidParameterError,
    KeyPair,
    PrivateKey,
    PublicKey,
    generate_keypair,
    validate_public_key,
)
from key_manager import KeyManager, KeyManagerError             # noqa: E402

TEST_BITS = 256


@pytest.fixture(scope="module")
def keypair():
    return generate_keypair(TEST_BITS)


# ---------------------------------------------------------------------------
# Public key validation
# ---------------------------------------------------------------------------

def test_composite_modulus_is_rejected(keypair):
    bad = PublicKey(p=keypair.public.p + 1, g=keypair.public.g,
                    y=keypair.public.y)           # p+1 is even, so composite
    with pytest.raises(InvalidParameterError):
        validate_public_key(bad)


def test_out_of_range_generator_is_rejected(keypair):
    bad = PublicKey(p=keypair.public.p, g=1, y=keypair.public.y)
    with pytest.raises(InvalidParameterError):
        validate_public_key(bad)


# ---------------------------------------------------------------------------
# KeyManager state handling
# ---------------------------------------------------------------------------

def test_manager_starts_without_keys():
    manager = KeyManager()
    assert manager.has_keys is False
    with pytest.raises(KeyManagerError):
        _ = manager.public_key


def test_manager_generates_and_clears():
    manager = KeyManager()
    manager.generate(128)
    assert manager.has_keys is True
    manager.clear()
    assert manager.has_keys is False


def test_manager_rejects_mismatched_moduli(keypair):
    other = generate_keypair(TEST_BITS)
    manager = KeyManager()
    mixed = KeyPair(public=keypair.public, private=other.private)
    with pytest.raises(KeyManagerError):
        manager.set_keypair(mixed)


# ---------------------------------------------------------------------------
# Key file export / import
# ---------------------------------------------------------------------------

def test_export_then_import_restores_the_same_keys(tmp_path, keypair):
    manager = KeyManager()
    manager.set_keypair(keypair)
    pub_path = tmp_path / "public_key.json"
    priv_path = tmp_path / "private_key.json"
    manager.export_public(str(pub_path))
    manager.export_private(str(priv_path))

    loaded = KeyManager().load_pair(str(pub_path), str(priv_path))
    assert loaded.public.p == keypair.public.p
    assert loaded.public.y == keypair.public.y
    assert loaded.private.x == keypair.private.x


def test_import_detects_non_matching_key_files(tmp_path, keypair):
    other = generate_keypair(TEST_BITS)
    manager = KeyManager()
    manager.set_keypair(keypair)
    pub_path = tmp_path / "public_key.json"
    manager.export_public(str(pub_path))

    other_manager = KeyManager()
    other_manager.set_keypair(other)
    priv_path = tmp_path / "other_private_key.json"
    other_manager.export_private(str(priv_path))

    with pytest.raises(KeyManagerError):
        KeyManager().load_pair(str(pub_path), str(priv_path))


def test_import_rejects_incomplete_key_file(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text(json.dumps({"p": "23", "g": "5"}), encoding="utf-8")
    with pytest.raises(KeyManagerError):
        KeyManager.load_public(str(path))


def test_import_rejects_non_json_file(tmp_path):
    path = tmp_path / "notjson.json"
    path.write_text("this is not json", encoding="utf-8")
    with pytest.raises(KeyManagerError):
        KeyManager.load_public(str(path))


def test_import_rejects_non_numeric_values(tmp_path):
    path = tmp_path / "text.json"
    path.write_text(json.dumps({"p": "abc", "g": "5", "y": "7"}),
                    encoding="utf-8")
    with pytest.raises(KeyManagerError):
        KeyManager.load_public(str(path))


# ---------------------------------------------------------------------------
# Application-level error paths
# ---------------------------------------------------------------------------

def test_encrypting_empty_text_raises(keypair):
    with pytest.raises(EncodingError):
        encrypt_text("", keypair.public)


def test_decrypting_garbage_raises(keypair):
    with pytest.raises(CiphertextFormatError):
        decrypt_text("not a ciphertext at all", keypair.private)


def test_ciphertext_larger_than_modulus_is_rejected(keypair):
    p = keypair.public.p
    forged = f"{p + 1:x}:{p + 2:x}"
    with pytest.raises(CiphertextFormatError):
        decrypt_text(forged, keypair.private)


def test_truncated_ciphertext_block_is_reported(keypair):
    ciphertext = encrypt_text("Two blocks of text please, thank you kindly.",
                              keypair.public)
    truncated = ciphertext.splitlines()[0].split(":")[0]     # c1 only
    with pytest.raises(CiphertextFormatError):
        decrypt_text(truncated, keypair.private)


def test_wrong_private_key_is_reported_not_silently_wrong(keypair):
    """A wrong key must produce an error, never plausible-looking output."""
    other = generate_keypair(TEST_BITS)
    ciphertext = encrypt_text("Confidential message", keypair.public)
    wrong = PrivateKey(p=keypair.public.p, g=keypair.public.g,
                       x=other.private.x)
    with pytest.raises(EncodingError):
        decrypt_text(ciphertext, wrong)
