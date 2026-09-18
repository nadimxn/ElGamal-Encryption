# Screenshot Acquisition Plan

Every figure below must be captured from your own running system. Do not
fabricate, edit or reuse images from any other source.

**Capture tips.** On Windows use `Win + Shift + S`. Set the key size to 512 so
the numbers are large enough to look serious but the window still fits. Use a
consistent test message — `CCS2243 ElGamal demonstration by S M Nadim Mahmud` —
so the figures tell one coherent story. Capture the whole application window,
including the status bar, since the status text is what evidences the outcome.
Save as PNG into `screenshots/` with the filenames given.

| Figure | Filename | What to do | What must be visible |
|---|---|---|---|
| 4.1 | `01_home_screen.png` | Launch `python main.py`, change nothing | Empty fields, key values showing `-`, status "Ready" |
| 4.2 | `02_key_generation.png` | Select 512, press Generate Key Pair, wait | Abbreviated `p`, `g`, `x`, `y`, block size, green status |
| 4.3 | `03_full_key_values.png` | Press Show Full Key Values | The dialog with complete `p`, `g`, `y` and the private `x` |
| 4.4 | `04_encryption.png` | Type the test message, press Encrypt | Plaintext and ciphertext both visible, status showing block count |
| 4.5 | `05_decryption.png` | Copy to Decryption Pane, press Decrypt | Recovered plaintext identical to the original, green status |
| 5.2 | `06_error_empty.png` | Reset, generate keys, press Encrypt with an empty box | Error dialog and red status |
| 5.3 | `07_error_malformed.png` | Paste `notaciphertext`, press Decrypt | Error message naming the format problem |
| 5.3b | `08_error_wrong_key.png` | Encrypt, reset, generate new keys, decrypt the old ciphertext | Error, and an empty recovered-plaintext box |
| 5.4 | `09_probabilistic_1.png` | Encrypt the test message | Ciphertext (first encryption) |
| 5.4 | `10_probabilistic_2.png` | Press Encrypt again, unchanged input | A visibly different ciphertext |
| 5.1 | `11_test_run.png` | Terminal: `python -m pytest tests -v` | The final summary line with the pass count |
| 6.1 | `12_benchmark_run.png` | Terminal: `python benchmark.py` | The printed timings |
| 6.1 | `results/benchmark_plot.png` | Produced automatically | The three-panel graph from **your** run |
| 4.x | `13_long_message.png` | Encrypt a 500-character paragraph | Multiple ciphertext lines |
| — | `14_key_files.png` (optional) | Export keys, open the folder | The two JSON files |

Figures 5.4 (`09` and `10`) are the most valuable pair in the report: placed
side by side they demonstrate probabilistic encryption visually, which is
exactly what a viva examiner will ask you to explain.

For the diagrams, open each `.drawio` file at https://app.diagrams.net and
export as PNG with a transparent background at 200% zoom, saving into
`diagrams/` as `system_architecture.png` and so on.
