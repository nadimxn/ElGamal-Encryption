# Presentation, Demonstration Script and Viva Preparation

Assessment weighting: Presentation, Demonstration & Q&A is 10% of the course
mark. The rubric rewards a confident, well-structured presentation, a working
live demonstration, and accurate answers about the cryptographic process,
design choices and code.

---

# PART A — PRESENTATION SLIDES (12 slides, ~12 minutes)

## Slide 1 — Title

> **ElGamal Encryption Implementation**
> A Python-Based Secure Message Encryption and Decryption Application
>
> S M Nadim Mahmud · AIU24102398 · BCS2A-D
> CCS2243 Cryptography Essential · Semester 3, 2025–2026
> Lecturer: Prof. Dr. Khalid Hussain
> Albukhary International University

**Speaker notes (30 s).** Introduce yourself and the project in one sentence:
"I implemented the ElGamal public-key cryptosystem from scratch in Python, with
a desktop interface, a test suite and a performance benchmark." Do not read the
slide aloud.

## Slide 2 — Background

> - Symmetric encryption requires a shared secret key — and a secure channel to
>   share it on
> - Diffie & Hellman (1976): separate public and private keys
> - RSA (1978): based on factoring — and **deterministic**
> - ElGamal (1985): based on the **discrete logarithm problem** — and
>   **probabilistic**
> - Goldwasser & Micali (1984): deterministic public-key encryption *cannot* be
>   semantically secure

**Speaker notes (60 s).** The key-distribution problem motivates public-key
cryptography. Emphasise the last point: randomised encryption is not a
decoration, it is a requirement, and ElGamal has it natively where RSA has to
add padding to get it.

## Slide 3 — Problem Statement

> Implementing a cryptosystem correctly requires decisions the formulae do not
> show:
> 1. **Message representation** — ElGamal encrypts `m` with `0 < m < p`. Text is
>    not an integer. Get this wrong and the failure is *silent*.
> 2. **Randomness** — a reused or predictable `k` breaks confidentiality while
>    everything still appears to work.
> 3. **Honest claims** — textbook ElGamal gives confidentiality only. No
>    integrity. No authentication.

**Speaker notes (60 s).** This slide is where you show you understand the
difference between knowing the formula and implementing it. Say plainly: my
project is about the decisions between the formula and the working program.

## Slide 4 — Aim and Objectives

> **Aim:** design, implement, test and critically evaluate a functional Python
> application performing ElGamal encryption and decryption.
>
> O1 Implement ElGamal from first principles (no crypto library)
> O2 Guarantee `0 < m < p` for arbitrary text
> O3 Build a Tkinter interface with validation and error handling
> O4 Use a fresh CSPRNG ephemeral `k` per encryption
> O5 Test systematically
> O6 Measure performance reproducibly
> O7 Evaluate security honestly

**Speaker notes (45 s).** Seven objectives, each with evidence in the report.
Flag O1: I did not call a library, so I can explain every line.

## Slide 5 — The ElGamal Algorithm

> **Key generation**
> `p = 2q + 1` safe prime · `g` a generator of `Z_p*` · `x` random ·
> `y = g^x mod p`
> Public `(p, g, y)` · Private `x`
>
> **Encryption** — fresh random `k` each time
> `c1 = g^k mod p` · `c2 = m · y^k mod p`
>
> **Decryption**
> `s = c1^x mod p` · `m = c2 · s⁻¹ mod p`
>
> **Why it works**
> `c1^x = g^(kx)` and `y^k = g^(xk)` — the same value, so `s⁻¹` cancels the mask

**Speaker notes (90 s).** Walk through the correctness argument slowly; this is
the single most likely viva question. Frame encryption as an in-line
Diffie–Hellman exchange: the sender does half a key agreement, uses the shared
value to mask the message, and sends their half alongside it.

## Slide 6 — System Architecture

> `[INSERT diagrams/system_architecture.png]`
>
> Tkinter GUI → Input validation → Message representation → ElGamal engine →
> Key management → OS CSPRNG
>
> No database. No network. No third-party cryptographic library.

**Speaker notes (45 s).** Four layers, one-directional dependencies. State
explicitly that there is no database, because the design deliberately does not
include one.

## Slide 7 — Design: solving the `m < p` problem

> `text → UTF-8 bytes → blocks → 0x01 prefix → integer m < p`
>
> `block_size(p) = (bit_length(p) − 1) // 8 − 1` bytes
>
> - Guarantees `m < p` **by construction**, for every possible input
> - The `0x01` prefix preserves leading zero bytes and guarantees `m ≠ 0`
> - 512-bit key → 62 bytes per block
>
> `[INSERT diagrams/encryption_flowchart.png]`

**Speaker notes (75 s).** Explain the arithmetic: a block plus its prefix
occupies at most `block_size + 1` bytes; the formula makes that at most
`bit_length(p) − 1` bits, hence strictly less than `p`. Then explain the
prefix: without it `b"\x00A"` and `b"A"` both become 65 and decoding is
ambiguous.

## Slide 8 — Implementation and Interface

> `[INSERT screenshots/02_key_generation.png]` and `[INSERT screenshots/04_encryption.png]`
>
> - `elgamal.py` — primes, generator, keygen, encrypt, decrypt, modular inverse
> - `crypto_utils.py` — encoding, blocks, ciphertext format
> - `key_manager.py` — key pair, JSON export/import with `g^x mod p == y` check
> - `gui.py` — Tkinter, worker thread for key generation
> - Randomness: `secrets`, never `random`

**Speaker notes (60 s).** Mention the threading decision: 1024-bit key
generation took a median of about 12 seconds, so it runs off the main thread
and posts back through a queue, because Tkinter widgets must only be touched by
the thread that created them.

## Slide 9 — Testing

> **88 automated tests**, three modules
>
> - Unit: primality (including Carmichael numbers), generator order, modular
>   inverse, key generation
> - Integration: round trips — ASCII, punctuation, digits, Unicode, emoji, null
>   bytes, 4,096 characters
> - Boundary: `m = 1`, `m = p`, `m = p+1`, `m = 0`, empty input
> - Negative: malformed ciphertext, wrong key, corrupted key files
> - **Tests that demonstrate weaknesses:** malleability, wrong-key failure
>
> `[INSERT screenshots/11_test_run.png]`

**Speaker notes (60 s).** Highlight the last bullet. Most projects test that
things work; I also wrote a test asserting that multiplying `c2` by 3 produces
a plaintext of `3m mod p`, which proves in code that the scheme has no
integrity protection.

## Slide 10 — Results

> `[INSERT results/benchmark_plot.png — your own run]`
>
> | Key size | Keygen (median) | Encrypt/block | Decrypt/block |
> |---|---|---|---|
> | 256 | `[YOUR FIGURE]` | | |
> | 512 | | | |
> | 1024 | | | |
>
> - Encryption ≈ **2×** decryption cost — two exponentiations versus one
> - Key generation is **thousands of times** more expensive than encryption
> - Ciphertext expansion ≈ 2:1 intrinsic, ≈ 4:1 after hex encoding

**Speaker notes (75 s).** Explain the 2:1 timing ratio from the algorithm, not
from the graph. Note that prime-search timing has huge variance because it is a
random search, which is why you report medians.

## Slide 11 — Security and Limitations

> **Provides:** confidentiality, under DLP/CDH, with an adequate key size
>
> **Does not provide:**
> - Integrity — a tampered ciphertext is undetectable (malleability)
> - Authentication or non-repudiation
> - Semantic security *as configured* — full `Z_p*` leaks the Legendre symbol
>   (Tsiounis & Yung, 1998, require a prime-order subgroup)
> - Chosen-ciphertext security
>
> **Also:** demo key sizes are below the 2048-bit minimum (Barker, 2020);
> exported private keys are unencrypted
>
> **This is an educational implementation. It is not production-ready.**

**Speaker notes (75 s).** Deliver this slide with confidence, not apology.
Knowing exactly what your system does not provide is the mark of a competent
security engineer, and the rubric rewards evaluating limitations.

## Slide 12 — Conclusion and Future Work

> All seven objectives achieved: working implementation, 88 tests passing,
> measured performance, honest security evaluation.
>
> **Future work**
> 1. Encrypt into a prime-order subgroup → restores semantic security
> 2. Encrypt-then-MAC, or Cramer–Shoup / DHIES → integrity and CCA security
> 3. Hybrid ElGamal + AES-GCM → removes expansion and cost for large messages
> 4. ElGamal signatures → authentication and non-repudiation
> 5. Encrypted private-key storage; elliptic-curve variant
>
> Thank you — questions welcome.

---

# PART B — LIVE DEMONSTRATION SCRIPT (~5 minutes)

**Before you start:** application already open at the home screen, terminal in
the project directory on a second window, a paragraph of test text on the
clipboard, and everything else closed. Have `512` pre-selected.

| # | Action | Say |
|---|---|---|
| 1 | Show the home screen | "Three panels: key generation, encryption, decryption, with a status bar." |
| 2 | Press **Encrypt** with no keys | "Validation first: it refuses to encrypt without a key pair, and says why." |
| 3 | Press **Generate Key Pair** (512) | "It is searching for a safe prime `p = 2q + 1`. The progress bar runs on a worker thread so the window stays responsive." |
| 4 | Show the values | "`p` is 155 decimal digits. `x` is the private key; `y = g^x mod p` is public. Recovering `x` from `y` is the discrete logarithm problem." |
| 5 | Press **Show Full Key Values** | "The complete numbers, if you want to see them." |
| 6 | Type the test message, **Encrypt** | "62 bytes per block at this key size, so this message becomes N blocks. Each line is `c1:c2` in hex." |
| 7 | Press **Encrypt** again | "Same message, same key — completely different ciphertext. A fresh random `k` is drawn for every block of every encryption. That is ElGamal being probabilistic." |
| 8 | **Copy to Decryption Pane**, **Decrypt** | "Exact recovery, including punctuation and spacing." |
| 9 | Delete a `:` from one line, **Decrypt** | "Malformed input is caught and the error names the line." |
| 10 | Reset, generate new keys, paste old ciphertext, **Decrypt** | "Wrong private key. It reports an error instead of returning garbage — the marker byte check catches it." |
| 11 | Terminal: `python -m pytest tests -v` | "88 tests: unit, integration, boundary, invalid input, and tests that demonstrate the scheme's weaknesses." |
| 12 | Terminal: show `results/benchmark_plot.png` | "Encryption costs about twice decryption, exactly as the algorithm predicts." |
| 13 | Close | "Correct, tested, measured — and confidentiality only. No integrity, no authentication. It is an educational implementation." |

**If something breaks:** stay calm, say what you expected and what happened,
and continue. Have `screenshots/` open in a folder as a fallback.

---

# PART C — VIVA QUESTIONS AND ANSWERS (27)

Answer in your own words. If you do not know something, say so and reason from
what you do know — that scores better than a confident wrong answer.

**1. Why did you choose ElGamal?**
It is a public-key scheme whose entire mathematics fits in a few dozen lines, so
I could implement it from first principles and explain every step. It is also
natively probabilistic, which let me demonstrate why randomised encryption
matters, and it is based on the discrete logarithm problem, which complements
the factoring-based RSA covered in the course.

**2. What is asymmetric cryptography?**
Encryption where two mathematically related but computationally independent keys
are used: a public key for encryption that anyone may hold, and a private key
for decryption held only by the recipient. It solves the key-distribution
problem of symmetric cryptography, at the cost of much slower operations.

**3. What is `p`?**
A large prime modulus. All arithmetic happens in `Z_p*`, the multiplicative
group of non-zero integers modulo `p`. I generate safe primes, `p = 2q + 1` with
`q` also prime.

**4. Why safe primes?**
Two reasons. The group order is `p − 1 = 2q`, which has one large prime factor,
so the Pohlig–Hellman attack — which reduces the discrete logarithm to
subgroups of small order — gains nothing. And because the factorisation of
`p − 1` is fully known, I can verify a generator cheaply and with certainty:
`g` is a generator exactly when `g² ≠ 1` and `g^q ≠ 1`.

**5. What is `g`?**
A generator of `Z_p*` — an element whose powers produce every element of the
group. My `find_generator` picks a random candidate and applies the two tests
above rather than assuming.

**6. What is `x`?**
The private key: a random integer in `[2, p−2]` drawn from the operating system
CSPRNG. It must never be disclosed.

**7. What is `y`?**
The public value `y = g^x mod p`. It is part of the public key `(p, g, y)`.
Computing `x` from `y` is the discrete logarithm problem.

**8. What is `k`?**
The ephemeral, one-time exponent chosen freshly for every encryption. It makes
the scheme probabilistic and must never be reused or predictable.

**9. What is the public key, and what is the private key?**
Public: `(p, g, y)`, may be published. Private: `x`, must be kept secret. `p`
and `g` are domain parameters and are not secret.

**10. Why must `k` be random?**
It is what makes encryption probabilistic. Without fresh randomness the same
plaintext always produces the same ciphertext, and an adversary who suspects a
message can encrypt it themselves and compare — so the scheme could not be
semantically secure.

**11. What happens if `k` is reused?**
If two messages `m` and `m'` are encrypted under the same key with the same `k`,
then `c1` is identical and `c2/c2' = m/m'`. An attacker who learns one plaintext
immediately recovers the other. This class of failure — a repeated nonce — is
how the PlayStation 3 ECDSA signing key was recovered. My implementation draws
`k` from `secrets` on every call to `encrypt_int`, once per block.

**12. Why `secrets` and not `random`?**
`random` is a Mersenne Twister designed for simulation. Its entire future output
can be reconstructed from 624 observed outputs, so an attacker who saw a few
ephemeral values could predict the rest and decrypt subsequent messages.
`secrets` draws on the operating system entropy source and is documented as the
module to use for security purposes.

**13. Walk me through encryption.**
Validate the plaintext is non-empty and a key exists. Encode as UTF-8. Split
into blocks of `(bit_length(p) − 1)//8 − 1` bytes. Prefix each block with `0x01`
and convert to an integer `m`, which is guaranteed less than `p`. For each
block draw a fresh `k`, compute `c1 = g^k mod p` and `c2 = m·y^k mod p`, and
serialise the pair as hex.

**14. Walk me through decryption.**
Parse each line into `c1` and `c2`, checking they are valid hex and in
`[1, p−1]`. Compute `s = c1^x mod p`, invert `s` modulo `p` with the Extended
Euclidean Algorithm, compute `m = c2·s⁻¹ mod p`, convert to bytes, verify and
strip the `0x01` marker, concatenate the blocks and decode as UTF-8.

**15. Why does decryption work?**
`s = c1^x = (g^k)^x = g^(kx)` and `y^k = (g^x)^k = g^(xk)`. Multiplication of
exponents commutes, so `s = y^k`. Therefore `c2·s⁻¹ = m·y^k·(y^k)⁻¹ = m mod p`.

**16. Why is a modular inverse needed, and how did you compute it?**
The message is masked by *multiplication* by `y^k`, so it is unmasked by
multiplying by the multiplicative inverse of that value. I used the Extended
Euclidean Algorithm, which returns `s, t` with `as + mt = gcd(a, m)`; when the
gcd is 1, `s mod m` is the inverse. Fermat's little theorem would also work
because `p` is prime, but the Euclidean algorithm is the general method and it
makes the failure case explicit.

**17. What is the discrete logarithm problem?**
Given `p`, a generator `g`, and `y = g^x mod p`, find `x`. Exponentiation is
cheap by square-and-multiply, roughly `O(log x)` multiplications, but no
efficient classical algorithm is known for the inverse; the best general methods
run in sub-exponential time. ElGamal's security rests on that asymmetry.

**18. Why does the same plaintext produce different ciphertexts?**
Because `k` is fresh each time. `c1 = g^k` changes, and `c2 = m·y^k` changes
with it. Both change consistently, so decryption still recovers the same `m`.
Test `test_encryption_is_probabilistic` confirms 20 encryptions give 20 distinct
ciphertexts, all decrypting correctly.

**19. What if the private key is exposed?**
Every message ever encrypted under the corresponding public key can be
decrypted — past and future. There is no forward secrecy. My exported private
key files are unencrypted JSON, which I flag as an educational limitation; a
real system would encrypt them with a passphrase-derived key or use an OS
keystore.

**20. What happens if the ciphertext is modified?**
It decrypts to something else, and the modification is not detected. ElGamal is
malleable: `(c1, t·c2)` decrypts to `t·m mod p`. I have a test that asserts
exactly this with `t = 3`. In my implementation an arbitrary tamper usually
trips the `0x01` marker check and produces an error — but that is an accident of
my encoding, not integrity protection, and a deliberate attacker who chose `t`
carefully could avoid it.

**21. Does ElGamal provide integrity or authentication?**
No. Neither. Textbook ElGamal provides confidentiality only. Integrity requires
a MAC or an authenticated construction; authentication requires a signature
scheme. Anyone holding the public key can produce a valid ciphertext, so you
cannot tell who encrypted a message.

**22. Is your system semantically secure?**
Not as configured, and I want to be precise about this. Tsiounis and Yung
proved ElGamal's semantic security is equivalent to the Decisional
Diffie–Hellman assumption *when messages come from a prime-order subgroup*. I
use a generator of the full group `Z_p*` so that arbitrary byte blocks map
directly to group elements, which means `c2` reveals the Legendre symbol of the
plaintext. One bit leaks per block. Encrypting into the subgroup of quadratic
residues would fix it, and that is the first item in my future work.

**23. What are ElGamal's main limitations?**
Ciphertext is twice the plaintext size in group elements. Encryption needs two
full-width exponentiations where RSA with a small public exponent needs roughly
one. Security is critically dependent on ephemeral freshness. No integrity, no
authentication, no CCA security. And, like RSA, it falls to Shor's algorithm on
a sufficiently large quantum computer.

**24. What happens if the plaintext is too large?**
It cannot be — that is the point of the block design. The block size is derived
from `bit_length(p)` so that every block integer is strictly less than `p` by
construction. I also kept an explicit check that raises `MessageTooLargeError`
for `m ≥ p` or `m ≤ 0`, as a defensive assertion. A naive implementation that
converted the whole message to one integer would have it silently reduced
modulo `p` and destroyed.

**25. How did you test the system?**
88 automated tests in three modules, run with pytest. Unit tests for primality —
including Carmichael numbers 561 and 1105, which defeat the Fermat test but not
Miller–Rabin — generator order, and modular inverse. Integration tests for text
round trips including Unicode, emoji, embedded nulls and 4,096-character inputs.
Boundary tests at `m = 1`, `m = p`, `m = p+1`, `m = 0` and block boundaries.
Negative tests for malformed ciphertext, wrong keys and corrupted key files.
Plus GUI behaviours verified manually.

**26. How did you measure performance, and what did you find?**
`benchmark.py` uses `time.perf_counter`, reports medians and spread over
repeated trials, and writes CSVs plus a graph. Key generation grows very
steeply with key size and has enormous variance, because prime search is a
random process — that is why I report medians. Encryption costs about twice
decryption at every size, which matches the algorithm: two exponentiations
versus one.

**27. Is it production-ready, and what would you improve?**
No, and I would not describe it as such. It is an educational implementation:
textbook ElGamal with demonstration key sizes, no integrity, and unencrypted
key storage. To move toward production I would encrypt into a prime-order
subgroup to restore semantic security, add encrypt-then-MAC or move to
Cramer–Shoup or DHIES for chosen-ciphertext security, use hybrid encryption
with AES-GCM so large messages are practical, enforce 2048-bit minimum keys per
NIST SP 800-57, encrypt the stored private key, and address side channels with
constant-time arithmetic.

---

## Likely follow-up questions worth rehearsing

- *Show me where in the code `k` is generated.* → `elgamal.py`,
  `encrypt_int`, the line `k = secrets.randbelow(p - 3) + 2`.
- *Why `randbelow(p - 3) + 2`?* → `randbelow(n)` returns `[0, n−1]`, so this
  gives a uniform value in `[2, p−2]`.
- *Why 40 Miller–Rabin rounds?* → Error probability at most `4⁻⁴⁰`, which is
  negligible; the staged search uses 5 rounds first only as a cheap filter, and
  survivors still get the full test.
- *What is the block size for a 512-bit key?* → 62 bytes.
- *Why is the ciphertext four times the plaintext rather than twice?* → Two
  group elements is the intrinsic 2:1; the hex transport encoding doubles it
  again. Raw bytes would be 2:1.
- *Did you use AI assistance?* → Answer honestly and specifically, per the
  assessment's academic integrity requirements, and be ready to demonstrate
  your understanding of any part of the code.
