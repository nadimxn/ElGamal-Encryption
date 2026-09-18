# ElGamal Encryption Implementation

A Python-based secure message encryption and decryption application built on the
ElGamal public-key cryptosystem, with a Tkinter desktop interface.

**Repository:** `[INSERT ACTUAL GITHUB URL]`

| | |
|---|---|
| Student | S M Nadim Mahmud |
| Student ID | AIU24102398 |
| Section | BCS2A-D |
| Course | CCS2243 – Cryptography Essential |
| Programme | Bachelor in Computer Science (Honours) |
| Semester / Session | 3 / 2025–2026 |
| Lecturer | Prof. Dr. Khalid Hussain |
| University | Albukhary International University |

---

## Academic purpose and honest scope

This project was written for a university cryptography assessment. It is an
**educational implementation**, not a production security product.

What that means in practice:

- The ElGamal mathematics is implemented from first principles so that the
  algorithm can be inspected, explained and defended, rather than hidden inside
  a library call.
- The implementation is *textbook* ElGamal. It provides confidentiality under
  the discrete logarithm and Decisional Diffie–Hellman assumptions, but it
  provides **no integrity and no authentication**, and it is **malleable**.
- Private keys, if exported, are written as **unencrypted JSON**.
- Key sizes below 2048 bits are offered because they make a live demonstration
  feasible. They are **not** adequate for real protection.

Do not use this code to protect anything that matters.

---

## Features

- Key pair generation at 256, 512, 1024 or 2048 bits using safe primes
  (`p = 2q + 1`) and a verified generator of `Z_p*`
- Miller–Rabin probabilistic primality testing with trial-division pre-filtering
- Text encryption and decryption with correct block handling, so that the
  requirement `0 < m < p` always holds and never fails silently
- Fresh ephemeral `k` drawn from the operating system CSPRNG on every block of
  every encryption, demonstrating probabilistic encryption
- Modular inverse by the Extended Euclidean Algorithm
- Input validation and specific, readable error messages for every failure path
- Optional key export/import as JSON, with a public/private consistency check
  (`g^x mod p == y`)
- 88 automated tests (unit, integration, boundary, invalid-input)
- Reproducible benchmark script with CSV output and graph generation

---

## Architecture

```
User
 └─ gui.py ................. Tkinter presentation layer, input validation
     └─ crypto_utils.py .... UTF-8 encoding, block splitting, ciphertext format
         └─ elgamal.py ..... primes, generator, keygen, encrypt, decrypt, inverse
     └─ key_manager.py ..... in-memory key pair, JSON export/import
             └─ secrets .... operating system CSPRNG
```

No database, no network service and no third-party cryptographic library are
used. `elgamal.py` depends only on Python's built-in integer arithmetic and the
standard-library `secrets` module.

---

## How the cryptography works

**Key generation**

1. Generate a safe prime `p = 2q + 1`.
2. Find `g` with `g^2 mod p != 1` and `g^q mod p != 1` (a generator of `Z_p*`).
3. Choose a private key `x` at random from `[2, p-2]`.
4. Compute `y = g^x mod p`.

Public key `(p, g, y)`; private key `x`.

**Encryption of a message integer `m`, `0 < m < p`**

```
k  = fresh random value in [2, p-2]      (new for every block)
c1 = g^k mod p
c2 = m * y^k mod p
```

**Decryption**

```
s  = c1^x mod p
m  = c2 * s^(-1) mod p
```

**Why it works**

`s = c1^x = (g^k)^x = g^(kx)` and `y^k = (g^x)^k = g^(xk)`, so `s = y^k`.
Therefore `c2 * s^(-1) = m * y^k * (y^k)^(-1) = m (mod p)`.

**Message representation**

```
text → UTF-8 bytes → blocks of (bit_length(p) - 1)//8 - 1 bytes
     → 0x01 prefix → integer m < p → ElGamal → "c1:c2" hex, one block per line
```

The `0x01` prefix preserves leading zero bytes and guarantees `m != 0`. The
block size is derived from `p` so that `m < p` holds for every possible byte
pattern, rather than being assumed.

---

## Installation

Requires **Python 3.8 or later**. Tkinter ships with the official Python
installer on Windows and macOS; on Debian/Ubuntu install `python3-tk`.

```bash
git clone [INSERT ACTUAL GITHUB URL]
cd ElGamal-Encryption

# The application itself needs no third-party packages.
# For the test suite and the benchmark graph:
pip install -r requirements.txt
```

## Running

```bash
python main.py                    # launch the GUI
python -m pytest tests -v         # run the test suite
python benchmark.py               # run the performance benchmark
python diagrams/make_diagrams.py  # regenerate the draw.io diagram sources
```

---

## Project structure

```
ElGamal-Encryption/
├── main.py                 Entry point
├── gui.py                  Tkinter interface
├── elgamal.py              Core ElGamal mathematics
├── crypto_utils.py         Message encoding and ciphertext format
├── key_manager.py          Key storage, export and import
├── benchmark.py            Performance measurement
├── requirements.txt
├── README.md
├── tests/
│   ├── test_elgamal.py         Core mathematics
│   ├── test_crypto_utils.py    Encoding and round trips
│   └── test_validation.py      Validation, errors, key files
├── diagrams/
│   ├── make_diagrams.py
│   ├── system_architecture.drawio
│   ├── use_case.drawio
│   ├── dfd.drawio
│   ├── system_flowchart.drawio
│   ├── key_generation_flowchart.drawio
│   ├── encryption_flowchart.drawio
│   ├── decryption_flowchart.drawio
│   └── class_diagram.drawio
├── docs/
│   ├── REPORT_DRAFT.md
│   ├── USER_GUIDE.md
│   ├── TEST_PLAN.md
│   ├── SCREENSHOT_PLAN.md
│   ├── PRESENTATION_AND_VIVA.md
│   └── AUDITS.md
├── results/                Benchmark CSVs, graph, test log
└── screenshots/            [TO BE POPULATED BY ACTUAL EXECUTION]
```

---

## Testing

```bash
python -m pytest tests -v
```

88 tests covering primality testing, safe-prime structure, generator order,
modular inverse, key generation, integer round trips, probabilistic encryption,
`m >= p` rejection, text round trips including Unicode and long inputs,
ciphertext format errors, wrong-key behaviour, and key file handling.

A reference run inside the development container reported **88 passed**. The
run on the submission machine must be repeated and captured; see
`docs/SCREENSHOT_PLAN.md`.

---

## Security considerations and limitations

| Property | Status in this implementation |
|---|---|
| Confidentiality | Yes, under the DLP/DDH assumptions and with adequate key size |
| Integrity | **No.** A modified ciphertext is not detected |
| Authentication | **No.** Anyone with the public key can encrypt |
| Non-repudiation | **No.** No signature scheme is implemented |
| IND-CPA (semantic security) | **Not achieved as configured** — see below |
| IND-CCA | **No.** Textbook ElGamal is malleable |
| Ciphertext expansion | Approximately 2x in group elements, ~4x after hex encoding |
| Private key at rest | Unencrypted JSON if exported |

**On semantic security.** Tsiounis and Yung (1998) proved that ElGamal is
semantically secure under the Decisional Diffie–Hellman assumption *when
messages are drawn from a prime-order subgroup*. This implementation uses a
generator of the full group `Z_p*` so that arbitrary byte blocks can be
encrypted directly. The consequence is that the Legendre symbol of the
plaintext leaks, so the scheme as configured is **not** semantically secure in
the strict sense. This is a deliberate, documented trade-off in favour of a
simple and inspectable message encoding, and it is discussed in the report
rather than glossed over.

**Malleability.** Multiplying `c2` by `t` yields a valid ciphertext that
decrypts to `m * t mod p`. `tests/test_elgamal.py` contains a test that
demonstrates this explicitly.

**Ephemeral key reuse.** If the same `k` is used for two messages under the same
public key, then `c2/c2' = m/m'`, so an attacker who learns one plaintext learns
the other. The implementation draws a fresh `k` for every block of every
encryption from `secrets`.

---

## Screenshots

See `screenshots/`. `[INSERT ACTUAL SCREENSHOTS AFTER EXECUTION]`

---

## Acknowledgements and AI disclosure

Cryptographic definitions and algorithm structure follow ElGamal (1985),
Menezes, van Oorschot and Vanstone (1996), and Paar and Pelzl (2010); key-size
guidance follows NIST SP 800-57 Part 1 Rev. 5 (Barker, 2020). Full references
are in the report.

Generative AI assistance was used during development and must be disclosed in
accordance with the CCS2243 assessment instructions. The student is responsible
for understanding and being able to explain every part of the submitted work;
`docs/PRESENTATION_AND_VIVA.md` exists for that purpose.

## Licence

Submitted as coursework. No licence for reuse is granted or implied.
