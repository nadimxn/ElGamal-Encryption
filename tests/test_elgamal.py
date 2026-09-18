"""
tests/test_elgamal.py
=====================

Unit tests for the core ElGamal mathematics (elgamal.py).

Run from the project root with:  python -m pytest tests -v
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from elgamal import (                                          # noqa: E402
    DecryptionError,
    InvalidParameterError,
    MessageTooLargeError,
    decrypt_int,
    encrypt_int,
    extended_gcd,
    find_generator,
    generate_keypair,
    generate_prime,
    generate_safe_prime,
    is_probable_prime,
    mod_inverse,
    validate_public_key,
)

TEST_BITS = 256          # small enough for a fast test run, large enough to be meaningful


@pytest.fixture(scope="module")
def keypair():
    """One key pair shared by the tests in this module (generation is slow)."""
    return generate_keypair(TEST_BITS)


# ---------------------------------------------------------------------------
# TC-U01 .. TC-U04  Primality and prime generation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [2, 3, 5, 7, 13, 97, 7919, 104729])
def test_known_primes_are_reported_prime(value):
    assert is_probable_prime(value) is True


@pytest.mark.parametrize("value", [0, 1, 4, 9, 15, 100, 561, 1105, 7917])
def test_composites_and_units_are_rejected(value):
    # 561 and 1105 are Carmichael numbers: they fool the Fermat test but not
    # Miller-Rabin.
    assert is_probable_prime(value) is False


def test_generate_prime_has_requested_bit_length():
    p = generate_prime(128)
    assert p.bit_length() == 128
    assert is_probable_prime(p)


def test_safe_prime_structure():
    p, q = generate_safe_prime(128)
    assert p == 2 * q + 1
    assert is_probable_prime(p) and is_probable_prime(q)
    assert p.bit_length() == 128


# ---------------------------------------------------------------------------
# TC-U05 .. TC-U06  Generator selection
# ---------------------------------------------------------------------------

def test_generator_has_full_order():
    p, q = generate_safe_prime(128)
    g = find_generator(p, q)
    # For p = 2q + 1 the order of g divides 2q. g is a generator iff it is
    # neither of order 1, 2 nor q.
    assert pow(g, 2, p) != 1
    assert pow(g, q, p) != 1
    assert pow(g, 2 * q, p) == 1          # Fermat's little theorem


# ---------------------------------------------------------------------------
# TC-U07 .. TC-U09  Modular inverse
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a,m", [(3, 11), (10, 17), (7, 13), (123456, 1000003)])
def test_mod_inverse_is_correct(a, m):
    assert (a * mod_inverse(a, m)) % m == 1


def test_mod_inverse_rejects_non_coprime_input():
    with pytest.raises(InvalidParameterError):
        mod_inverse(4, 8)


def test_extended_gcd_bezout_identity():
    g, s, t = extended_gcd(240, 46)
    assert g == 2
    assert 240 * s + 46 * t == g


# ---------------------------------------------------------------------------
# TC-U10 .. TC-U12  Key generation
# ---------------------------------------------------------------------------

def test_keypair_satisfies_y_equals_g_pow_x(keypair):
    pub, priv = keypair.public, keypair.private
    assert pow(pub.g, priv.x, pub.p) == pub.y


def test_keypair_modulus_has_requested_size(keypair):
    assert keypair.public.bit_length == TEST_BITS


def test_private_exponent_in_valid_range(keypair):
    assert 1 < keypair.private.x < keypair.public.p - 1


def test_validate_public_key_accepts_generated_key(keypair):
    validate_public_key(keypair.public)          # must not raise


def test_generate_keypair_rejects_tiny_key_size():
    with pytest.raises(InvalidParameterError):
        generate_keypair(32)


# ---------------------------------------------------------------------------
# TC-U13 .. TC-U16  Encryption and decryption of integers
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("m", [1, 2, 42, 65537, 2 ** 100 + 7])
def test_integer_round_trip(m, keypair):
    c1, c2 = encrypt_int(m, keypair.public)
    assert decrypt_int(c1, c2, keypair.private) == m


def test_ciphertext_components_are_in_group(keypair):
    c1, c2 = encrypt_int(12345, keypair.public)
    p = keypair.public.p
    assert 1 <= c1 < p and 1 <= c2 < p


def test_encryption_is_probabilistic(keypair):
    """Same plaintext + same key should give different ciphertexts."""
    m = 987654321
    results = {encrypt_int(m, keypair.public) for _ in range(20)}
    assert len(results) == 20, (
        "Repeated encryptions produced a duplicate ciphertext, which would "
        "indicate that the ephemeral value k is being reused."
    )
    # Every one of them must still decrypt to the original message.
    for c1, c2 in results:
        assert decrypt_int(c1, c2, keypair.private) == m


def test_message_equal_to_or_larger_than_p_is_rejected(keypair):
    p = keypair.public.p
    with pytest.raises(MessageTooLargeError):
        encrypt_int(p, keypair.public)
    with pytest.raises(MessageTooLargeError):
        encrypt_int(p + 1, keypair.public)


def test_zero_and_negative_messages_are_rejected(keypair):
    with pytest.raises(MessageTooLargeError):
        encrypt_int(0, keypair.public)
    with pytest.raises(MessageTooLargeError):
        encrypt_int(-5, keypair.public)


# ---------------------------------------------------------------------------
# TC-U17 .. TC-U19  Failure behaviour
# ---------------------------------------------------------------------------

def test_out_of_range_ciphertext_is_rejected(keypair):
    p = keypair.public.p
    with pytest.raises(DecryptionError):
        decrypt_int(p, 5, keypair.private)
    with pytest.raises(DecryptionError):
        decrypt_int(5, 0, keypair.private)


def test_wrong_private_key_does_not_recover_plaintext(keypair):
    """Decrypting with a different x gives a wrong value, not the plaintext."""
    other = generate_keypair(TEST_BITS)
    m = 1234567
    c1, c2 = encrypt_int(m, keypair.public)
    # Use the wrong x but the correct domain parameters, so that the
    # arithmetic still runs and the failure is cryptographic, not structural.
    from elgamal import PrivateKey
    wrong = PrivateKey(p=keypair.public.p, g=keypair.public.g,
                       x=other.private.x)
    assert decrypt_int(c1, c2, wrong) != m


def test_modified_ciphertext_changes_plaintext_predictably(keypair):
    """ElGamal is malleable: multiplying c2 by t multiplies m by t.

    This test documents a real weakness of textbook ElGamal rather than a
    feature of this implementation.
    """
    p = keypair.public.p
    m = 1000
    c1, c2 = encrypt_int(m, keypair.public)
    tampered_c2 = (c2 * 3) % p
    assert decrypt_int(c1, tampered_c2, keypair.private) == (m * 3) % p
