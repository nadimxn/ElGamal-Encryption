"""
elgamal.py
==========

Core mathematics of the ElGamal public-key cryptosystem (ElGamal, 1985).

This module is deliberately self-contained: every cryptographic operation
(primality testing, safe-prime generation, generator selection, key
generation, encryption, decryption, modular inversion) is implemented here
from Python's built-in integer arithmetic. No third-party cryptographic
library performs any part of the ElGamal computation.

The only external dependency is the standard-library ``secrets`` module,
which provides a cryptographically secure pseudo-random number generator
(CSPRNG) backed by the operating system entropy source.

Notation used throughout (standard ElGamal notation):
    p  - a large prime modulus
    g  - a generator of the multiplicative group Z_p*
    x  - the private key, 1 < x < p-1
    y  - the public value, y = g^x mod p
    k  - a fresh ephemeral (one-time) random exponent, chosen per encryption
    m  - the plaintext represented as an integer with 0 < m < p
    c1 - g^k mod p
    c2 - m * y^k mod p

Author : S M Nadim Mahmud (AIU24102398)
Course : CCS2243 - Cryptography Essential
Purpose: Educational implementation for university assessment. This code is
         NOT intended for production use. See README.md and the security
         discussion in the project report for the limitations.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

#: Key sizes (in bits) that the application offers. 256 and 512 bits are far
#: below any real-world security level and are offered only because they make
#: the demonstration fast enough to run interactively during a viva. 1024 and
#: 2048 bits are included so that the performance trend can be measured.
SUPPORTED_KEY_SIZES: Tuple[int, ...] = (256, 512, 1024, 2048)

#: Minimum modulus size the implementation will accept at all. Below this the
#: block-encoding scheme has no room to work.
MIN_KEY_BITS: int = 64

#: Number of Miller-Rabin rounds used for probabilistic primality testing.
#: With 40 rounds the probability that a composite is wrongly reported prime
#: is at most 4^-40, which is negligible for this project's purposes.
MILLER_RABIN_ROUNDS: int = 40

#: Small primes used for fast trial division before the (expensive)
#: Miller-Rabin test. This is a performance optimisation only; it does not
#: change the correctness of the primality decision.
_SMALL_PRIMES: Tuple[int, ...] = (
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251,
)


class ElGamalError(Exception):
    """Base class for all errors raised by this module."""


class InvalidParameterError(ElGamalError):
    """Raised when a supplied domain parameter or key is not valid."""


class MessageTooLargeError(ElGamalError):
    """Raised when an integer message m does not satisfy 0 < m < p.

    ElGamal operates in Z_p*, so a message integer that is greater than or
    equal to p cannot be recovered: it would be reduced modulo p and the
    original value would be lost. The implementation raises this error rather
    than allowing a silent, unrecoverable mathematical failure.
    """


class DecryptionError(ElGamalError):
    """Raised when a ciphertext cannot be decrypted with the supplied key."""


# ---------------------------------------------------------------------------
# Key containers
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PublicKey:
    """ElGamal public key (p, g, y)."""

    p: int
    g: int
    y: int

    @property
    def bit_length(self) -> int:
        """Bit length of the modulus p."""
        return self.p.bit_length()

    def as_dict(self) -> dict:
        return {"p": str(self.p), "g": str(self.g), "y": str(self.y)}


@dataclass(frozen=True)
class PrivateKey:
    """ElGamal private key x, stored together with its domain parameters.

    The domain parameters (p, g) are not secret; they are kept alongside x
    purely so that a decryption operation has everything it needs.
    """

    p: int
    g: int
    x: int

    def as_dict(self) -> dict:
        return {"p": str(self.p), "g": str(self.g), "x": str(self.x)}


@dataclass(frozen=True)
class KeyPair:
    """A matching (public, private) ElGamal key pair."""

    public: PublicKey
    private: PrivateKey


# ---------------------------------------------------------------------------
# Primality testing and prime generation
# ---------------------------------------------------------------------------

def is_probable_prime(n: int, rounds: int = MILLER_RABIN_ROUNDS) -> bool:
    """Return ``True`` if *n* is probably prime, ``False`` if it is composite.

    Uses trial division by small primes followed by the Miller-Rabin
    probabilistic primality test with randomly chosen bases.

    A ``False`` result is always correct (a witness of compositeness was
    found). A ``True`` result is correct with probability at least
    1 - 4^(-rounds).
    """
    if n < 2:
        return False
    for sp in _SMALL_PRIMES:
        if n == sp:
            return True
        if n % sp == 0:
            return False

    # Write n - 1 as d * 2^r with d odd.
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2          # random base in [2, n-2]
        v = pow(a, d, n)
        if v == 1 or v == n - 1:
            continue
        for _ in range(r - 1):
            v = pow(v, 2, n)
            if v == n - 1:
                break
        else:
            return False                           # definitely composite
    return True


def _passes_trial_division(n: int) -> bool:
    """Cheap pre-filter: reject *n* if it is divisible by a small prime.

    Roughly 80 percent of random odd candidates are eliminated by this test at
    a tiny fraction of the cost of one Miller-Rabin round, which is what makes
    safe-prime generation practical at 1024 bits and above.
    """
    for sp in _SMALL_PRIMES:
        if n == sp:
            return True
        if n % sp == 0:
            return False
    return True


def generate_prime(bits: int) -> int:
    """Generate a random probable prime with exactly *bits* bits.

    The top and bottom bits are forced to 1 so that the result always has the
    requested bit length and is odd.
    """
    if bits < 8:
        raise InvalidParameterError("Prime size must be at least 8 bits.")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def generate_safe_prime(bits: int) -> Tuple[int, int]:
    """Generate a safe prime ``p = 2q + 1`` and return ``(p, q)``.

    A safe prime is a prime p for which q = (p-1)/2 is also prime. Safe primes
    are used here because the factorisation of p-1 is then fully known
    (p - 1 = 2 * q), which makes it cheap and certain to verify that a
    candidate element is a generator of Z_p*. It also guarantees that Z_p*
    contains no small subgroups other than {1, p-1}, so the discrete logarithm
    problem cannot be reduced to small subgroups via the Pohlig-Hellman
    algorithm.

    Safe-prime search is significantly slower than ordinary prime search,
    which is why key generation time grows sharply with key size.
    """
    if bits < MIN_KEY_BITS:
        raise InvalidParameterError(
            f"Key size must be at least {MIN_KEY_BITS} bits."
        )
    while True:
        # Candidate q with the requested size, forced odd and full length.
        q = secrets.randbits(bits - 1) | (1 << (bits - 2)) | 1
        p = 2 * q + 1
        if p.bit_length() != bits:
            continue

        # Stage 1: trial division on both candidates (very cheap).
        if not _passes_trial_division(q) or not _passes_trial_division(p):
            continue
        # Stage 2: a few Miller-Rabin rounds to discard most composites fast.
        if not is_probable_prime(q, rounds=5):
            continue
        if not is_probable_prime(p, rounds=5):
            continue
        # Stage 3: full-confidence testing on the surviving pair.
        if is_probable_prime(q) and is_probable_prime(p):
            return p, q


def find_generator(p: int, q: int) -> int:
    """Find a generator g of the full multiplicative group Z_p*.

    For a safe prime p = 2q + 1 the group order is p - 1 = 2q, whose only
    prime factors are 2 and q. An element g is therefore a generator exactly
    when ``g^2 mod p != 1`` and ``g^q mod p != 1``.
    """
    if p < 5:
        raise InvalidParameterError("Modulus p is too small.")
    while True:
        g = secrets.randbelow(p - 3) + 2           # candidate in [2, p-2]
        if pow(g, 2, p) == 1:
            continue
        if pow(g, q, p) == 1:
            continue
        return g


# ---------------------------------------------------------------------------
# Modular inverse
# ---------------------------------------------------------------------------

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Return ``(g, s, t)`` such that ``g = gcd(a, b) = a*s + b*t``.

    Implemented iteratively to avoid Python recursion-depth limits on large
    inputs.
    """
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def mod_inverse(a: int, m: int) -> int:
    """Return the modular multiplicative inverse of *a* modulo *m*.

    That is, the unique value ``a_inv`` in [1, m-1] with
    ``a * a_inv = 1 (mod m)``. The inverse exists only when gcd(a, m) = 1.

    The Extended Euclidean Algorithm is used rather than Fermat's little
    theorem so that the classical algorithm taught in the course is visible in
    the implementation. Both approaches are correct for prime m.
    """
    a %= m
    if a == 0:
        raise InvalidParameterError("0 has no modular inverse.")
    g, s, _ = extended_gcd(a, m)
    if g != 1:
        raise InvalidParameterError(
            f"No modular inverse exists: gcd({a}, {m}) = {g}."
        )
    return s % m


# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------

def generate_keypair(bits: int = 512) -> KeyPair:
    """Generate an ElGamal key pair with a modulus of *bits* bits.

    Steps (standard ElGamal key generation):
        1. Choose a large safe prime p = 2q + 1.
        2. Choose a generator g of Z_p*.
        3. Choose a private key x uniformly at random from [2, p-2].
        4. Compute y = g^x mod p.
        5. Publish (p, g, y); keep x secret.
    """
    if bits < MIN_KEY_BITS:
        raise InvalidParameterError(
            f"Key size must be at least {MIN_KEY_BITS} bits."
        )
    p, q = generate_safe_prime(bits)
    g = find_generator(p, q)
    x = secrets.randbelow(p - 3) + 2               # private key in [2, p-2]
    y = pow(g, x, p)
    return KeyPair(public=PublicKey(p=p, g=g, y=y),
                   private=PrivateKey(p=p, g=g, x=x))


def validate_public_key(key: PublicKey) -> None:
    """Raise :class:`InvalidParameterError` if *key* is structurally invalid.

    The checks performed are sanity checks on ranges and primality; they do
    not and cannot prove that the key was generated honestly.
    """
    if key.p < MIN_KEY_BITS:
        raise InvalidParameterError("Modulus p is too small to be usable.")
    if not is_probable_prime(key.p):
        raise InvalidParameterError("Modulus p is not prime.")
    if not (2 <= key.g <= key.p - 2):
        raise InvalidParameterError("Generator g is out of range.")
    if not (1 <= key.y <= key.p - 1):
        raise InvalidParameterError("Public value y is out of range.")


# ---------------------------------------------------------------------------
# Encryption and decryption of a single integer
# ---------------------------------------------------------------------------

def encrypt_int(m: int, key: PublicKey) -> Tuple[int, int]:
    """Encrypt the integer *m* under the public key and return ``(c1, c2)``.

    A fresh ephemeral exponent k is drawn from the system CSPRNG on every
    call, which is what makes ElGamal a probabilistic (randomised) cipher:
    encrypting the same plaintext twice normally yields different ciphertexts.

    Raises:
        MessageTooLargeError: if m is not in the range 0 < m < p.
    """
    p = key.p
    if not isinstance(m, int):
        raise InvalidParameterError("Message must be an integer.")
    if m <= 0 or m >= p:
        raise MessageTooLargeError(
            f"Message integer must satisfy 0 < m < p "
            f"(m has {m.bit_length()} bits, p has {p.bit_length()} bits)."
        )
    k = secrets.randbelow(p - 3) + 2               # ephemeral k in [2, p-2]
    c1 = pow(key.g, k, p)
    c2 = (m * pow(key.y, k, p)) % p
    return c1, c2


def decrypt_int(c1: int, c2: int, key: PrivateKey) -> int:
    """Decrypt the ciphertext pair ``(c1, c2)`` and return the integer m.

    Correctness:
        s   = c1^x    = (g^k)^x = g^(kx) (mod p)
        y^k = (g^x)^k = g^(xk)           (mod p)
        so s = y^k, and
        c2 * s^-1 = m * y^k * (y^k)^-1 = m (mod p).
    """
    p = key.p
    if not (1 <= c1 <= p - 1) or not (1 <= c2 <= p - 1):
        raise DecryptionError(
            "Ciphertext component is outside the valid range [1, p-1]."
        )
    s = pow(c1, key.x, p)
    s_inv = mod_inverse(s, p)
    return (c2 * s_inv) % p


# ---------------------------------------------------------------------------
# Block-level encryption of a list of integers
# ---------------------------------------------------------------------------

def encrypt_blocks(blocks: List[int], key: PublicKey) -> List[Tuple[int, int]]:
    """Encrypt a list of message integers, one ElGamal operation per block."""
    return [encrypt_int(m, key) for m in blocks]


def decrypt_blocks(pairs: List[Tuple[int, int]],
                   key: PrivateKey) -> List[int]:
    """Decrypt a list of ``(c1, c2)`` pairs back into message integers."""
    return [decrypt_int(c1, c2, key) for c1, c2 in pairs]
