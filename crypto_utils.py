"""
crypto_utils.py
===============

Message representation, block handling, ciphertext serialisation and input
validation for the ElGamal application.

Why this module exists
----------------------
ElGamal encrypts an *integer* m in the range 0 < m < p. Plaintext typed by a
user is a *string*. This module defines the bridge between the two, and it is
where the ``m < p`` constraint is enforced rather than being ignored.

Encoding scheme
---------------
    text --UTF-8--> bytes --split--> blocks --prefix 0x01--> integers

Each block of at most ``block_size(p)`` bytes is prefixed with a single
0x01 byte before conversion to an integer. The prefix serves two purposes:

  1. It preserves leading zero bytes. Without it, the byte strings
     b"\\x00A" and b"A" would both convert to the integer 65 and decoding
     would be ambiguous.
  2. It guarantees the block integer is non-zero, so the value 0 (which has
     no inverse and is not a member of Z_p*) can never occur.

``block_size(p)`` is chosen as ``(p.bit_length() - 1) // 8 - 1`` bytes, which
guarantees that the prefixed block, having at most ``block_size + 1`` bytes,
is strictly smaller than p for every possible byte pattern.

Ciphertext text format
----------------------
One block per line, each line ``<c1 in hex>:<c2 in hex>``. This format is
compact, copy-pasteable between the encryption and decryption panes of the
GUI, and unambiguous to parse. It is a transport encoding only and provides
no confidentiality, integrity or authentication of its own.
"""

from __future__ import annotations

from typing import List, Tuple

from elgamal import (
    ElGamalError,
    InvalidParameterError,
    MessageTooLargeError,
    PublicKey,
)

#: Separator between the two components of one ciphertext block.
PAIR_SEPARATOR = ":"

#: Separator between consecutive ciphertext blocks.
BLOCK_SEPARATOR = "\n"

#: Non-zero marker byte prefixed to every plaintext block before the
#: byte-to-integer conversion (see module docstring).
PREFIX_BYTE = b"\x01"


class EncodingError(ElGamalError):
    """Raised when plaintext or ciphertext cannot be encoded or decoded."""


class CiphertextFormatError(ElGamalError):
    """Raised when a ciphertext string does not match the expected format."""


# ---------------------------------------------------------------------------
# Block sizing
# ---------------------------------------------------------------------------

def block_size(p: int) -> int:
    """Return the maximum number of plaintext bytes that fit in one block.

    Derivation: the prefixed block occupies ``block_size + 1`` bytes, whose
    largest possible value is ``2^(8*(block_size+1)) - 1``. Requiring
    ``8 * (block_size + 1) <= p.bit_length() - 1`` guarantees that value is
    strictly less than p, so the ``m < p`` condition holds for every input.
    """
    size = (p.bit_length() - 1) // 8 - 1
    if size < 1:
        raise InvalidParameterError(
            "Modulus p is too small to encode even one plaintext byte; "
            "use a larger key size."
        )
    return size


# ---------------------------------------------------------------------------
# Text <-> integer blocks
# ---------------------------------------------------------------------------

def text_to_blocks(text: str, p: int) -> List[int]:
    """Convert *text* into a list of integers, each strictly less than p."""
    if not isinstance(text, str):
        raise EncodingError("Plaintext must be a string.")
    if text == "":
        raise EncodingError("Plaintext is empty; nothing to encrypt.")
    try:
        data = text.encode("utf-8")
    except UnicodeEncodeError as exc:            # pragma: no cover - defensive
        raise EncodingError(f"Plaintext could not be UTF-8 encoded: {exc}")

    size = block_size(p)
    blocks: List[int] = []
    for start in range(0, len(data), size):
        chunk = data[start:start + size]
        m = int.from_bytes(PREFIX_BYTE + chunk, byteorder="big")
        if m >= p:                                # pragma: no cover - defensive
            raise MessageTooLargeError(
                "Internal block sizing error: block integer is not smaller "
                "than p."
            )
        blocks.append(m)
    return blocks


def blocks_to_text(blocks: List[int]) -> str:
    """Convert a list of message integers back into the original text."""
    data = bytearray()
    for index, m in enumerate(blocks):
        if m <= 0:
            raise EncodingError(
                f"Block {index + 1} is not a valid message integer."
            )
        raw = m.to_bytes((m.bit_length() + 7) // 8, byteorder="big")
        if raw[0:1] != PREFIX_BYTE:
            raise EncodingError(
                f"Block {index + 1} does not carry the expected marker byte. "
                "The ciphertext or the private key is probably incorrect."
            )
        data.extend(raw[1:])
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EncodingError(
            "Decrypted bytes are not valid UTF-8 text. The ciphertext or the "
            f"private key is probably incorrect ({exc.reason})."
        )


# ---------------------------------------------------------------------------
# Ciphertext serialisation
# ---------------------------------------------------------------------------

def pairs_to_string(pairs: List[Tuple[int, int]]) -> str:
    """Serialise ciphertext pairs into the transport text format."""
    if not pairs:
        raise CiphertextFormatError("There are no ciphertext blocks to write.")
    return BLOCK_SEPARATOR.join(
        f"{c1:x}{PAIR_SEPARATOR}{c2:x}" for c1, c2 in pairs
    )


def string_to_pairs(text: str) -> List[Tuple[int, int]]:
    """Parse the transport text format back into ciphertext pairs.

    Raises:
        CiphertextFormatError: if the text is empty, has the wrong number of
            components on any line, or contains non-hexadecimal values.
    """
    if not isinstance(text, str) or text.strip() == "":
        raise CiphertextFormatError("Ciphertext field is empty.")

    pairs: List[Tuple[int, int]] = []
    for line_no, line in enumerate(text.strip().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        parts = line.split(PAIR_SEPARATOR)
        if len(parts) != 2:
            raise CiphertextFormatError(
                f"Line {line_no} is malformed: expected exactly one "
                f"'{PAIR_SEPARATOR}' separating c1 and c2."
            )
        try:
            c1 = int(parts[0].strip(), 16)
            c2 = int(parts[1].strip(), 16)
        except ValueError:
            raise CiphertextFormatError(
                f"Line {line_no} contains a value that is not valid "
                "hexadecimal."
            )
        if c1 <= 0 or c2 <= 0:
            raise CiphertextFormatError(
                f"Line {line_no} contains a non-positive ciphertext component."
            )
        pairs.append((c1, c2))

    if not pairs:
        raise CiphertextFormatError("No ciphertext blocks were found.")
    return pairs


# ---------------------------------------------------------------------------
# High-level convenience operations used by the GUI
# ---------------------------------------------------------------------------

def encrypt_text(text: str, key: PublicKey) -> str:
    """Encrypt *text* under *key* and return the serialised ciphertext."""
    from elgamal import encrypt_blocks                # local import: no cycle
    blocks = text_to_blocks(text, key.p)
    pairs = encrypt_blocks(blocks, key)
    return pairs_to_string(pairs)


def decrypt_text(ciphertext: str, key) -> str:
    """Decrypt a serialised ciphertext with a private key and return text."""
    from elgamal import decrypt_blocks                # local import: no cycle
    pairs = string_to_pairs(ciphertext)
    for line_no, (c1, c2) in enumerate(pairs, start=1):
        if c1 >= key.p or c2 >= key.p:
            raise CiphertextFormatError(
                f"Block {line_no} is larger than the modulus p. The "
                "ciphertext does not belong to this key."
            )
    blocks = decrypt_blocks(pairs, key)
    return blocks_to_text(blocks)


# ---------------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------------

def ciphertext_expansion(plaintext: str, ciphertext: str) -> float:
    """Return the ciphertext-to-plaintext size ratio, in characters.

    ElGamal is expected to at least double the message size because each
    plaintext block is replaced by two group elements (c1, c2). The hex
    transport encoding adds a further factor of two.
    """
    plain_len = len(plaintext.encode("utf-8"))
    if plain_len == 0:
        raise EncodingError("Plaintext is empty; expansion is undefined.")
    return len(ciphertext.encode("utf-8")) / plain_len
