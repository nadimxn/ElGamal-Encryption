# Test Plan

## 1. Purpose

To verify that the implementation is functionally correct, handles boundary
conditions and invalid input safely, and behaves probabilistically as ElGamal
requires.

## 2. Levels of testing

| Level | Scope | Method |
|---|---|---|
| Unit | Individual functions in `elgamal.py` and `crypto_utils.py` | Automated (pytest) |
| Integration | Full text round trip across encoding and cryptographic layers | Automated |
| Boundary | `m = 1`, `m = p`, `m = p+1`, `m = 0`, empty input, block boundaries | Automated |
| Negative | Malformed ciphertext, wrong key, corrupted key files | Automated |
| Security-behaviour | Ephemeral freshness, malleability, wrong-key failure | Automated |
| GUI / functional | Startup, buttons, error dialogs, reset | Manual |
| Performance | Key generation, encryption, decryption, expansion | Automated (`benchmark.py`) |

## 3. Running the automated suite

```bash
cd ElGamal-Encryption
python -m pytest tests -v
```

To save the output for your appendix:

```bash
python -m pytest tests -v > results/test_output.txt
```

Expected: all tests pass. A reference run in the development container reported
`88 passed in 0.96s` under Python 3.12.3 with pytest 9.1.1. **Your own run is
the evidence that belongs in the report** — do not quote the reference figure
as if it were yours.

To see the three security-behaviour tests specifically:

```bash
python -m pytest tests -v -k "probabilistic or malleab or wrong_private_key"
```

## 4. Running the benchmark

```bash
python benchmark.py --note "Windows 11, Intel i5-1135G7, 16 GB RAM"
```

Useful variants:

```bash
python benchmark.py --sizes 256 512 --key-trials 10   # faster, more stable medians
python benchmark.py --sizes 2048 --key-trials 1       # slow; one 2048-bit sample
python benchmark.py --no-plot                         # if matplotlib is unavailable
```

Outputs land in `results/`: three CSV files, `benchmark_plot.png` and
`benchmark_environment.txt`. Close other applications before running, and note
that key generation timing varies by an order of magnitude between runs — this
is intrinsic to prime search, not a fault in the measurement.

## 5. Manual GUI test procedure

Perform these in order and record the outcome in the Table 5.1 column marked
`[TO BE VERIFIED BY ACTUAL EXECUTION]`.

| ID | Action | Expected |
|---|---|---|
| TC01 | `python main.py` | Window opens; status "Ready. Generate a key pair to begin." |
| TC13 | Type text, press **Encrypt** *before* generating keys | Error dialog and red status: generate a key pair first |
| TC02 | Select 512, press **Generate Key Pair** | Progress bar runs; `p`, `g`, `x`, `y` appear; block size shows 62 bytes |
| TC04 | Type `Hello, world!`, press **Encrypt** | Ciphertext lines appear in `c1:c2` hex form |
| TC16 | Press **Encrypt** again without changing the text | A completely different ciphertext |
| TC05 | Press **Copy to Decryption Pane**, then **Decrypt** | `Hello, world!` recovered; green status |
| TC07 | Press **Clear / Reset**, generate keys, press **Encrypt** with an empty box | Error: plaintext is empty |
| TC12 | Paste `notaciphertext` into the decryption box, press **Decrypt** | `CiphertextFormatError` message naming the problem |
| TC12b | Delete the `:` from one ciphertext line, press **Decrypt** | Error naming the offending line number |
| TC14 | Encrypt, press **Reset**, generate a *new* key pair, paste the old ciphertext, press **Decrypt** | Error, not garbage text |
| TC11 | Paste a paragraph of 500+ characters, encrypt and decrypt | Many ciphertext lines; text recovered exactly |
| TC17 | With all fields populated, press **Clear / Reset** | All boxes empty; key fields show `-` |

## 6. Evidence rules

- Record **Actual Result** only after you have run the step.
- Write **Pass** only when the observed result matches the expected result.
- If something fails, record the failure and what you changed. A documented and
  fixed failure is stronger evidence of real testing than a table of
  unblemished passes.
- Never copy a test outcome from this repository into your report as your own
  observation.
