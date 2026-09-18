# Audits: References, Rubric Traceability and Quality

---

# PART 1 — REFERENCE VALIDITY AUDIT

Every reference in the report was checked against web sources before being
included. This table records **what was actually checked**, not a blanket claim
of verification. Where a bibliographic element could not be confirmed from an
authoritative source it is marked accordingly, with an instruction.

Legend: **Y** = confirmed from at least one authoritative or independent
source · **Y²** = confirmed from two or more independent sources ·
**P** = partially confirmed (single source, or a secondary citation) ·
**N** = not confirmed.

| # | Reference | Exists | Author | Title | Year | Vol/Pages | DOI/URL | Cited in text | APA 7 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | ElGamal (1985), *IEEE Trans. Inf. Theory*, 31(4), 469–472 | Y² | Y² | Y² | Y² | Y² | **P** — DOI `10.1109/TIT.1985.1057074` appears in a publisher reference list; not resolved directly | §1.1, 2.9, 6.8 | Y |
| 2 | Diffie & Hellman (1976), 22(6), 644–654 | Y² | Y² | Y² | Y² | Y² | **P** — DOI `10.1109/TIT.1976.1055638` seen in two independent reference lists | §1.1, 2.5 | Y |
| 3 | Rivest, Shamir & Adleman (1978), *CACM*, 21(2), 120–126 | Y² | Y² | Y² | Y² | Y² | **N** — DOI `10.1145/359340.359342` was *not* confirmed in searching | §1.1, 2.6 | Y |
| 4 | Goldwasser & Micali (1984), *JCSS*, 28(2), 270–299 | Y² | Y² | Y² | Y² | Y² | Y — DOI `10.1016/0022-0000(84)90070-9` confirmed in a Springer reference list | §1.1, 2.6 | Y |
| 5 | Menezes, van Oorschot & Vanstone (1996), *Handbook of Applied Cryptography*, CRC Press | Y² | Y² | Y² | Y² | ISBN 0-8493-8523-7 confirmed | Y — free official copy exists at the University of Waterloo CACR site; **confirm the exact URL yourself before adding it** | §2.2, 2.3, 2.7, 2.8 | Y |
| 6 | Katz & Lindell, *Introduction to Modern Cryptography* (3rd ed.), CRC Press | Y² | Y² | Y² | **P** — library catalogues give 2021, some vendors give 2020. The report uses 2021; **check your library's record and use one year consistently** | ISBN 9780815354369 confirmed | n/a (book) | §2.17 | Y |
| 7 | Paar & Pelzl (2010), *Understanding Cryptography*, Springer | Y² | Y² | Y² | Y² | ISBN 978-3-642-04100-6 | Y — DOI `10.1007/978-3-642-04101-3` confirmed | §2.2, 2.4, 2.5, 2.7 | Y |
| 8 | Barker (2020), NIST SP 800-57 Part 1 Rev. 5 | Y² | Y² | Y² | Y² | n/a | Y² — DOI `10.6028/NIST.SP.800-57pt1r5` confirmed on the NIST publication itself | §2.17, 6.8 | Y |
| 9 | Tsiounis & Yung (1998), PKC '98, LNCS 1431, 117–134 | Y² | Y² | Y² | Y² | Y — pages confirmed by a Google Research listing | Y — DOI `10.1007/BFb0054019` matched the correct abstract | §2.14, 6.8 | Y |
| 10 | Boneh (1998), ANTS-III, LNCS 1423, 48–63 | Y | Y | Y | Y | **P** — pages from one source | **P** — DOI `10.1007/BFb0054851` from one source only | §2.8 | Y |
| 11 | Pohlig & Hellman (1978), 24(1), 106–110 | Y² | Y² | Y² | Y² | Y² | **N** — DOI `10.1109/TIT.1978.1055817` was *not* confirmed | §2.8 | Y |
| 12 | Python Software Foundation, `secrets` documentation | Y² | n/a (corporate author) | Y² | n.d. | n/a | Y² — https://docs.python.org/3/library/secrets.html confirmed live | §2.17, 4.13 | Y |

## Action required before submission

1. **References 3 and 11 (RSA; Pohlig & Hellman): the DOIs are not verified.**
   Either resolve them yourself at https://doi.org (paste the DOI; it must land
   on the correct paper) or **delete the DOI from the reference**. APA 7 does
   not require a DOI when none is available. Do not submit an unverified DOI.
2. **References 1, 2, 10:** resolve the DOIs the same way. They are very likely
   correct — they appear in publisher reference lists — but "likely correct" is
   not verified.
3. **Reference 6 (Katz & Lindell):** settle on 2021 or 2020 based on the copy
   you can actually access, and make the in-text citation match.
4. **Reference 5 (Menezes et al.):** if you cite the free online edition, visit
   the CACR page first and copy the URL exactly as it appears.
5. Every reference in the list is cited at least once in the text, and every
   in-text citation appears in the list. Re-check this after any edit.

## Citation integrity notes

- Tsiounis and Yung (1998) is cited **only** for the claim that ElGamal's
  semantic security is equivalent to DDH **for messages in an appropriate
  subgroup**. That proviso is part of their result; do not cite them for an
  unqualified claim of semantic security, which the paper does not support for
  the full-group configuration used here.
- Barker (2020) is cited only for key-management and key-size guidance.
- Goldwasser and Micali (1984) is cited for the necessity of probabilistic
  encryption, which is their result; they did not write about ElGamal, which
  postdates them.
- No source is cited for a claim it does not make, and no reference is included
  that is not used.

---

# PART 2 — RUBRIC TRACEABILITY MATRIX

Mapped against the official CCS2243 assessment rubric.

| # | Criterion (weight) | Required evidence | Project component | Report location | Diagram / test / screenshot evidence | Status | Improvement needed |
|---|---|---|---|---|---|---|---|
| 1 | **Project Proposal & Scope (5%)** | Precise, feasible, justified problem, objectives, scope, technique | Project definition | §1.2 Problem Statement, §1.3 Aim, §1.4 Objectives O1–O7, §1.5 Scope, §1.6 Significance, §1.7 Limitations | — | **Complete in draft** | If a separate proposal was submitted earlier, ensure the title, objectives and scope here match it exactly |
| 2 | **Literature Review & Cryptographic Understanding (10%)** | Accurate, thorough treatment of concepts, security properties, algorithm operation, strengths, limitations, well-integrated sources | Chapter 2 | §2.1–2.20, incl. correctness proof (2.13), security properties (2.14), comparison table (2.18), gap (2.19) | 12 verified references; audit in Part 1 | **Complete in draft** | Resolve the DOI items in Part 1 |
| 3 | **System Design (10%)** | Complete, logical design; diagrams showing components, data/key flow, inputs/outputs, security-relevant decisions | `diagrams/` (8 editable `.drawio` files) | §3.6–3.17 | Fig 3.1 architecture, 3.2 use case, 3.3 DFD, 3.4–3.7 flowcharts, 3.8 class diagram | **Sources complete; export pending** | Export each `.drawio` to PNG and insert into the report |
| 4 | **Implementation & Functional Correctness (30%)** | Fully functional, correct cryptographic operations; organised, robust code; appropriate key/data handling; student understands it | `elgamal.py`, `crypto_utils.py`, `key_manager.py`, `gui.py`, `main.py` | Chapter 4 (§4.1–4.19) | 88 passing tests; Figures 4.1–4.5 | **Code complete and tested; screenshots pending** | Run the application, capture Figures 4.1–4.5 per `SCREENSHOT_PLAN.md` |
| 5 | **Testing and Evaluation (15%)** | Systematic normal and edge cases; expected vs actual; evidence; evaluation of correctness, performance, security, limitations | `tests/` (3 modules), `benchmark.py` | Chapter 5 (Table 5.1, TC01–TC26), §6.2–6.8 | `results/` CSVs and graph; Figures 5.1–5.4 | **Automated tests complete; GUI rows and your own figures pending** | Run pytest and benchmark on your machine; complete the `[TO BE VERIFIED]` rows |
| 6 | **Final Report & Technical Documentation (20%)** | Complete, technically accurate, well-organised, professional; documents theory, design, implementation, testing, results, limitations, references | `docs/REPORT_DRAFT.md` | Chapters 1–7, References, Appendices A–G | Full document | **Draft complete; evidence placeholders pending** | Replace all `[INSERT ...]` markers; convert to PDF as required by the submission format |
| 7 | **Presentation, Demonstration & Q&A (10%)** | Confident structured presentation; working live demo; accurate explanation of process, design choices and code | `docs/PRESENTATION_AND_VIVA.md` | 12 slides + notes, demo script, 27 Q&A | Live demonstration | **Materials complete; rehearsal required** | Rehearse the demo end to end at least three times, including the failure paths |

## Submission requirements from the assessment document

| Requirement | Status |
|---|---|
| PDF final report | Convert `REPORT_DRAFT.md` after inserting evidence — **pending** |
| Source code / project files | Complete — the whole `ElGamal-Encryption/` directory |
| APA 7th edition citations | Applied throughout; see Part 1 |
| Individual work | Yes — single-student project |
| Generative AI disclosure | **Required.** AI assistance was used in producing this project and must be disclosed per the assessment's academic integrity section. Appendix G of the report is the place for it. You must be able to explain all submitted work |
| Acknowledge borrowed code/libraries | No third-party code is used; the standard library modules used are named in §4.5 |
| Ethical / authorised use | Satisfied — the system operates only on the user's own input; no external system is accessed |

---

# PART 3 — FINAL QUALITY AUDIT

## Audit 1 — Cryptography

| Check | Status | Note |
|---|---|---|
| ElGamal mathematics correct | ✔ | Verified against ElGamal (1985) and Menezes et al. (1996) |
| Key generation correct | ✔ | Safe prime, verified generator, `x` in `[2, p−2]`, `y = g^x mod p` |
| Encryption correct | ✔ | `c1 = g^k`, `c2 = m·y^k`, fresh `k` per block |
| Decryption correct | ✔ | `s = c1^x`, `m = c2·s⁻¹`; 88 tests confirm round trips |
| Modular inverse correct | ✔ | Extended Euclidean Algorithm; tested against `a·a⁻¹ ≡ 1` |
| Random `k` handled correctly | ✔ | `secrets`, fresh per block; 20-sample distinctness test |
| Message representation correct | ✔ | Block scheme with marker byte; leading nulls preserved |
| `m < p` handled, not silently failing | ✔ | Guaranteed by block sizing; explicit `MessageTooLargeError` |
| Security limitations stated correctly | ✔ | Including the subgroup/Legendre-symbol issue, which most student projects omit |
| No misleading security claims | ✔ | No "military-grade", no "production-ready", no "completely secure" anywhere |

## Audit 2 — Software

| Check | Status | Note |
|---|---|---|
| All files complete, no placeholders in code | ✔ | No `TODO`, no `pass  # implement later` |
| Imports correct | ✔ | All modules compile; test suite imports resolve |
| Encryption works | ✔ | Verified by execution |
| Decryption works | ✔ | Verified by execution |
| Validation works | ✔ | Verified by execution |
| Error handling works | ✔ | Every error path has a test |
| Tests match the actual code API | ✔ | 88 passed in a reference run |
| Benchmark matches the actual code | ✔ | Executed; CSVs and graph produced |
| GUI works | **Not verified here** | Tkinter is unavailable in the development container; `gui.py` compiles cleanly but **must be run and screenshotted on your machine** |

## Audit 3 — Diagrams

| Check | Status | Note |
|---|---|---|
| Architecture matches implementation | ✔ | Every box corresponds to a real module |
| Use case matches implementation | ✔ | Eight use cases, all implemented |
| DFD matches implementation | ✔ | No database shown, because none exists |
| Flowcharts match the actual algorithms | ✔ | Key generation flowchart reflects the staged prime search as coded |
| Class diagram matches the code | ✔ | Generated from the actual class and function names |
| ERD included only if justified | ✔ | **Not included.** See the statement below |
| draw.io files editable | ✔ | Uncompressed mxGraphModel XML; all eight parse as valid XML |
| No contradictory components | ✔ | Diagrams and text reviewed against the source |

**ERD statement for the report:** "An entity-relationship diagram was not
included because the implemented application does not require a persistent
relational database. The only persistent artefacts are two optional JSON key
files, which have no relational structure and are described in Section 3.15."
This statement is accurate for the implementation as delivered.

## Audit 4 — Report

| Check | Status |
|---|---|
| Problem statement clear and specific | ✔ (three concrete sub-problems) |
| Aim clear | ✔ |
| Objectives measurable | ✔ (O1–O7, each with named evidence) |
| Scope realistic and bounded | ✔ (explicit out-of-scope list) |
| Literature review substantive | ✔ (20 sections, 12 verified sources) |
| Theory accurate | ✔ (correctness proof included) |
| Design documented | ✔ (8 diagrams, requirements tables) |
| Implementation documented | ✔ (with code extracts and rationale) |
| Testing documented | ✔ (26 test cases, strategy, levels) |
| Results supported by evidence | **Partly** — reference-run figures present and labelled; **your figures required** |
| Security evaluated | ✔ (Table 6.4, honest on what is absent) |
| Limitations discussed | ✔ (§1.7, §6.10, §7.4) |
| Conclusion matches findings | ✔ |

## Audit 5 — References

| Check | Status |
|---|---|
| Every reference exists | ✔ (all 12 verified to exist) |
| Every citation is real | ✔ (none fabricated) |
| URLs verified | ✔ (the one URL cited, the Python docs, was confirmed live) |
| DOIs verified | **Partly** — see Part 1; four need resolving, two should be removed if they cannot be confirmed |
| No fake references | ✔ |
| No fake DOI | ✔ (no DOI was invented; unconfirmed ones are flagged rather than presented as verified) |
| No invalid URL | ✔ |
| APA 7 consistent | ✔ |
| In-text citations match the reference list | ✔ (12 of 12 cited) |
| Claims supported by the cited sources | ✔ (see the citation integrity notes in Part 1) |

## Audit 6 — Evidence

| Check | Status |
|---|---|
| No fabricated screenshot | ✔ — no screenshot exists yet; all are marked `[INSERT ...]` |
| No fabricated test result | ✔ — the 88-pass result is from a real execution and is labelled a *reference run*; GUI rows are marked `[TO BE VERIFIED BY ACTUAL EXECUTION]` |
| No fabricated performance result | ✔ — all figures in Tables 6.1–6.3 come from a real `benchmark.py` run, with the environment recorded in `results/benchmark_environment.txt`, and are explicitly flagged as needing replacement |
| No fabricated GitHub URL | ✔ — `[INSERT ACTUAL GITHUB URL]` throughout |
| Execution-dependent claims marked | ✔ |

---

# PART 4 — WHAT REMAINS FOR YOU TO DO

Ordered by priority.

1. **Run the application** (`python main.py`) and confirm it behaves as
   documented. The GUI has not been executed in this environment.
2. **Capture the screenshots** listed in `SCREENSHOT_PLAN.md`.
3. **Run the tests** on your machine, save the output, screenshot the summary
   line, and complete the `[TO BE VERIFIED]` rows of Table 5.1.
4. **Run the benchmark** on your machine and replace Tables 6.1–6.3 and
   Figure 6.1 with your own numbers, updating the warning box in Chapter 6.
5. **Export the eight diagrams** from draw.io as PNG and insert them.
6. **Resolve or remove the four unverified DOIs** (Part 1).
7. **Create the GitHub repository**, push the project, and replace every
   `[INSERT ACTUAL GITHUB URL]`.
8. **Fill in the environment table** in §4.2 with your actual Python version,
   OS and hardware.
9. **Write the AI disclosure** (Appendix G) in line with the assessment's
   academic integrity requirements.
10. **Convert the report to PDF** and submit it with the source files.
11. **Rehearse the demonstration** end to end, including the deliberate failure
    paths, and work through all 27 viva questions until you can answer them
    without the notes.
