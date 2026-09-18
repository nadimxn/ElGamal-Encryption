"""
tests/test_crypto_utils.py
==========================

Unit and integration tests for message representation, block handling,
ciphertext serialisation and the end-to-end text round trip.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crypto_utils import (                                     # noqa: E402
    CiphertextFormatError,
    EncodingError,
    block_size,
    blocks_to_text,
    ciphertext_expansion,
    decrypt_text,
    encrypt_text,
    pairs_to_string,
    string_to_pairs,
    text_to_blocks,
)
from elgamal import generate_keypair                            # noqa: E402

TEST_BITS = 256


@pytest.fixture(scope="module")
def keypair():
    return generate_keypair(TEST_BITS)


# ---------------------------------------------------------------------------
# Block sizing
# ---------------------------------------------------------------------------

def test_block_size_leaves_room_for_the_prefix_byte(keypair):
    p = keypair.public.p
    size = block_size(p)
    # The largest possible prefixed block must still be smaller than p.
    largest = int.from_bytes(b"\x01" + b"\xff" * size, "big")
    assert largest < p


def test_block_size_scales_with_modulus():
    small = generate_keypair(128).public.p
    assert block_size(small) < block_size(generate_keypair(256).public.p)


# ---------------------------------------------------------------------------
# Text <-> blocks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "A",
    "Hello, world!",
    "1234567890",
    "!@#$%^&*()_+-=[]{};':\",./<>?",
    "Cryptography is the practice of secure communication.",
    "Unicode: naive cafe resume - and emoji \U0001F510",
    "line one\nline two\ttabbed",
    "x" * 500,
])
def test_text_block_round_trip(text, keypair):
    blocks = text_to_blocks(text, keypair.public.p)
    assert blocks_to_text(blocks) == text


def test_every_block_is_smaller_than_p(keypair):
    blocks = text_to_blocks("y" * 1000, keypair.public.p)
    assert all(0 < m < keypair.public.p for m in blocks)


def test_leading_null_bytes_are_preserved(keypair):
    text = "\x00\x00abc"
    assert blocks_to_text(text_to_blocks(text, keypair.public.p)) == text


def test_empty_plaintext_is_rejected(keypair):
    with pytest.raises(EncodingError):
        text_to_blocks("", keypair.public.p)


def test_long_text_is_split_into_multiple_blocks(keypair):
    size = block_size(keypair.public.p)
    text = "z" * (size * 3 + 1)
    assert len(text_to_blocks(text, keypair.public.p)) == 4


def test_blocks_without_marker_byte_are_rejected():
    # 0x41 = "A" without the 0x01 prefix.
    with pytest.raises(EncodingError):
        blocks_to_text([0x41])


# ---------------------------------------------------------------------------
# Ciphertext serialisation
# ---------------------------------------------------------------------------

def test_pairs_string_round_trip():
    pairs = [(255, 4096), (1, 2), (123456789, 987654321)]
    assert string_to_pairs(pairs_to_string(pairs)) == pairs


@pytest.mark.parametrize("bad", [
    "",
    "   ",
    "deadbeef",                       # no separator
    "dead:beef:cafe",                 # two separators
    "zzzz:1234",                      # not hexadecimal
    "1234:",                          # missing component
    "0:1234",                         # non-positive component
])
def test_malformed_ciphertext_is_rejected(bad):
    with pytest.raises(CiphertextFormatError):
        string_to_pairs(bad)


def test_blank_lines_inside_ciphertext_are_tolerated():
    assert len(string_to_pairs("aa:bb\n\ncc:dd\n")) == 2


# ---------------------------------------------------------------------------
# End-to-end text encryption
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "Short",
    "CCS2243 Cryptography Essential",
    "A longer plaintext that will certainly span several ElGamal blocks "
    "because it is much longer than the per-block byte budget." * 3,
])
def test_text_encrypt_decrypt_round_trip(text, keypair):
    ciphertext = encrypt_text(text, keypair.public)
    assert decrypt_text(ciphertext, keypair.private) == text


def test_same_plaintext_gives_different_ciphertext(keypair):
    text = "Repeat me"
    first = encrypt_text(text, keypair.public)
    second = encrypt_text(text, keypair.public)
    assert first != second
    assert decrypt_text(first, keypair.private) == text
    assert decrypt_text(second, keypair.private) == text


def test_ciphertext_from_another_key_fails_cleanly(keypair):
    other = generate_keypair(TEST_BITS)
    ciphertext = encrypt_text("secret", other.public)
    with pytest.raises((EncodingError, CiphertextFormatError)):
        decrypt_text(ciphertext, keypair.private)


def test_ciphertext_expansion_is_at_least_four(keypair):
    """Two group elements per block, each hex-encoded, so >= 4x growth."""
    text = "Measure the expansion of this message."
    ciphertext = encrypt_text(text, keypair.public)
    assert ciphertext_expansion(text, ciphertext) > 4.0
