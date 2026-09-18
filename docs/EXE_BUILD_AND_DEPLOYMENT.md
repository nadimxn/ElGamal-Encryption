# Building and Deploying the Windows Executable

ElGamal Encryption Implementation — CCS2243 Cryptography Essential

This document covers building `ElGamal-Encryption.exe`, testing it, and
publishing it so that a marker can download and run it without installing
Python.

---

## 1. Requirements

**To build locally (Windows only):**

- Windows 10 or 11, 64-bit
- Python 3.8 or later, installed with the **tcl/tk and IDLE** option ticked
  (Tkinter is required and PyInstaller must be able to find it)
- Roughly 500 MB of free disk space for the build environment

**To run the finished executable:** Windows 10 or 11, 64-bit. Nothing else.
No Python, no pip, no dependencies.

**On cross-compilation.** PyInstaller bundles the Python interpreter and
native libraries of the environment it runs in, so it cannot target Windows
from a native Linux or macOS Python. A Windows `.exe` can, however, be produced
on Linux by running a *Windows* Python and PyInstaller under Wine, which is how
the executable accompanying this project was first built and tested. That
approach is a convenience, not a substitute for the real thing: Wine is not
Windows, and a build intended for distribution should come from the GitHub
Actions workflow in Section 6, which runs on a genuine Windows runner.

---

## 2. Local build

Open a command prompt in the project folder and run:

```
build_exe.bat
```

The script performs seven steps and stops with a clear message if any fails:

1. Locates Python and prints its version
2. Confirms Tkinter is importable
3. Creates the `.venv-build` virtual environment
4. Installs `requirements.txt` and PyInstaller into it
5. Runs the test suite — **the build stops if any test fails**
6. Removes `build/` and `dist/`, then runs PyInstaller
7. Confirms the executable exists and runs its self test

To build manually instead:

```
pip install pyinstaller
pyinstaller --clean --noconfirm ElGamal-Encryption.spec
```

---

## 3. Output

```
dist\ElGamal-Encryption.exe
```

A single file, approximately 12 MB, containing the application, the Python
interpreter and the Tkinter runtime. It can be copied anywhere and run from any
folder; it does not read anything from the project directory.

### What the spec file does

`ElGamal-Encryption.spec` configures a one-file, windowed build. Three
decisions are worth knowing:

- `console=False` — no command window appears behind the interface. The side
  effect is that `--selftest` output is not visible when the program is started
  by double-clicking; run it from a command prompt to see the report.
- `datas=[]` — the application bundles no data files, because it loads no
  icons, images, templates or configuration at runtime. Every file it touches
  is a path the user picks in a dialog, so no resource-path helper is needed.
- `excludes=[...]` — `matplotlib`, `numpy` and `pytest` are development
  dependencies used only by `benchmark.py` and the test suite. Excluding them
  keeps the executable small.

---

## 4. Testing the executable

### Automatic

```
dist\ElGamal-Encryption.exe --selftest
```

It also writes `elgamal_selftest.log` beside the executable. Because the
application is built windowed, it has no console attached when double-clicked,
and redirecting its output (`> out.txt`) can fail to initialise Python's
standard streams. The log file is therefore the reliable way to read the
result, and is what the CI workflow inspects.

This generates a 512-bit key pair and checks eight things: that
`y = g^x mod p` holds, that a short message, a long multi-block message and a
UTF-8 message each survive a round trip, that encrypting the same plaintext
twice gives different ciphertexts and that both still decrypt, that empty
plaintext is rejected, and that malformed ciphertext is rejected. It prints
`SELFTEST PASS` and exits 0, or `SELFTEST FAIL` and exits 1.

### Manual

Double-click the executable and work through this sequence:

| Step | Action | Expected |
|---|---|---|
| 1 | The window opens | Three panels; status reads "Ready" |
| 2 | Press **Encrypt** before generating keys | Error: generate a key pair first |
| 3 | Select 512 bits, press **Generate Key Pair** | Key values appear; block size 62 bytes |
| 4 | Type `Hello, ElGamal!`, press **Encrypt** | Ciphertext appears as `c1:c2` hex |
| 5 | Press **Encrypt** again | A completely different ciphertext |
| 6 | Press **Copy to Decryption Pane**, then **Decrypt** | `Hello, ElGamal!` recovered exactly |
| 7 | Paste a long paragraph and repeat | Several ciphertext lines; recovered exactly |
| 8 | Delete a `:` from a ciphertext line, press **Decrypt** | Error naming the line |
| 9 | Press **Clear / Reset** | All fields cleared |
| 10 | Close the window | Application exits; no orphan process |

Confirm as you go that **no console window** appears alongside the interface.

---

## 5. Windows SmartScreen

The executable is not code-signed, so on first run Windows may show
"Windows protected your PC". This is expected for any unsigned executable and
does not indicate a problem with the file. Choose **More info → Run anyway**.
Mention this to anyone you send the file to, so the warning does not look like
a malware alert.

Code signing requires a certificate from a commercial authority and is out of
scope for coursework.

---

## 6. Building through GitHub Actions

`.github/workflows/build-windows-exe.yml` builds the executable on a Windows
runner. It triggers on a push to `main`, on a pull request, on a tag beginning
with `v`, and manually from the Actions tab.

The workflow checks out the repository, installs Python 3.12 and the
dependencies, runs the full test suite, builds with the same spec file used
locally, checks that the executable exists and is a plausible size, runs the
self test and requires it to report PASS, and uploads the executable as an
artifact.

To download a build that was not made from a tag: open the **Actions** tab,
click the most recent successful run, and download `ElGamal-Encryption-exe`
from the Artifacts section. Artifacts are ZIP files and expire after 90 days,
which is why a Release is the better way to share the file.

---

## 7. Publishing a GitHub Release

Pushing a tag beginning with `v` makes the workflow create a Release and attach
the executable to it:

```
git tag v1.0.0
git push origin v1.0.0
```

Then watch the Actions tab until the run finishes, and check the Releases page.
The asset URL follows this pattern:

```
https://github.com/<owner>/<repo>/releases/download/v1.0.0/ElGamal-Encryption.exe
```

Open that URL yourself before sending it to anyone. A link that has not been
clicked is a link that has not been tested.

If the release step fails with a permissions error, go to
**Settings → Actions → General → Workflow permissions** and select
**Read and write permissions**.

---

## 8. Instructions for the marker

Suggested wording:

> The application is available as a Windows executable that requires no
> installation:
>
> `<paste the verified release URL>`
>
> Download `ElGamal-Encryption.exe` and double-click it. Windows may warn that
> the publisher is unknown, because the file is not code-signed; choose
> "More info" then "Run anyway".
>
> To confirm the cryptography works before using the interface, run
> `ElGamal-Encryption.exe --selftest` from a command prompt. It performs key
> generation and encryption/decryption round trips and reports PASS or FAIL.
>
> Source code, tests, diagrams and the full report are in the repository.

---

## 9. Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError` when the EXE starts | A module was missed by the analysis. Add it to `hiddenimports` in the spec and rebuild |
| `Failed to execute script 'main'` | Build the executable with `console=True` temporarily to see the traceback, fix the cause, then set it back to `False` |
| A console window appears behind the GUI | `console=True` is set in the spec. It must be `False` |
| Tkinter error at start-up | Python was installed without tcl/tk. Reinstall Python with "tcl/tk and IDLE" ticked and rebuild |
| Antivirus quarantines the EXE | A common false positive for PyInstaller one-file builds. Leaving UPX disabled (as the spec does) reduces it. Add an exclusion, or distribute the source instead |
| The EXE is very large | Check that the `excludes` list in the spec is intact; if `matplotlib` or `numpy` slip in, the file grows substantially |
| `Fatal Python error: init_sys_streams` | The windowed EXE was run with its output redirected. Run it without redirection and read `elgamal_selftest.log` instead |
| Slow start-up | Normal for a one-file build: it unpacks to a temporary folder on each launch. A one-folder build starts faster but is not a single file |
| Build fails at the test step | This is intentional. Fix the failing tests before packaging |
| The release step fails with 403 | Workflow permissions are read-only; see Section 7 |
