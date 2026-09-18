# -*- mode: python ; coding: utf-8 -*-
"""
ElGamal-Encryption.spec
=======================

PyInstaller build configuration for the ElGamal Encryption Implementation.

Build with:

    pyinstaller --clean --noconfirm ElGamal-Encryption.spec

Output:

    dist/ElGamal-Encryption.exe        (on Windows)
    dist/ElGamal-Encryption            (on Linux/macOS)

Design notes
------------
* **One file.** `onefile` is used because the application has no external data
  files to sit beside it, so a single executable is the simplest thing for a
  marker to download and run.

* **No console.** `console=False` so that launching the GUI does not open a
  command window behind it. Note the consequence: `--selftest` still works, but
  its output is not visible when the program is started by double-clicking. Run
  it from a terminal (`ElGamal-Encryption.exe --selftest`) to see the report.
  On Windows a windowed build writes nothing to an inherited console either, so
  CI redirects the output to a file (see the workflow).

* **No bundled data.** The application loads no icons, images, templates or
  configuration files at runtime. Every file it touches is a path the user
  chooses in a file dialog. There is therefore nothing to add to `datas`, and
  no runtime resource-path helper is required.

* **Explicit hidden imports.** `main.py` imports `gui` inside a function so
  that a missing Tkinter can be reported cleanly rather than crashing at
  start-up. PyInstaller's static analysis does follow that import, but the
  project modules are listed explicitly so the build does not depend on that
  behaviour.

* **Excludes.** `matplotlib`, `numpy`, `pytest` and the test modules are
  development-only dependencies used by `benchmark.py` and `tests/`. They are
  excluded so the executable stays small; the packaged application never
  imports them.
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'gui',
        'elgamal',
        'crypto_utils',
        'key_manager',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'secrets',
        'queue',
        'threading',
        'json',
        'dataclasses',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pytest',
        'tests',
        'benchmark',
        'PIL',
        'pandas',
        'scipy',
        'IPython',
        'setuptools',
        'pip',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ElGamal-Encryption',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,                 # UPX compression is skipped: it slows start-up
                               # and is a common false-positive trigger for
                               # antivirus software.
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,             # windowed application: no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=None,              # no Windows version resource; add one here if
                               # a signed/branded build is ever required
)
