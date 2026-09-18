# ElGamal Encryption Implementation: A Python-Based Secure Message Encryption and Decryption Application

**Report draft — CCS2243 Cryptography Essential, Assessment 1 (Individual Project, 20%)**

> **How to use this draft.** Everything here is written to be submitted, with
> two exceptions that are marked throughout in square brackets:
> `[INSERT ...]` marks evidence that only exists once *you* run the software
> (screenshots, your machine's timings, your GitHub URL), and
> `[TO BE VERIFIED BY ACTUAL EXECUTION]` marks test outcomes that must be
> confirmed on your machine. Performance figures quoted in Chapter 6 are from a
> reference run on the development container, are labelled as such, and **must
> be replaced** with figures from your own machine.

---

## Title Page

**ELGAMAL ENCRYPTION IMPLEMENTATION: A PYTHON-BASED SECURE MESSAGE ENCRYPTION AND DECRYPTION APPLICATION**

Submitted in partial fulfilment of the requirements for
CCS2243 – Cryptography Essential

**Student:** S M Nadim Mahmud
**Student ID:** AIU24102398
**Section:** BCS2A-D
**Programme:** Bachelor in Computer Science (Honours)
**Semester:** 3
**Academic Session:** 2025–2026
**Lecturer:** Prof. Dr. Khalid Hussain
**Institution:** Albukhary International University

**Date of submission:** `[INSERT DATE]`

---

## Abstract

This project designs, implements, tests and evaluates a desktop application
that performs message encryption and decryption using the ElGamal public-key
cryptosystem. The application is written in Python with a Tkinter graphical
interface, and the entire cryptosystem — safe-prime generation, generator
selection, key generation, modular exponentiation, modular inversion,
encryption and decryption — is implemented directly from Python's integer
arithmetic rather than delegated to a cryptographic library, so that the
algorithm can be inspected and explained. Randomness is obtained from the
operating system entropy source through Python's `secrets` module, and a fresh
ephemeral exponent is drawn for every encrypted block, which makes the scheme
probabilistic: the same plaintext encrypted twice under the same key normally
produces different ciphertexts.

A specific design problem addressed in this work is the constraint that ElGamal
encrypts an integer `m` satisfying `0 < m < p`. Plaintext is therefore encoded
as UTF-8 bytes, split into blocks whose size is derived from the bit length of
the modulus, and prefixed with a marker byte, which guarantees that the
constraint holds for every possible input and preserves leading zero bytes on
decoding. The system was evaluated with an automated suite of 88 tests covering
correctness, boundary conditions, invalid input and probabilistic behaviour,
together with a reproducible benchmark measuring key generation, encryption and
decryption cost across key sizes and message lengths.

The evaluation confirms functional correctness and illustrates the practical
cost profile of ElGamal, including its ciphertext expansion of roughly a factor
of two in group elements. The report is deliberately explicit about what the
implementation does *not* provide: textbook ElGamal offers no integrity, no
authentication and no protection against chosen-ciphertext attacks, it is
malleable, and the configuration used here — a generator of the full group
`Z_p*` rather than a prime-order subgroup — leaks the Legendre symbol of the
plaintext and is therefore not semantically secure in the strict sense. The
system is presented as an educational instrument for understanding
public-key encryption, not as a production security product.

**Keywords:** ElGamal, public-key cryptography, discrete logarithm problem,
probabilistic encryption, modular arithmetic, Python, Tkinter.

---

## Table of Contents

1. Introduction
2. Literature Review
3. System Analysis and Design
4. Implementation
5. Testing and Evaluation
6. Results and Discussion
7. Conclusion and Future Work
   References
   Appendices

*(Generate the final page-numbered contents with your word processor's
automatic table of contents once the document is assembled.)*

## List of Figures

| Figure | Title | Source |
|---|---|---|
| 3.1 | System architecture | `diagrams/system_architecture.drawio` |
| 3.2 | Use case diagram | `diagrams/use_case.drawio` |
| 3.3 | Context and Level 1 data flow diagram | `diagrams/dfd.drawio` |
| 3.4 | Overall system flowchart | `diagrams/system_flowchart.drawio` |
| 3.5 | Key generation flowchart | `diagrams/key_generation_flowchart.drawio` |
| 3.6 | Encryption flowchart | `diagrams/encryption_flowchart.drawio` |
| 3.7 | Decryption flowchart | `diagrams/decryption_flowchart.drawio` |
| 3.8 | Class and module diagram | `diagrams/class_diagram.drawio` |
| 4.1 | Application home screen | `[INSERT ACTUAL SCREENSHOT]` |
| 4.2 | Successful key generation | `[INSERT ACTUAL SCREENSHOT]` |
| 4.3 | Full key values dialog | `[INSERT ACTUAL SCREENSHOT]` |
| 4.4 | Encryption result | `[INSERT ACTUAL SCREENSHOT]` |
| 4.5 | Decryption result | `[INSERT ACTUAL SCREENSHOT]` |
| 5.1 | Test suite execution | `[INSERT ACTUAL SCREENSHOT]` |
| 5.2 | Error handling: empty plaintext | `[INSERT ACTUAL SCREENSHOT]` |
| 5.3 | Error handling: malformed ciphertext | `[INSERT ACTUAL SCREENSHOT]` |
| 5.4 | Same plaintext, two different ciphertexts | `[INSERT ACTUAL SCREENSHOT]` |
| 6.1 | Benchmark graph | `results/benchmark_plot.png` (regenerate) |

## List of Tables

| Table | Title |
|---|---|
| 3.1 | Functional requirements |
| 3.2 | Non-functional requirements |
| 3.3 | Use case descriptions |
| 3.4 | Block size by key size |
| 5.1 | Test case specification and results |
| 6.1 | Key generation timing |
| 6.2 | Encryption and decryption timing by key size |
| 6.3 | Message size scaling and ciphertext expansion |
| 6.4 | Security properties provided and not provided |

---

# CHAPTER 1 – INTRODUCTION

## 1.1 Background

Cryptography is the discipline concerned with securing information against
adversaries who may observe or interfere with it. Before 1976, practical
cryptography was almost entirely symmetric: the sender and receiver had to
share the same secret key, which had to be distributed over some separate
trusted channel. Diffie and Hellman (1976) removed that requirement by
proposing public-key cryptography, in which a user publishes an encryption key
while retaining a distinct secret decryption key. Rivest, Shamir and Adleman
(1978) gave the first widely adopted concrete construction, based on the
difficulty of factoring large integers.

ElGamal (1985) proposed an alternative public-key scheme whose security rests
instead on the difficulty of computing discrete logarithms in a finite field,
building directly on the Diffie–Hellman key exchange. The scheme is notable for
being *probabilistic*: encryption incorporates a fresh random value, so the same
message encrypted twice produces different ciphertexts. Goldwasser and Micali
(1984) had shown that this property is not a curiosity but a necessity —
deterministic public-key encryption cannot satisfy a strong definition of
security, because an adversary can simply encrypt a guessed plaintext and
compare.

ElGamal remains relevant today. Its structure underlies the Digital Signature
Algorithm, it is used in the OpenPGP ecosystem, and its homomorphic property
makes it a building block in electronic voting and mix-net protocols. For a
student of cryptography it is also unusually instructive: the whole scheme can
be written in a few dozen lines of arithmetic, which makes every design decision
visible.

## 1.2 Problem Statement

Cryptographic algorithms are frequently taught as a sequence of formulae and
then used in practice through library calls such as `encrypt(key, message)`.
Both the formulae and the library call conceal the decisions that actually
determine whether an implementation is correct or broken. Three of these
decisions are the specific focus of this project.

First, **the message representation problem**. ElGamal encrypts an integer `m`
with `0 < m < p`. Text is not an integer. A naive implementation converts an
entire string to one large integer; when that integer exceeds `p`, the
arithmetic silently reduces it modulo `p` and the original message becomes
unrecoverable. The failure is silent, which is the worst kind.

Second, **the randomness problem**. ElGamal's security depends on the ephemeral
exponent `k` being fresh and unpredictable. An implementation that reuses `k`,
or draws it from a non-cryptographic generator, produces ciphertexts that look
correct and decrypt correctly, while being vulnerable to an attacker who
recovers one plaintext and thereby recovers others.

Third, **the security-claim problem**. Student and hobby implementations
routinely describe textbook ElGamal as "secure encryption" without stating that
it provides no integrity, is malleable, and — in the common full-group
configuration — is not semantically secure.

The problem this project addresses is therefore: *how can the ElGamal
cryptosystem be implemented in a way that is functionally correct, handles the
`m < p` constraint explicitly rather than silently, uses cryptographically
appropriate randomness, and is accompanied by an accurate rather than
flattering account of its security properties?*

## 1.3 Aim

To design, implement, test and critically evaluate a functional Python desktop
application that performs message encryption and decryption using the ElGamal
public-key cryptosystem, demonstrating both correct cryptographic
implementation and an accurate understanding of the scheme's security
properties and limitations.

## 1.4 Objectives

1. **O1** — To implement the ElGamal cryptosystem in Python from first
   principles, including safe-prime generation, generator selection, key
   generation, modular exponentiation and modular inversion, without delegating
   the core mathematics to an external cryptographic library.
2. **O2** — To design and implement a message representation scheme that
   guarantees the constraint `0 < m < p` for arbitrary UTF-8 text of any
   length, and that rejects rather than silently corrupts out-of-range values.
3. **O3** — To build a Tkinter graphical interface supporting key generation,
   encryption, decryption, key inspection, reset and clear error reporting.
4. **O4** — To ensure every encryption uses a fresh ephemeral value drawn from
   a cryptographically secure source, and to demonstrate the resulting
   probabilistic behaviour experimentally.
5. **O5** — To validate the implementation with a systematic automated test
   suite covering normal operation, boundary conditions and invalid input.
6. **O6** — To measure the performance of key generation, encryption and
   decryption across key sizes and message lengths using a reproducible
   benchmark.
7. **O7** — To evaluate the security properties actually provided by the
   implementation, and to document its limitations accurately.

Each objective is measurable: O1–O4 by inspection of the source and by test
outcomes, O5 by the test report, O6 by the benchmark output, and O7 by
Chapter 6 of this report.

## 1.5 Scope

**Within scope.** A single-user desktop application; ElGamal key generation at
256, 512, 1024 and 2048 bits; encryption and decryption of UTF-8 text of
arbitrary length through block processing; display and optional JSON export of
keys; input validation and error handling; an automated test suite; a
performance benchmark; and a security evaluation.

**Outside scope.** Network transmission of ciphertext; multi-user key
distribution or a public-key infrastructure; ElGamal digital signatures;
elliptic-curve variants; hybrid encryption with a symmetric cipher; padding
schemes or chosen-ciphertext-secure constructions such as Cramer–Shoup or
DHIES; encrypted key storage; and side-channel resistance. These are discussed
as future work in Chapter 7 but are not implemented, and the report makes no
claim about them.

## 1.6 Significance

The project contributes an implementation that is deliberately transparent: the
cryptographic core is 300 lines of commented Python in which every step of the
algorithm corresponds to a named function that can be traced to the definitions
in the literature. Three aspects have practical value beyond the assessment.
The block-encoding design shows how the `m < p` constraint is satisfied by
construction rather than by hope. The test suite includes tests that
*demonstrate weaknesses* — malleability and the consequences of a wrong key —
rather than only demonstrating success, which is unusual in student work and
directly supports the security discussion. The benchmark quantifies the cost
asymmetry between key generation and encryption, which is the practical reason
public-key schemes are used to establish symmetric keys rather than to encrypt
bulk data.

## 1.7 Limitations

1. The implementation is textbook ElGamal, with no integrity protection, no
   authentication and no chosen-ciphertext security.
2. The scheme uses a generator of the full group `Z_p*` rather than a
   prime-order subgroup, which leaks the Legendre symbol of each plaintext
   block; it is therefore not semantically secure in the strict sense
   (see Section 2.14 and 6.8).
3. Key sizes below 2048 bits are selectable for demonstration purposes and are
   not adequate for real protection.
4. Exported private keys are stored as unencrypted JSON.
5. Performance is measured in CPython, which is considerably slower than
   optimised C implementations; the figures illustrate relative trends rather
   than absolute achievable performance.
6. The implementation makes no attempt at constant-time execution and is not
   resistant to timing or other side-channel attacks.
7. Automated testing covers the cryptographic core and the encoding layer; the
   Tkinter interface is verified manually rather than by automated UI tests.

## 1.8 Report Organisation

Chapter 2 reviews the cryptographic background and related work. Chapter 3
presents requirements and system design with the supporting diagrams.
Chapter 4 documents the implementation. Chapter 5 sets out the testing strategy
and results. Chapter 6 discusses results, performance and security. Chapter 7
concludes and identifies future work.

---

# CHAPTER 2 – LITERATURE REVIEW

## 2.1 Introduction

This chapter establishes the conceptual and mathematical foundations the
implementation rests on, situates ElGamal among related cryptosystems, and
identifies the gap this project addresses. Sources are drawn from the original
research papers, standard reference works, and current standards
documentation.

## 2.2 Cryptography

Cryptography concerns techniques for securing information in the presence of
adversaries. Menezes, van Oorschot and Vanstone (1996) define it as the study
of mathematical techniques related to information security objectives, and
their taxonomy — symmetric-key primitives, public-key primitives and unkeyed
primitives such as hash functions — remains the standard organisation of the
field. Cryptography is distinguished from cryptanalysis, which studies methods
for defeating those techniques; the two together form cryptology (Paar &
Pelzl, 2010).

## 2.3 Security Goals

Four goals are conventionally distinguished (Menezes et al., 1996):

- **Confidentiality** — information is unintelligible to unauthorised parties.
- **Integrity** — unauthorised modification is detectable.
- **Authentication** — the identity of a party or the origin of data is
  corroborated.
- **Non-repudiation** — a party cannot credibly deny a prior commitment.

These are separable. A scheme can provide confidentiality and nothing else,
which is precisely the case for the system built here. Stating which goals a
system meets, and which it does not, is a basic requirement of honest security
engineering, and is revisited in Section 6.8.

## 2.4 Symmetric Cryptography

In symmetric encryption the same key encrypts and decrypts. Modern symmetric
ciphers such as AES are fast and compact, and are the workhorses of bulk data
encryption. Their weakness is organisational rather than mathematical: `n`
mutually communicating parties require `n(n-1)/2` distinct keys, and every key
must be distributed over a channel that is already secure (Paar & Pelzl, 2010).
This key-distribution problem motivated public-key cryptography.

## 2.5 Asymmetric Cryptography

Diffie and Hellman (1976) proposed separating the encryption and decryption
capabilities into two mathematically related but computationally independent
keys: a public key that may be freely distributed, and a private key retained
by its owner. The relationship between them must be a *one-way function with a
trapdoor*: easy to compute in one direction, infeasible to invert without the
trapdoor. The security of every public-key scheme therefore reduces to the
conjectured hardness of some computational problem.

## 2.6 Public-Key Encryption

The first practical realisation was RSA (Rivest, Shamir & Adleman, 1978), whose
security relates to the difficulty of factoring a product of two large primes.
RSA in its textbook form is deterministic, which Goldwasser and Micali (1984)
showed to be a fundamental limitation: under their definition of semantic
security, no deterministic public-key scheme can be secure, because an
adversary who suspects a plaintext can encrypt it and compare ciphertexts. This
result is the theoretical reason ElGamal's randomised design matters.

## 2.7 Mathematical Foundations

**Modular arithmetic.** Computation in `Z_p = {0, 1, ..., p-1}` with addition
and multiplication reduced modulo `p`. When `p` is prime, every non-zero
element has a multiplicative inverse, and the non-zero elements form the cyclic
multiplicative group `Z_p*` of order `p-1` (Menezes et al., 1996).

**Modular exponentiation.** Computing `g^a mod p` naively requires `a`
multiplications, which is infeasible for cryptographic exponents. Square-and-
multiply reduces this to `O(log a)` modular multiplications, making encryption
fast even though inverting the operation is believed hard (Paar & Pelzl, 2010).
Python's built-in `pow(base, exp, mod)` implements this.

**Modular multiplicative inverse.** For `gcd(a, m) = 1` there is a unique
`a^(-1)` in `[1, m-1]` with `a * a^(-1) ≡ 1 (mod m)`. It is computed by the
Extended Euclidean Algorithm, which returns integers `s, t` with
`as + mt = gcd(a, m)`; when the gcd is 1, `s mod m` is the inverse (Menezes et
al., 1996). Decryption in ElGamal requires exactly this operation.

**Generators.** An element `g` of `Z_p*` is a generator if its powers produce
every element of the group. For a safe prime `p = 2q + 1` the group order is
`2q`, so a candidate `g` is a generator precisely when `g^2 mod p != 1` and
`g^q mod p != 1` — a cheap and certain test, which is why safe primes are used
in this implementation.

**Primality testing.** Generating a large prime means testing random candidates.
The Miller–Rabin test is a probabilistic algorithm: a composite input is
detected with probability at least 3/4 per round, so `t` rounds give an error
probability of at most `4^(-t)` (Menezes et al., 1996). With 40 rounds, as used
here, the residual probability is negligible compared with hardware error rates.

## 2.8 The Discrete Logarithm Problem

Given a prime `p`, a generator `g` of `Z_p*` and an element `y`, the discrete
logarithm problem (DLP) is to find `x` with `g^x ≡ y (mod p)`. No polynomial-
time classical algorithm is known; the best general methods, such as the index
calculus family, run in sub-exponential time (Menezes et al., 1996). Two
related problems matter for ElGamal specifically:

- **Computational Diffie–Hellman (CDH):** given `g^a` and `g^b`, compute
  `g^(ab)`. If CDH is hard, ElGamal encryption is one-way.
- **Decisional Diffie–Hellman (DDH):** distinguish `(g^a, g^b, g^(ab))` from
  `(g^a, g^b, g^c)` for random `c`. Boneh (1998) surveys this assumption. It is
  the condition under which ElGamal achieves semantic security.

Pohlig and Hellman (1978) showed that the DLP in a group of order `n` reduces to
the DLP in subgroups of prime-power order dividing `n`, so a group whose order
has only small prime factors offers no security. Safe primes avoid this: the
order `p - 1 = 2q` has the single large prime factor `q`.

Shor's algorithm would solve the DLP efficiently on a sufficiently large
quantum computer, which is why discrete-logarithm and factoring-based schemes
alike are being succeeded by post-quantum alternatives; this is noted for
completeness and is outside the scope of the implementation.

## 2.9 The ElGamal Cryptosystem

ElGamal (1985) proposed a public-key encryption scheme and a signature scheme
based on the difficulty of computing discrete logarithms over finite fields.
The encryption scheme can be read as an *in-line* Diffie–Hellman exchange: the
sender performs their half of a key agreement, uses the resulting shared value
to mask the message multiplicatively, and transmits their half of the exchange
alongside the masked message.

## 2.10 Key Generation

1. Select a large prime `p`.
2. Select a generator `g` of `Z_p*`.
3. Select `x` uniformly at random with `1 < x < p - 1`.
4. Compute `y = g^x mod p`.

The public key is `(p, g, y)` and the private key is `x`. Recovering `x` from
`y` is exactly the DLP.

## 2.11 Encryption

For a message `m` with `0 < m < p`, the sender selects a fresh random ephemeral
value `k` with `1 < k < p - 1` and computes

```
c1 = g^k mod p
c2 = m · y^k mod p
```

The ciphertext is the pair `(c1, c2)`. Because `k` is fresh on each encryption,
the scheme is probabilistic and the ciphertext is twice the size of the
plaintext in group elements.

## 2.12 Decryption

The receiver computes the shared value `s = c1^x mod p` and recovers

```
m = c2 · s^(-1) mod p
```

## 2.13 Correctness

```
s   = c1^x    = (g^k)^x = g^(kx)  (mod p)
y^k = (g^x)^k = g^(xk)            (mod p)
```

Since `kx = xk`, we have `s = y^k`. Therefore

```
c2 · s^(-1) = (m · y^k) · (y^k)^(-1) = m  (mod p)
```

The inverse exists because `p` is prime and `s != 0`, so `gcd(s, p) = 1`.

## 2.14 Security Properties

ElGamal is one-way under the CDH assumption: an adversary who could recover `m`
from `(c1, c2)` and the public key could compute Diffie–Hellman shared values.
Tsiounis and Yung (1998) proved the stronger result that ElGamal's semantic
security is *equivalent* to the DDH assumption, **provided messages are drawn
from an appropriate subgroup**. This proviso is substantive and is frequently
omitted in summaries. When the full group `Z_p*` is used with a full-order
generator — the configuration adopted in this project so that arbitrary byte
blocks map directly to group elements — `c2` reveals the Legendre symbol of
`m`, because the quadratic residuosity of `y^k` is computable from `c1`. One
bit of plaintext information therefore leaks per block, and DDH does not hold in
`Z_p*`. This is stated here because the implementation inherits the
consequence, which is analysed in Section 6.8.

ElGamal is also **malleable**: given `(c1, c2)` encrypting `m`, the pair
`(c1, t·c2 mod p)` is a valid ciphertext for `t·m mod p`, without knowledge of
`m` or `x`. The same property, viewed constructively, is the multiplicative
homomorphism that makes ElGamal useful in voting and mix-net protocols. It is
also why textbook ElGamal is not secure against chosen-ciphertext attacks, and
why constructions such as Cramer–Shoup and DHIES exist.

## 2.15 Strengths

The scheme's security rests on a well-studied problem; it is natively
probabilistic, and therefore does not need a padding scheme retrofitted to
achieve randomisation as RSA does; key generation can share domain parameters
`(p, g)` across users; and its homomorphic structure enables protocols that RSA
cannot support as naturally.

## 2.16 Limitations

Ciphertext is twice the size of plaintext in group elements, compared with a
1:1 ratio for RSA. Encryption requires two modular exponentiations rather than
one, and, unlike RSA with a small public exponent, both are full-width.
Security depends critically on the ephemeral value: reuse of `k` across two
messages under the same key yields `c2/c2' = m/m'`, so recovery of one
plaintext reveals the other. Basic ElGamal provides no integrity or
authentication, and, as noted, no chosen-ciphertext security.

## 2.17 Related Work

Barker (2020), in NIST SP 800-57 Part 1 Revision 5, provides the authoritative
current guidance on key sizes and cryptoperiods, and is the appropriate source
for the claim that finite-field schemes require moduli of at least 2048 bits
for contemporary protection. Katz and Lindell (2021) give the standard rigorous
treatment of semantic security and of the reductions relating ElGamal to DDH.
Paar and Pelzl (2010) present ElGamal from an implementation perspective,
including the square-and-multiply algorithm and the practical consequences of
ciphertext expansion. The Python Software Foundation's documentation for the
`secrets` module states that it should be used in preference to the `random`
module for security purposes, which is the basis of the randomness decision in
Section 4.13.

## 2.18 Comparison with Related Cryptosystems

| Property | RSA | ElGamal | AES (for contrast) |
|---|---|---|---|
| Type | Asymmetric | Asymmetric | Symmetric |
| Hard problem | Integer factorisation | Discrete logarithm | None (design-based) |
| Deterministic? | Yes (textbook) | No — probabilistic | Depends on mode |
| Ciphertext expansion | 1:1 | 2:1 | 1:1 |
| Encryption cost | One exponentiation (small `e`) | Two exponentiations | Very fast |
| Homomorphism | Multiplicative | Multiplicative | None |
| Integrity built in | No | No | No (needs a MAC or AEAD) |

The comparison explains the standard practice of hybrid encryption: public-key
schemes establish or transport a symmetric key, and the symmetric cipher
encrypts the data.

## 2.19 Literature Gap and Project Motivation

The mathematics of ElGamal is thoroughly documented in the sources above, and
numerous implementations exist. What is comparatively scarce in accessible
teaching material is a treatment that connects the mathematics to the
implementation decisions that determine whether a deployment is sound — how the
`m < p` constraint is enforced for real text, where randomness comes from and
why, and what security claims can honestly be made about the result. This
project addresses that gap by building a complete, inspectable implementation
in which each of those decisions is made explicitly, tested, and then evaluated
critically, including tests that demonstrate the scheme's weaknesses rather
than only its successes.

## 2.20 Summary

ElGamal is a probabilistic public-key encryption scheme whose security rests on
the discrete logarithm problem and, for semantic security, on the Decisional
Diffie–Hellman assumption in an appropriate subgroup. It provides
confidentiality but not integrity or authentication, is malleable, and expands
ciphertext by a factor of two. These properties frame both the design presented
in Chapter 3 and the evaluation in Chapter 6.

---

# CHAPTER 3 – SYSTEM ANALYSIS AND DESIGN

## 3.1 Introduction

This chapter derives the system requirements from the problem statement and
presents the design: architecture, use cases, data flow, process flowcharts,
message representation, key management, interface layout and security design.

## 3.2 Problem Analysis

The system must bridge two representations — human-readable text and integers
in `Z_p*` — while making three guarantees: that every message integer satisfies
`0 < m < p`; that every encryption uses fresh unpredictable randomness; and
that every failure is reported rather than producing plausible-looking wrong
output. The third guarantee matters because a cryptographic application that
returns garbage silently is worse than one that refuses.

A layered design follows from this analysis. The interface layer handles
presentation and first-line validation; an encoding layer handles the text-to-
integer mapping and the block constraint; a cryptographic layer implements
ElGamal over integers; and a key management layer holds the active key pair.
Each layer can then be tested independently of the interface, which is what
makes an 88-test automated suite possible for a GUI application.

## 3.3 Requirements Gathering

Requirements were derived from three sources: the CCS2243 assessment
instructions, which require a working implementation applying a cryptographic
technique with design evidence, testing and evaluation; the mathematical
definition of ElGamal as given in Chapter 2; and the security considerations
that follow from it.

## 3.4 Functional Requirements

**Table 3.1 — Functional requirements**

| ID | Requirement | Implemented in |
|---|---|---|
| FR1 | Generate an ElGamal key pair at a user-selected size | `elgamal.generate_keypair`, `KeyManager.generate` |
| FR2 | Accept plaintext input of arbitrary length | `gui.ElGamalApp.plaintext_box` |
| FR3 | Encrypt plaintext under the active public key | `crypto_utils.encrypt_text` |
| FR4 | Display the ciphertext in a readable, copyable format | `crypto_utils.pairs_to_string`, GUI |
| FR5 | Accept ciphertext input for decryption | `gui.ElGamalApp.ciphertext_in` |
| FR6 | Decrypt ciphertext with the corresponding private key | `crypto_utils.decrypt_text` |
| FR7 | Display the recovered plaintext | `gui.ElGamalApp.plaintext_out` |
| FR8 | Validate all user input before cryptographic processing | `gui` handlers, `crypto_utils.string_to_pairs` |
| FR9 | Report all errors with specific, understandable messages | `gui.ElGamalApp.show_error` |
| FR10 | Clear all fields and discard keys on reset | `gui.ElGamalApp.on_reset` |
| FR11 | Display the full key values on request | `gui.ElGamalApp.on_show_keys` |
| FR12 | Export and import key pairs as JSON, verifying that they match | `key_manager.KeyManager` |
| FR13 | Use a fresh ephemeral `k` for every encrypted block | `elgamal.encrypt_int` |

FR11–FR13 are listed because they are implemented, not to lengthen the table.

## 3.5 Non-Functional Requirements

**Table 3.2 — Non-functional requirements**

| ID | Requirement | How it is met |
|---|---|---|
| NFR1 | Correctness: decryption recovers the exact plaintext | 88 automated tests, including Unicode and long inputs |
| NFR2 | Responsiveness: the interface must not freeze during key generation | Key generation runs on a worker thread with a progress bar |
| NFR3 | Usability: operable without cryptographic expertise | Three labelled panels following the operational sequence |
| NFR4 | Maintainability: cryptography separable from interface | Four modules with a one-directional dependency graph |
| NFR5 | Portability: runs on Windows, macOS and Linux | Standard library only; no compiled dependencies |
| NFR6 | Reproducibility: results regenerable by a third party | `pytest` suite and `benchmark.py` with CSV output |
| NFR7 | Transparency: security limitations stated in the product itself | Warnings on private key export; documented in README |

## 3.6 System Architecture

**[Figure 3.1 — System architecture; source `diagrams/system_architecture.drawio`]**

The architecture is a four-layer stack. The user interacts only with the
Tkinter presentation layer. Input validation sits directly beneath it and is
the sole gateway to the cryptographic layers. The message representation module
(`crypto_utils.py`) converts between text and integers; the cryptographic
engine (`elgamal.py`) performs all modular arithmetic; and the key management
module (`key_manager.py`) holds the active key pair and handles optional file
storage. The operating system CSPRNG is shown as an external dependency because
randomness genuinely originates outside the application.

No database, network service or third-party cryptographic library appears in
the architecture, because none exists in the implementation.

## 3.7 Use Case Diagram

**[Figure 3.2 — Use case diagram; source `diagrams/use_case.drawio`]**

A single actor, the User, interacts with eight primary use cases. *Validate
Input* and *Display Status or Error Message* are modelled as `<<include>>`
relationships because they are invoked unconditionally by the operations that
reference them. *Encrypt Message* and *Decrypt Message* are shown with a
precondition dependency on *Generate Key Pair*, reflecting the check performed
by `on_encrypt` and `on_decrypt`.

## 3.8 Use Case Descriptions

**Table 3.3 — Use case descriptions**

| Use case | Actor | Precondition | Main flow | Postcondition | Exceptions |
|---|---|---|---|---|---|
| Generate Key Pair | User | Application running | Select key size → press Generate → safe prime found, `g`, `x`, `y` computed | Key pair active; values displayed | Size invalid → error in status bar |
| Enter Plaintext | User | Application running | Type or paste text | Plaintext ready | — |
| Encrypt Message | User | Key pair exists; plaintext non-empty | Encode → block → fresh `k` per block → compute `(c1, c2)` → serialise | Ciphertext displayed | No key, or empty plaintext → error |
| View Ciphertext | User | Encryption completed | Read or copy the ciphertext field | — | — |
| Enter Ciphertext | User | Application running | Paste ciphertext or use *Copy to Decryption Pane* | Ciphertext ready | — |
| Decrypt Message | User | Key pair exists; ciphertext present | Parse → validate → `s = c1^x` → invert → recover `m` → decode | Plaintext displayed | Malformed, out-of-range, or wrong key → specific error |
| Export / Import Keys | User | Key pair exists (export) | Confirm warning → choose folder → write JSON | Key files written or loaded | I/O error, mismatched pair → error |
| Clear / Reset | User | Application running | Press Reset | All fields cleared; key pair discarded | — |

## 3.9 Data Flow Diagram

**[Figure 3.3 — Context and Level 1 DFD; source `diagrams/dfd.drawio`]**

The context diagram shows a single process exchanging data with one external
entity. The Level 1 diagram decomposes it into seven processes: validate input,
generate key pair, encode plaintext, encrypt blocks, decrypt blocks, decode
blocks and format output. One internal data store (D1, the active key pair in
memory) and one optional external store (D2, the JSON key files) are shown. No
relational database appears, because the application does not use one.

## 3.10 Overall System Flowchart

**[Figure 3.4 — System flowchart; source `diagrams/system_flowchart.drawio`]**

The application is event-driven: after launch it waits for user actions,
dispatches each to the relevant operation, checks preconditions, displays the
result or an error, and returns to the waiting state until the user exits.

## 3.11 Key Generation Workflow

**[Figure 3.5 — Key generation flowchart; source `diagrams/key_generation_flowchart.drawio`]**

The flowchart shows the staged prime search actually implemented: a random odd
candidate `q` is generated; `p = 2q + 1` is formed; both are filtered by trial
division against the first 54 primes; survivors face five Miller–Rabin rounds;
and only those that survive that are subjected to the full 40-round test.
Candidates that fail at any stage are discarded and the search restarts. The
staging is a performance measure — Section 6.2 shows why it is necessary — and
does not affect the confidence of the final primality decision.

## 3.12 Encryption Workflow

**[Figure 3.6 — Encryption flowchart; source `diagrams/encryption_flowchart.drawio`]**

```
Start → read plaintext → key present? → plaintext non-empty?
      → UTF-8 encode → split into blocks → prefix 0x01 → integer m
      → check 0 < m < p → fresh k per block → c1 = g^k mod p
      → c2 = m·y^k mod p → serialise as hex → display → End
```

The `0 < m < p` check is retained even though the block sizing makes violation
impossible, as a defensive assertion against a future change to the encoding.

## 3.13 Decryption Workflow

**[Figure 3.7 — Decryption flowchart; source `diagrams/decryption_flowchart.drawio`]**

```
Start → read ciphertext → key present? → parse hex pairs
      → format valid and 1 ≤ c1, c2 ≤ p-1? → s = c1^x mod p
      → s⁻¹ by Extended Euclidean Algorithm → m = c2·s⁻¹ mod p
      → bytes, strip 0x01 marker → marker present and valid UTF-8?
      → concatenate → display → End
```

The marker and UTF-8 checks are what convert a wrong-key decryption from
silent garbage into a reported error.

## 3.14 Message Representation

The block size is derived from the modulus:

```
block_size(p) = (bit_length(p) - 1) // 8 - 1   bytes
```

A block of that many bytes, prefixed with `0x01`, occupies at most
`block_size + 1` bytes, whose maximum value is `2^(8·(block_size+1)) - 1`. The
formula guarantees `8·(block_size + 1) ≤ bit_length(p) - 1`, so that maximum is
strictly less than `p`. The constraint is therefore satisfied *by construction*
for every possible byte pattern, not merely for typical inputs.

**Table 3.4 — Block size by key size**

| Key size (bits) | Plaintext bytes per block | Ciphertext blocks for a 100-byte message |
|---|---|---|
| 256 | 30 | 4 |
| 512 | 62 | 2 |
| 1024 | 126 | 1 |
| 2048 | 254 | 1 |

The `0x01` prefix serves two further purposes: it preserves leading zero bytes,
which would otherwise be lost in the integer conversion and make decoding
ambiguous, and it guarantees `m != 0`, since 0 is not a member of `Z_p*`.

## 3.15 Key Management

The active key pair is held in memory in a `KeyManager` instance for the
lifetime of the session and is discarded on reset or exit. Export is optional
and writes two JSON files: `public_key.json` containing `(p, g, y)` and
`private_key.json` containing `(p, g, x)`. On import, the pair is validated —
`p` must be prime, `g` and `y` in range, `x` in `[2, p-2]`, and crucially
`g^x mod p == y` — so that a mismatched pair is rejected at load time rather
than producing confusing decryption failures later.

The private key file is unencrypted. The interface displays an explicit warning
before export, and the file itself carries a warning field. A production system
would derive a key from a passphrase with a memory-hard KDF and encrypt the
private key with an authenticated cipher, or delegate storage to an OS keystore
or hardware security module. This is stated as a known limitation rather than
disguised.

## 3.16 Graphical Interface Design

The window is divided into three numbered panels matching the operational
sequence, with a persistent status bar:

```
ELGAMAL ENCRYPTION IMPLEMENTATION
CCS2243 Cryptography Essential – Educational Prototype
─────────────────────────────────────────────────────
1. KEY GENERATION
   Key size: [512 ▾]  [Generate Key Pair] [Show Full Key Values]
                      [Export Keys...]    [Import Keys...]
   Prime p:                    1234…5678  (155 digits)
   Generator g:                …
   Private key x:              …
   Public value y = g^x mod p: …
   Plaintext bytes per block:  62 bytes (modulus is 512 bits)
─────────────────────────────────────────────────────
2. ENCRYPTION
   Plaintext:   [                    ]
   [Encrypt]
   Ciphertext:  [                    ]
   [Copy to Decryption Pane]
─────────────────────────────────────────────────────
3. DECRYPTION
   Ciphertext to decrypt: [           ]
   [Decrypt]
   Recovered plaintext:   [           ]
─────────────────────────────────────────────────────
[Clear / Reset]   Status: Ready. Generate a key pair to begin.
```

Three design decisions are worth noting. Key values are abbreviated in the main
panel with a digit count, because a 512-bit modulus is 155 decimal digits and
would otherwise destroy the layout in a report screenshot; the full values are
one click away. The block size is displayed, making the `m < p` constraint
visible to the user rather than hidden. The status bar shows green for success
and red for failure, so that the outcome of an operation is unambiguous in a
screenshot.

## 3.17 Security Design

Security decisions embedded in the design:

1. **Randomness source.** All random values — candidate primes, the private key
   `x`, and every ephemeral `k` — come from `secrets`, which draws on the
   operating system entropy source. `random` is not used anywhere in the
   cryptographic path.
2. **Fresh `k` per block.** `encrypt_int` draws a new `k` on every call, and it
   is called once per block, so a two-block message uses two independent `k`
   values.
3. **Safe primes.** `p = 2q + 1` ensures the group order has one large prime
   factor, preventing the Pohlig–Hellman reduction, and makes generator
   verification cheap and certain.
4. **Verified generators.** `g` is tested rather than assumed.
5. **Fail closed.** Every error path raises a specific exception that the GUI
   converts into a message; no path returns a wrong result quietly.
6. **Honest key sizes.** The default is 512 bits for demonstration speed, and
   the report states plainly that 2048 bits is the minimum for real use
   (Barker, 2020).

## 3.18 Summary

The design separates presentation, validation, encoding, cryptography and key
management into independently testable layers, enforces the `m < p` constraint
structurally, and treats error reporting as a security requirement rather than
a usability nicety.

---

# CHAPTER 4 – IMPLEMENTATION

## 4.1 Introduction

This chapter documents how the design was realised, with reference to the
actual source files.

## 4.2 Development Environment

| Item | Value |
|---|---|
| Language | Python 3.8+ (`[INSERT YOUR EXACT VERSION: python --version]`) |
| GUI toolkit | Tkinter (standard library) |
| Test framework | pytest |
| Plotting (benchmark only) | matplotlib |
| Editor / IDE | `[INSERT: e.g. Visual Studio Code / PyCharm]` |
| Operating system | `[INSERT: e.g. Windows 11]` |
| Hardware | `[INSERT: CPU model, RAM]` |
| Version control | Git / GitHub — `[INSERT ACTUAL GITHUB URL]` |

## 4.3 Python

Python was selected for three reasons specific to this project. Its integers
have arbitrary precision, so 2048-bit arithmetic requires no big-number
library and the code reads like the mathematical definitions. Its built-in
`pow(base, exponent, modulus)` performs efficient modular exponentiation,
which is the single most frequent operation in ElGamal. And the standard
library provides `secrets`, `tkinter` and `json`, which covers every
requirement without external dependencies.

## 4.4 Tkinter

Tkinter was chosen over alternatives because it ships with CPython, so the
application runs from a clean Python installation with no `pip install` step —
a meaningful property for a project that must be demonstrated on an unfamiliar
machine. The assessment document lists it among the recommended GUI frameworks.

## 4.5 Libraries

The application uses no third-party libraries at all. Within the standard
library it uses `secrets` for randomness, `tkinter` for the interface, `json`
for key files, `dataclasses` for key containers, `threading` and `queue` for
non-blocking key generation, and `os` for path handling. `pytest` and
`matplotlib` are development tools only; neither is imported by the
application. Consequently, no part of the ElGamal computation is performed by
an external library, which was objective O1.

## 4.6 Project Structure

```
ElGamal-Encryption/
├── main.py            entry point and environment checks
├── gui.py             Tkinter interface (≈420 lines)
├── elgamal.py         ElGamal mathematics (≈300 lines)
├── crypto_utils.py    encoding and ciphertext format (≈220 lines)
├── key_manager.py     key storage and validation (≈190 lines)
├── benchmark.py       performance measurement
├── tests/             88 automated tests in three modules
├── diagrams/          generator script and eight .drawio sources
├── docs/              report, user guide, test plan, viva preparation
└── results/           benchmark CSVs and graph
```

Dependencies run in one direction only: `gui → crypto_utils → elgamal`, and
`gui → key_manager → elgamal`. `elgamal.py` imports nothing from the project.

## 4.7 Key Generation

`generate_keypair(bits)` calls `generate_safe_prime(bits)`, then
`find_generator(p, q)`, then draws `x` and computes `y`:

```python
p, q = generate_safe_prime(bits)
g = find_generator(p, q)
x = secrets.randbelow(p - 3) + 2        # uniform in [2, p-2]
y = pow(g, x, p)
```

`generate_safe_prime` implements the staged search described in Section 3.11.
The expression `secrets.randbelow(p - 3) + 2` yields a uniform value in
`[2, p-2]`: `randbelow(n)` returns `[0, n-1]`, so `randbelow(p-3)` gives
`[0, p-4]`, and adding 2 gives `[2, p-2]`.

`find_generator` exploits the safe-prime structure. Since `p - 1 = 2q` with `q`
prime, the order of any element divides `2q`, so the possible orders are
1, 2, `q` and `2q`. Excluding `g^2 = 1` and `g^q = 1` therefore leaves only
order `2q`, a full generator:

```python
while True:
    g = secrets.randbelow(p - 3) + 2
    if pow(g, 2, p) == 1:  continue
    if pow(g, q, p) == 1:  continue
    return g
```

Roughly half of all candidates qualify, so the loop terminates quickly.

## 4.8 Modular Arithmetic

Modular exponentiation uses Python's built-in three-argument `pow`, which
implements square-and-multiply and reduces at each step, keeping intermediate
values bounded by `p²`. Computing `y^k mod p` for a 2048-bit modulus takes
milliseconds; computing it by repeated multiplication would be infeasible. This
asymmetry — cheap exponentiation, infeasible logarithm — is the foundation the
whole scheme stands on.

## 4.9 Modular Inverse

`mod_inverse(a, m)` uses the iterative Extended Euclidean Algorithm:

```python
old_r, r = a, b
old_s, s = 1, 0
old_t, t = 0, 1
while r != 0:
    quotient = old_r // r
    old_r, r = r, old_r - quotient * r
    old_s, s = s, old_s - quotient * s
    old_t, t = t, old_t - quotient * t
```

returning `(gcd, s, t)` with `as + mt = gcd`. When the gcd is 1, `s mod m` is
the inverse. Fermat's little theorem (`a^(p-2) mod p`) would also work for
prime `p`, and would be marginally faster, but the Extended Euclidean Algorithm
was chosen because it is the algorithm taught in the course, it works for any
coprime modulus rather than only primes, and it makes the failure case —
`gcd != 1` — explicit rather than silently returning a wrong value. The
iterative form avoids Python's recursion limit on large inputs.

## 4.10 Message Conversion

`text_to_blocks` and `blocks_to_text` implement the scheme of Section 3.14:

```python
size = block_size(p)
for start in range(0, len(data), size):
    chunk = data[start:start + size]
    m = int.from_bytes(b"\x01" + chunk, byteorder="big")
```

Decoding reverses this, verifies the marker byte, strips it, concatenates and
decodes as UTF-8. A missing marker or invalid UTF-8 raises `EncodingError` with
a message naming the probable cause.

## 4.11 Encryption

```python
if m <= 0 or m >= p:
    raise MessageTooLargeError(...)
k  = secrets.randbelow(p - 3) + 2
c1 = pow(key.g, k, p)
c2 = (m * pow(key.y, k, p)) % p
```

The range check precedes the arithmetic, so an out-of-range message is rejected
rather than silently reduced. `encrypt_blocks` maps this over the block list,
so `k` is fresh per block, not per message.

## 4.12 Decryption

```python
if not (1 <= c1 <= p - 1) or not (1 <= c2 <= p - 1):
    raise DecryptionError(...)
s = pow(c1, key.x, p)
m = (c2 * mod_inverse(s, p)) % p
```

## 4.13 Randomness

Every random value in the cryptographic path comes from `secrets`, which the
Python documentation identifies as the module to use in preference to `random`
for security purposes, and which draws on the operating system's entropy
source. Three properties are required and obtained: unpredictability (an
attacker cannot infer future values from past ones), uniformity (no bias toward
particular values), and freshness (a new value on each call). Using `random`
instead would be catastrophic here: it is a Mersenne Twister whose entire
future output can be reconstructed from 624 observed outputs, so an attacker
who recovered a few ephemeral values could predict subsequent ones and decrypt
every later message.

## 4.14 Key Management

`KeyManager` holds an `Optional[KeyPair]` and raises `KeyManagerError` when an
operation requires keys that do not exist, which is the mechanism behind the
"generate a key pair first" messages. `load_pair` performs the consistency
check `pow(g, x, p) == y` before accepting an imported pair.

## 4.15 Graphical Interface

`ElGamalApp` extends `ttk.Frame` and builds four sections with `grid`. The
notable implementation detail is key generation threading. A 1024-bit safe
prime search took a median of roughly 12.6 seconds in the reference environment
(Section 6.2), which would freeze the interface entirely if run on the main
thread. The work therefore runs on a daemon thread that posts its result to a
`queue.Queue`, while the main thread polls the queue every 120 ms via
`self.after`. This is necessary because Tkinter widgets may only be touched
from the thread that created them, so the worker thread never writes to the
interface directly.

## 4.16 Validation

Validation is layered. The interface checks that a key pair exists and that the
relevant text field is non-empty. `string_to_pairs` checks the ciphertext
structure line by line, reporting the offending line number. `decrypt_text`
checks each component against `p`. `decrypt_int` checks the `[1, p-1]` range.
`blocks_to_text` checks the marker byte and UTF-8 validity. Each layer reports
what it knows, which is why the error messages are specific rather than a
generic "operation failed".

## 4.17 Error Handling

All project exceptions derive from `ElGamalError`, allowing the GUI to catch
one base class while the specific subclasses carry actionable messages:

| Exception | Raised when | Message seen by the user |
|---|---|---|
| `InvalidParameterError` | Key size too small; non-prime modulus; no inverse | "Key size must be at least 64 bits." |
| `MessageTooLargeError` | `m` outside `(0, p)` | Names the bit lengths of `m` and `p` |
| `DecryptionError` | Ciphertext component out of range | "Ciphertext component is outside the valid range [1, p-1]." |
| `EncodingError` | Empty plaintext; missing marker; invalid UTF-8 | "The ciphertext or the private key is probably incorrect." |
| `CiphertextFormatError` | Malformed or non-hex ciphertext | "Line 2 is malformed: expected exactly one ':' separating c1 and c2." |
| `KeyManagerError` | No keys; unreadable or mismatched key files | "The private key does not correspond to the public key." |

## 4.18 Integration

The layers integrate through narrow interfaces: the GUI calls only
`encrypt_text`, `decrypt_text`, `block_size` and the `KeyManager` methods; the
encoding layer calls only `encrypt_blocks` and `decrypt_blocks`. The tests
exercise each layer through the same public interfaces the GUI uses, so a test
pass is meaningful evidence about the application's behaviour and not only
about isolated functions.

## 4.19 Summary

The implementation comprises roughly 1,100 lines of application code plus
tests and tooling, with no third-party runtime dependencies. All cryptographic
operations are implemented directly, randomness is drawn from the operating
system, and every failure mode raises a specific, reportable exception.

**Screenshots of the running application**

- `[INSERT FIGURE 4.1: ACTUAL APPLICATION HOME SCREEN]`
- `[INSERT FIGURE 4.2: ACTUAL KEY GENERATION RESULT]`
- `[INSERT FIGURE 4.3: ACTUAL FULL KEY VALUES DIALOG]`
- `[INSERT FIGURE 4.4: ACTUAL ENCRYPTION RESULT]`
- `[INSERT FIGURE 4.5: ACTUAL DECRYPTION RESULT]`

---

# CHAPTER 5 – TESTING AND EVALUATION

## 5.1 Introduction

This chapter sets out the testing strategy, the test cases and their results.
Detailed execution instructions are in `docs/TEST_PLAN.md`.

## 5.2 Testing Strategy

Four levels were applied. **Unit testing** exercises individual functions —
primality testing, generator order, modular inverse, key generation — in
isolation. **Integration testing** exercises complete text round trips through
the encoding and cryptographic layers together. **Boundary testing** targets the
edges: `m = 1`, `m = p`, `m = p + 1`, empty input, single-character input, and
inputs sized to fall exactly on block boundaries. **Negative testing** supplies
invalid input — malformed ciphertext, non-hexadecimal values, wrong keys,
corrupted key files — and asserts that a specific exception is raised.

A deliberate design choice was to include tests that *demonstrate weaknesses*:
`test_modified_ciphertext_changes_plaintext_predictably` asserts that
multiplying `c2` by 3 yields a plaintext of `3m mod p`, documenting ElGamal's
malleability as executable evidence rather than as a claim in prose.

The automated suite covers the cryptographic core and the encoding layer. The
Tkinter interface is verified manually against the test cases marked "GUI" in
Table 5.1, because automated GUI testing would have added tooling complexity
disproportionate to the project's scope. This is a stated limitation of the
test strategy, not an omission.

## 5.3–5.7 Unit, Functional, Integration, Boundary and Invalid-Input Testing

The suite comprises 88 tests across three modules:

| Module | Tests | Focus |
|---|---|---|
| `tests/test_elgamal.py` | 39 | Primality, safe primes, generators, modular inverse, key generation, integer round trips, probabilistic behaviour, malleability |
| `tests/test_crypto_utils.py` | 32 | Block sizing, text round trips including Unicode and 500-character inputs, ciphertext serialisation, expansion ratio |
| `tests/test_validation.py` | 17 | Public key validation, key manager state, JSON export/import, error paths |

## 5.8 Security Testing

Four security-relevant behaviours are tested directly:

1. **Ephemeral freshness** — 20 encryptions of the same plaintext under the same
   key must produce 20 distinct ciphertexts, and all 20 must decrypt correctly.
2. **Wrong-key behaviour** — decryption with an incorrect `x` must raise an
   error rather than return plausible text.
3. **Malleability** — a tampered `c2` produces a predictably altered plaintext,
   confirming the absence of integrity protection.
4. **Range enforcement** — `m >= p` and `m <= 0` are rejected.

## 5.9 Performance Testing

`benchmark.py` measures key generation (median over repeated trials, because
prime search is a random process with high variance), per-block encryption and
decryption, and full-pipeline timing against message length. It writes three
CSV files, a PNG graph and an environment record. Results are in Chapter 6.

## 5.10 Test Cases and 5.11 Results

**Table 5.1 — Test case specification and results**

Status column: results marked *Pass (reference run)* were obtained by executing
`python -m pytest tests -v` in the development container; **you must re-run them
on your machine and capture the output** before submission. Rows marked
`[TO BE VERIFIED BY ACTUAL EXECUTION]` require manual interaction with the GUI.

| ID | Description | Input | Expected result | Actual result | Status | Evidence |
|---|---|---|---|---|---|---|
| TC01 | Application startup | `python main.py` | Window opens; status "Ready" | | `[TO BE VERIFIED BY ACTUAL EXECUTION]` | Figure 4.1 |
| TC02 | Key generation, 512-bit | Select 512, press Generate | `p`, `g`, `x`, `y` displayed; block size 62 bytes | | `[TO BE VERIFIED BY ACTUAL EXECUTION]` | Figure 4.2 |
| TC03 | Key pair validity | Generated pair | `y == g^x mod p`; `p` prime; `x` in range | Holds for generated pairs | Pass (reference run) | `test_keypair_satisfies_y_equals_g_pow_x` |
| TC04 | Normal plaintext encryption | "Hello, world!" | Ciphertext of `c1:c2` hex lines | Correct format produced | Pass (reference run) | `test_text_encrypt_decrypt_round_trip` |
| TC05 | Valid decryption | Ciphertext from TC04 | Original plaintext recovered | Recovered exactly | Pass (reference run) | same |
| TC06 | Round trip, multiple lengths | 5, 30, 500, 4096 characters | Plaintext recovered exactly | Recovered exactly | Pass (reference run) | `test_text_block_round_trip` |
| TC07 | Empty plaintext | "" | `EncodingError`; GUI shows "Plaintext is empty" | Exception raised | Pass (reference run) + GUI check | `test_encrypting_empty_text_raises`; Figure 5.2 |
| TC08 | Special characters | `!@#$%^&*()_+-=[]{};':",./<>?` | Recovered exactly | Recovered exactly | Pass (reference run) | `test_text_block_round_trip` |
| TC09 | Numeric input | "1234567890" | Recovered exactly | Recovered exactly | Pass (reference run) | same |
| TC10 | Unicode and emoji | "Unicode: … 🔐" | Recovered exactly | Recovered exactly | Pass (reference run) | same |
| TC11 | Long plaintext | 500 and 4096 characters | Multiple blocks; recovered exactly | 67 blocks at 4096 bytes | Pass (reference run) | `test_long_text_is_split_into_multiple_blocks` |
| TC12 | Malformed ciphertext | `deadbeef`, `zzzz:1234`, `dead:beef:cafe` | `CiphertextFormatError` naming the line | Exception raised for all | Pass (reference run) | `test_malformed_ciphertext_is_rejected`; Figure 5.3 |
| TC13 | Missing key | Encrypt before generating keys | Error: generate a key pair first | | `[TO BE VERIFIED BY ACTUAL EXECUTION]` | GUI screenshot |
| TC14 | Incorrect private key | Ciphertext from key A, private key B | `EncodingError`, not garbage text | Exception raised | Pass (reference run) | `test_wrong_private_key_is_reported_not_silently_wrong` |
| TC15 | Message at and beyond the modulus | `m = p`, `m = p + 1`, `m = 0`, `m < 0` | `MessageTooLargeError` | Exception raised for all | Pass (reference run) | `test_message_equal_to_or_larger_than_p_is_rejected` |
| TC16 | Same plaintext encrypted twice | "Repeat me" × 20 | 20 distinct ciphertexts, all decrypting correctly | 20 distinct | Pass (reference run) | `test_encryption_is_probabilistic`; Figure 5.4 |
| TC17 | Clear / reset | Press Reset with data present | All fields cleared; keys discarded | | `[TO BE VERIFIED BY ACTUAL EXECUTION]` | GUI screenshot |
| TC18 | Performance benchmark | `python benchmark.py` | CSVs and graph produced | Produced; see Chapter 6 | Pass (reference run) | `results/` |
| TC19 | Carmichael numbers rejected | 561, 1105 | Reported composite | Reported composite | Pass (reference run) | `test_composites_and_units_are_rejected` |
| TC20 | Generator has full order | Generated `g` | `g^2 ≠ 1`, `g^q ≠ 1`, `g^2q = 1` | Holds | Pass (reference run) | `test_generator_has_full_order` |
| TC21 | Leading null bytes preserved | `"\x00\x00abc"` | Recovered exactly | Recovered exactly | Pass (reference run) | `test_leading_null_bytes_are_preserved` |
| TC22 | Key export and import | Export then import | Same `p`, `g`, `y`, `x` restored | Restored | Pass (reference run) | `test_export_then_import_restores_the_same_keys` |
| TC23 | Mismatched key files rejected | Public A + private B | `KeyManagerError` | Exception raised | Pass (reference run) | `test_import_detects_non_matching_key_files` |
| TC24 | Corrupted key file rejected | Non-JSON, incomplete, non-numeric | `KeyManagerError` | Exception raised for all | Pass (reference run) | three tests in `test_validation.py` |
| TC25 | Malleability demonstrated | `c2 → 3·c2` | Decrypts to `3m mod p` | Confirmed | Pass (reference run) | `test_modified_ciphertext_changes_plaintext_predictably` |
| TC26 | Ciphertext expansion | 38-character message | Ratio > 4 | Ratio > 4 | Pass (reference run) | `test_ciphertext_expansion_is_at_least_four` |

**Reference run summary:** `88 passed in 0.96s` (Python 3.12.3, pytest 9.1.1,
Linux container). `[INSERT YOUR OWN RUN: python -m pytest tests -v]`

## 5.12 Screenshot Evidence

See `docs/SCREENSHOT_PLAN.md` for the exact sequence of actions to perform and
capture. Do not fabricate these images.

## 5.13 Performance Analysis

See Chapter 6.

## 5.14 Security Evaluation

See Section 6.8.

## 5.15 Summary

The system passes an automated suite of 88 tests covering correctness, boundary
conditions, invalid input and probabilistic behaviour, including tests that
document known weaknesses of the scheme. GUI behaviours require manual
verification and are marked accordingly.

---

# CHAPTER 6 – RESULTS AND DISCUSSION

> **Important.** The figures in Sections 6.2–6.7 come from a reference run in
> the development environment recorded in `results/benchmark_environment.txt`
> (CPython 3.12.3 on Linux, x86-64 container). They are included so the analysis
> is concrete. **Re-run `python benchmark.py` on your own machine and replace
> these tables and the graph with your own output**, then update this warning
> box to describe your machine.

## 6.1 Introduction

This chapter reports the observed behaviour of the implementation and discusses
what the results mean.

## 6.2 Key Generation Results

**Table 6.1 — Key generation timing (5 trials per size, reference run)**

| Key size (bits) | Median (ms) | Mean (ms) | Min (ms) | Max (ms) | Std. dev. (ms) |
|---|---|---|---|---|---|
| 256 | 39.2 | 82.1 | 14.7 | 191.3 | 79.2 |
| 512 | 1,205.9 | 1,217.9 | 205.4 | 2,663.6 | 906.9 |
| 1024 | 12,566.3 | 11,857.2 | 1,823.9 | 27,639.9 | 10,523.2 |

Two observations. First, cost grows steeply — roughly 30× from 256 to 512 bits
and a further 10× from 512 to 1024. This is expected: safe-prime generation
requires both `q` and `p = 2q + 1` to be prime, and the density of primes near
`n` is about `1/ln n`, so the probability that a random candidate pair are both
prime falls roughly as `1/(ln n)²` while each Miller–Rabin test itself becomes
more expensive.

Second, the variance is enormous — the standard deviation is comparable to the
mean, and at 1024 bits the fastest trial was 15 times faster than the slowest.
This is not measurement noise but an intrinsic property of the algorithm: prime
generation is a random search, so the running time follows a geometric
distribution. This is precisely why the benchmark reports the median and the
spread rather than a single mean, and why five trials are the minimum
meaningful sample. It is also why key generation runs on a worker thread in the
GUI (Section 4.15): a 27-second freeze would be indistinguishable from a crash.

The 2048-bit option is offered in the interface but was excluded from the
reference benchmark because a single trial can take several minutes in CPython.
`[OPTIONAL: run python benchmark.py --sizes 2048 --key-trials 1 and report it]`

## 6.3 Encryption Results

**Table 6.2 — Per-block operation timing (mean of 50 trials, reference run)**

| Key size (bits) | Bytes per block | Encrypt (ms/block) | Decrypt (ms/block) | Ratio enc:dec |
|---|---|---|---|---|
| 256 | 30 | 0.228 | 0.152 | 1.50 |
| 512 | 62 | 1.323 | 0.745 | 1.78 |
| 1024 | 126 | 7.466 | 3.966 | 1.88 |

Encryption consistently costs close to twice decryption. This matches the
algorithm exactly: encryption performs two modular exponentiations (`g^k` and
`y^k`) while decryption performs one (`c1^x`) plus a comparatively cheap
Extended Euclidean inversion. The measured ratio approaching 2 as key size
grows is direct experimental confirmation that exponentiation dominates and
that the inversion cost becomes negligible in comparison.

Cost per block grows roughly by a factor of 5–6 per doubling of key size,
consistent with modular exponentiation being cubic in the bit length for
schoolbook multiplication (2³ = 8, reduced in practice by CPython's use of
Karatsuba multiplication for large integers).

## 6.4 Decryption Results

Decryption recovered the original plaintext exactly in every round-trip test,
across all tested key sizes, message lengths from 1 to 4,096 characters, and
inputs including ASCII, punctuation, digits, multi-byte UTF-8 characters, emoji
and embedded null bytes. Decryption with a wrong private key never produced
readable output; it raised `EncodingError` because the `0x01` marker byte was
absent from the recovered block.

## 6.5 Correctness

Objective O1 and O2 are met: the round-trip property `D(E(m)) = m` held in
every one of the automated tests, and the `m < p` constraint was satisfied by
construction, verified by `test_every_block_is_smaller_than_p` and by the
explicit rejection of `m >= p` in `test_message_equal_to_or_larger_than_p_is_rejected`.

## 6.6 Edge Cases

| Edge case | Behaviour observed |
|---|---|
| Empty plaintext | Rejected with a clear message |
| Single character | Encrypted and recovered correctly (one block) |
| Exactly one block boundary | Correct block count; recovered exactly |
| Leading null bytes | Preserved by the `0x01` marker |
| `m = 1` | Encrypted and recovered correctly |
| `m = p`, `m = p + 1`, `m = 0`, `m < 0` | Rejected with `MessageTooLargeError` |
| Ciphertext components ≥ `p` | Rejected before arithmetic |
| Truncated ciphertext line | `CiphertextFormatError` naming the line |
| Carmichael numbers 561, 1105 | Correctly identified as composite |

## 6.7 Performance and Message Size

**Table 6.3 — Message size scaling at 512 bits (reference run)**

| Plaintext (bytes) | Blocks | Ciphertext (bytes) | Expansion ratio | Encrypt (ms) | Decrypt (ms) |
|---|---|---|---|---|---|
| 16 | 1 | 257 | 16.06 | 1.35 | 0.80 |
| 64 | 2 | 515 | 8.05 | 2.69 | 1.54 |
| 256 | 5 | 1,288 | 5.03 | 6.64 | 3.73 |
| 1,024 | 17 | 4,383 | 4.28 | 22.50 | 12.61 |
| 4,096 | 67 | 17,267 | 4.22 | 86.17 | 47.43 |

Timing scales linearly with the number of blocks, as expected for independent
per-block encryption.

The expansion ratio deserves attention because it is frequently misreported.
ElGamal's intrinsic expansion is 2:1 — one plaintext group element becomes two
ciphertext group elements. The ratios above are roughly 4:1 asymptotically
because the hexadecimal transport encoding doubles the size again; it would be
2:1 if ciphertexts were transmitted as raw bytes. The much higher ratio for
short messages (16.06 for a 16-byte message) is a *padding* effect: a 16-byte
message still occupies a full 512-bit block pair, so the fixed per-block cost
is amortised over very little data. This is a practical argument for hybrid
encryption: ElGamal is well suited to encrypting a short symmetric key, and
poorly suited to bulk data.

**[INSERT FIGURE 6.1: YOUR OWN `results/benchmark_plot.png`]**

## 6.8 Security Discussion

**Table 6.4 — Security properties**

| Property | Provided? | Basis |
|---|---|---|
| Confidentiality (one-wayness) | Yes, under CDH with adequate key size | ElGamal (1985) |
| Semantic security (IND-CPA) | **No, as configured** | Requires DDH in a prime-order subgroup (Tsiounis & Yung, 1998); full `Z_p*` leaks the Legendre symbol |
| Integrity | **No** | Demonstrated by TC25 |
| Authentication | **No** | Anyone holding the public key can encrypt |
| Non-repudiation | **No** | No signature scheme implemented |
| IND-CCA security | **No** | Malleability precludes it |
| Forward secrecy | **No** | Compromise of `x` exposes all past ciphertexts |
| Side-channel resistance | **No** | No constant-time implementation |

**Key size.** NIST SP 800-57 Part 1 Rev. 5 (Barker, 2020) establishes the
current key-size guidance; finite-field schemes require moduli of at least 2048
bits for contemporary protection. The 256- and 512-bit options in this
application exist so that key generation completes within a live demonstration,
and are stated in the interface and documentation to be inadequate for real
use. Table 6.1 makes the trade-off concrete: the configuration that is fast
enough to demonstrate is precisely the configuration that is too weak to trust.

**The subgroup issue.** As discussed in Section 2.14, using a generator of the
full group `Z_p*` means `c2` reveals whether `m` is a quadratic residue, so one
bit leaks per block and DDH does not hold. Encrypting into the prime-order
subgroup of quadratic residues would restore semantic security but requires an
invertible map from arbitrary byte strings into that subgroup, which
substantially complicates the encoding layer. The simpler encoding was chosen
deliberately for an educational implementation, and the consequence is reported
rather than concealed. Section 7.5 lists the correction as future work.

**Ephemeral reuse.** If `k` were reused for two messages under the same public
key, then `c1` would be identical and `c2/c2' = m/m'`, so an attacker knowing
one plaintext would recover the other. The implementation draws `k` from
`secrets` on every call to `encrypt_int`, and `encrypt_int` is called once per
block; TC16 confirms 20 distinct ciphertexts for 20 encryptions of identical
plaintext. The historical significance of this failure mode — the same class of
error that broke the PlayStation 3 signing key through a repeated nonce in
ECDSA — makes it worth testing rather than assuming.

**Private key exposure.** Anyone obtaining `x` can decrypt every message
encrypted under the corresponding `y`, past and future. There is no forward
secrecy. Exported private keys are unencrypted JSON, which is acceptable only
because this is a classroom artefact.

**Honest summary.** The implementation is a correct realisation of textbook
ElGamal, providing confidentiality against a passive adversary who cannot solve
the discrete logarithm problem for the chosen key size, and nothing else. It is
not a secure messaging system, is not production-ready, and no claim of
"military-grade" or comparable security is made anywhere in this work.

## 6.9 Discussion

The results support three broader points. First, the cost asymmetry between key
generation (seconds) and encryption (milliseconds) explains why public-key
domain parameters are generated once and reused, and why real protocols use
public-key cryptography to establish symmetric keys rather than to encrypt
data. Second, the expansion data quantifies the same conclusion from the
bandwidth side. Third, and most important for this assessment, the exercise of
implementing the scheme surfaced questions that reading the formulae did not:
what to do when a block integer would exceed `p`, what happens to leading zero
bytes, and how a wrong key should fail. Each has a defensible answer in the
implementation, and each is the kind of decision that separates a correct
implementation from one that merely appears to work.

## 6.10 Limitations

The limitations of Section 1.7 are confirmed by the evaluation. In addition:
performance figures reflect CPython and are not representative of optimised
implementations; the automated suite does not cover the Tkinter layer; and the
benchmark measures a single machine under uncontrolled load.

## 6.11 Summary

The implementation is functionally correct across all tested inputs, exhibits
the expected performance characteristics of ElGamal, and provides
confidentiality but no integrity, authentication or semantic security in its
current configuration.

---

# CHAPTER 7 – CONCLUSION AND FUTURE WORK

## 7.1 Conclusion

This project produced a working Python desktop application implementing the
ElGamal public-key cryptosystem, in which the complete cryptographic core —
safe-prime generation, generator selection, key generation, modular
exponentiation, modular inversion, encryption and decryption — is implemented
directly rather than delegated to a library. The application encrypts and
decrypts arbitrary UTF-8 text through a block scheme that guarantees the
`0 < m < p` constraint by construction, draws every ephemeral value from the
operating system CSPRNG, validates all input, and reports every failure
specifically. It was verified by 88 automated tests and characterised by a
reproducible benchmark.

## 7.2 Objective Achievement

| Objective | Status | Evidence |
|---|---|---|
| O1 — Implement ElGamal from first principles | Achieved | `elgamal.py`; no third-party imports |
| O2 — Correct message representation with `m < p` guaranteed | Achieved | Section 3.14; TC15, TC21 |
| O3 — Tkinter interface with all required operations | Achieved | `gui.py`; Figures 4.1–4.5 |
| O4 — Fresh CSPRNG ephemeral per encryption | Achieved | Section 4.13; TC16 |
| O5 — Systematic automated testing | Achieved | 88 tests; Table 5.1 |
| O6 — Reproducible performance measurement | Achieved | `benchmark.py`; Tables 6.1–6.3 |
| O7 — Accurate security evaluation | Achieved | Section 6.8; Table 6.4 |

## 7.3 Contributions

A transparent, fully commented ElGamal implementation suitable for study; a
block-encoding design that enforces the modulus constraint structurally rather
than by assumption; a test suite that documents the scheme's weaknesses as
executable assertions; and a measured account of ElGamal's cost and expansion
characteristics.

## 7.4 Limitations

As set out in Sections 1.7 and 6.10: textbook ElGamal with no integrity or
authentication; not semantically secure in the full-group configuration;
demonstration key sizes below current recommendations; unencrypted key storage;
CPython performance; no side-channel resistance; no automated GUI testing.

## 7.5 Future Work

1. **Encrypt into a prime-order subgroup.** Restrict messages to the subgroup of
   quadratic residues with an invertible encoding, restoring semantic security
   under DDH (the most significant correction available).
2. **Add integrity and authentication.** Apply an encrypt-then-MAC construction,
   or implement a chosen-ciphertext-secure scheme such as Cramer–Shoup or DHIES.
3. **Hybrid encryption.** Use ElGamal to transport an AES key and AES-GCM for
   the payload, eliminating both the expansion and the performance penalty for
   large messages.
4. **ElGamal digital signatures.** Implement the signature scheme from the same
   1985 paper, adding authentication and non-repudiation.
5. **Encrypted key storage.** Protect the private key with a passphrase-derived
   key and an authenticated cipher.
6. **Elliptic-curve ElGamal.** Equivalent security at far smaller key sizes.
7. **Automated GUI testing** and constant-time arithmetic.

---

# REFERENCES

*(APA 7th edition. Verification status for each entry is recorded in
`docs/AUDITS.md`.)*

Barker, E. (2020). *Recommendation for key management: Part 1 – General* (NIST
Special Publication 800-57 Part 1, Revision 5). National Institute of Standards
and Technology. https://doi.org/10.6028/NIST.SP.800-57pt1r5

Boneh, D. (1998). The decision Diffie-Hellman problem. In J. P. Buhler (Ed.),
*Algorithmic number theory: Third international symposium, ANTS-III* (Lecture
Notes in Computer Science, Vol. 1423, pp. 48–63). Springer.
https://doi.org/10.1007/BFb0054851

Diffie, W., & Hellman, M. (1976). New directions in cryptography. *IEEE
Transactions on Information Theory, 22*(6), 644–654.
https://doi.org/10.1109/TIT.1976.1055638

ElGamal, T. (1985). A public key cryptosystem and a signature scheme based on
discrete logarithms. *IEEE Transactions on Information Theory, 31*(4), 469–472.
https://doi.org/10.1109/TIT.1985.1057074

Goldwasser, S., & Micali, S. (1984). Probabilistic encryption. *Journal of
Computer and System Sciences, 28*(2), 270–299.
https://doi.org/10.1016/0022-0000(84)90070-9

Katz, J., & Lindell, Y. (2021). *Introduction to modern cryptography* (3rd ed.).
CRC Press.

Menezes, A. J., van Oorschot, P. C., & Vanstone, S. A. (1996). *Handbook of
applied cryptography*. CRC Press.

Paar, C., & Pelzl, J. (2010). *Understanding cryptography: A textbook for
students and practitioners*. Springer. https://doi.org/10.1007/978-3-642-04101-3

Pohlig, S., & Hellman, M. (1978). An improved algorithm for computing logarithms
over GF(p) and its cryptographic significance. *IEEE Transactions on Information
Theory, 24*(1), 106–110. https://doi.org/10.1109/TIT.1978.1055817

Python Software Foundation. (n.d.). *secrets — Generate secure random numbers
for managing secrets*. Python 3 documentation. Retrieved September 18, 2026,
from https://docs.python.org/3/library/secrets.html

Rivest, R. L., Shamir, A., & Adleman, L. (1978). A method for obtaining digital
signatures and public-key cryptosystems. *Communications of the ACM, 21*(2),
120–126. https://doi.org/10.1145/359340.359342

Tsiounis, Y., & Yung, M. (1998). On the security of ElGamal based encryption. In
H. Imai & Y. Zheng (Eds.), *Public key cryptography, PKC '98* (Lecture Notes in
Computer Science, Vol. 1431, pp. 117–134). Springer.
https://doi.org/10.1007/BFb0054019

---

# APPENDICES

**Appendix A — Full source code.** `elgamal.py`, `crypto_utils.py`,
`key_manager.py`, `gui.py`, `main.py`, `benchmark.py`. Paste with syntax
highlighting, or reference the repository at `[INSERT ACTUAL GITHUB URL]`.

**Appendix B — Test suite source.** `tests/test_elgamal.py`,
`tests/test_crypto_utils.py`, `tests/test_validation.py`.

**Appendix C — Full test output.** `[INSERT YOUR OWN pytest OUTPUT]`

**Appendix D — Benchmark CSV data.** `results/benchmark_keygen.csv`,
`benchmark_operations.csv`, `benchmark_message_sizes.csv`,
`benchmark_environment.txt` — regenerated on your machine.

**Appendix E — Diagram sources.** Eight editable `.drawio` files in
`diagrams/`, regenerable with `python diagrams/make_diagrams.py`.

**Appendix F — User guide.** `docs/USER_GUIDE.md`.

**Appendix G — Generative AI disclosure.** State the tools used, what they were
used for, and confirm that you understand and can explain all submitted work,
in accordance with the CCS2243 academic integrity requirements.
