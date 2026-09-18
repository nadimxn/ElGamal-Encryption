"""
main.py
=======

Entry point for the ElGamal Encryption Implementation.

Run from the project root with:

    python main.py

Command-line options:

    python main.py --selftest    run a headless key/encrypt/decrypt round trip
                                 and report PASS or FAIL, without opening the
                                 interface. Used to verify a packaged build.
    python main.py --version     print the application version and exit.

The application requires Python 3.8 or later with the standard library only
(Tkinter ships with the official CPython installer on Windows and macOS; on
Debian/Ubuntu it is provided by the ``python3-tk`` package).
"""

from __future__ import annotations

import sys

APP_NAME = "ElGamal Encryption Implementation"
APP_VERSION = "1.0.0"


def _emit(line: str, sink) -> None:
    """Print a line and also record it in the log file.

    A windowed (``console=False``) build has no console attached, so printing
    may be unavailable or invisible depending on how the program was started.
    The log file makes the result readable in every case, and is what the CI
    workflow inspects.
    """
    try:
        print(line)
    except Exception:                               # no usable stdout
        pass
    if sink is not None:
        try:
            sink.write(line + "\n")
        except Exception:
            pass


def selftest() -> int:
    """Exercise the cryptographic core without the interface.

    Generates a key pair, encrypts and decrypts two messages, and checks that
    repeated encryption of the same plaintext produces different ciphertexts.
    Returns 0 if every check passes, 1 otherwise. This exists so that a
    packaged executable can be verified automatically, including in CI where
    no display is available.
    """
    import os
    log_path = os.path.join(os.getcwd(), "elgamal_selftest.log")
    try:
        sink = open(log_path, "w", encoding="utf-8")
    except OSError:
        sink = None

    try:
        from crypto_utils import decrypt_text, encrypt_text
        from elgamal import generate_keypair
    except ImportError as exc:
        _emit(f"SELFTEST FAIL: could not import the application modules: {exc}",
              sink)
        if sink:
            sink.close()
        return 1

    checks = []
    try:
        _emit(f"{APP_NAME} {APP_VERSION} - self test", sink)
        _emit("Generating a 512-bit key pair...", sink)
        keypair = generate_keypair(512)
        public, private = keypair.public, keypair.private
        checks.append(("key pair satisfies y = g^x mod p",
                       pow(public.g, private.x, public.p) == public.y))

        short_message = "Hello, ElGamal!"
        cipher = encrypt_text(short_message, public)
        checks.append(("short message round trip",
                       decrypt_text(cipher, private) == short_message))

        long_message = ("CCS2243 Cryptography Essential. " * 40) + "End."
        long_cipher = encrypt_text(long_message, public)
        checks.append(("long multi-block round trip",
                       decrypt_text(long_cipher, private) == long_message))

        unicode_message = "UTF-8: cafe, 密碼學, 3.14159, !@#$%^&*()"
        unicode_cipher = encrypt_text(unicode_message, public)
        checks.append(("UTF-8 round trip",
                       decrypt_text(unicode_cipher, private) == unicode_message))

        again = encrypt_text(short_message, public)
        checks.append(("repeated encryption differs (fresh ephemeral k)",
                       again != cipher))
        checks.append(("second ciphertext also decrypts",
                       decrypt_text(again, private) == short_message))

        try:
            encrypt_text("", public)
            checks.append(("empty plaintext rejected", False))
        except Exception:
            checks.append(("empty plaintext rejected", True))

        try:
            decrypt_text("not-a-ciphertext", private)
            checks.append(("malformed ciphertext rejected", False))
        except Exception:
            checks.append(("malformed ciphertext rejected", True))

    except Exception as exc:                        # pragma: no cover
        _emit(f"SELFTEST FAIL: unexpected error: {type(exc).__name__}: {exc}",
              sink)
        if sink:
            sink.close()
        return 1

    for name, ok in checks:
        _emit(f"  [{'PASS' if ok else 'FAIL'}] {name}", sink)

    failed = [name for name, ok in checks if not ok]
    if failed:
        _emit(f"\nSELFTEST FAIL: {len(failed)} of {len(checks)} checks failed.",
              sink)
        if sink:
            sink.close()
        return 1
    _emit(f"\nSELFTEST PASS: all {len(checks)} checks passed.", sink)
    _emit(f"Log written to {log_path}", sink)
    if sink:
        sink.close()
    return 0


def main() -> int:
    if sys.version_info < (3, 8):
        print("Python 3.8 or later is required.", file=sys.stderr)
        return 1

    args = sys.argv[1:]
    if "--version" in args:
        print(f"{APP_NAME} {APP_VERSION}")
        return 0
    if "--selftest" in args:
        return selftest()

    try:
        from gui import launch
    except ImportError as exc:
        print(
            "Tkinter is not available in this Python installation.\n"
            f"Details: {exc}\n"
            "On Windows, reinstall Python with the 'tcl/tk and IDLE' option.\n"
            "On Debian/Ubuntu, run: sudo apt install python3-tk",
            file=sys.stderr,
        )
        return 1
    launch()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
