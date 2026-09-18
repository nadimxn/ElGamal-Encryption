"""
main.py
=======

Entry point for the ElGamal Encryption Implementation.

Run from the project root with:

    python main.py

The application requires Python 3.8 or later with the standard library only
(Tkinter ships with the official CPython installer on Windows and macOS; on
Debian/Ubuntu it is provided by the ``python3-tk`` package).
"""

from __future__ import annotations

import sys


def main() -> int:
    if sys.version_info < (3, 8):
        print("Python 3.8 or later is required.", file=sys.stderr)
        return 1
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
