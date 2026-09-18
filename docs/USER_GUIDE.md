# User Guide

ElGamal Encryption Implementation — CCS2243 Cryptography Essential

## 1. Requirements

- Python 3.8 or later
- Tkinter (bundled with the official Python installer on Windows and macOS; on
  Debian/Ubuntu install it with `sudo apt install python3-tk`)
- No third-party packages are needed to run the application

To check your installation:

```bash
python --version
python -c "import tkinter; print('Tkinter OK')"
```

## 2. Opening the project

```bash
cd ElGamal-Encryption
```

Optional, for the test suite and the benchmark graph only:

```bash
pip install -r requirements.txt
```

## 3. Starting the application

```bash
python main.py
```

The window opens with the status bar showing *Ready. Generate a key pair to begin.*

## 4. Generating keys

1. Choose a key size from the dropdown. **512 is recommended for a live
   demonstration**: 256 is faster but too small to be taken seriously, and 1024
   can take 10–30 seconds while 2048 can take several minutes.
2. Press **Generate Key Pair**. The progress bar animates while the safe-prime
   search runs; the interface stays responsive.
3. When it completes, the panel shows abbreviated values of `p`, `g`, `x` and
   `y`, plus the number of plaintext bytes that fit in one block.
4. Press **Show Full Key Values** to open a window with the complete numbers.
   This is the view to screenshot when you need to show the actual key material.

Keys exist only in memory. Pressing Reset or closing the application discards
them.

## 5. Entering plaintext

Click in the **Plaintext** box in section 2 and type or paste any text. Any
length works — long messages are split into blocks automatically. Unicode,
punctuation, digits and emoji are all supported.

## 6. Encrypting

Press **Encrypt**. The ciphertext appears as one line per block, each line in
the form `c1:c2` with both values in hexadecimal. The status bar reports how
many plaintext bytes were encrypted into how many blocks.

Press **Encrypt** again without changing anything. The ciphertext changes
completely. This is the probabilistic behaviour of ElGamal and is worth
demonstrating explicitly during your presentation.

## 7. Viewing and transferring the ciphertext

Press **Copy to Decryption Pane** to move the ciphertext into section 3. You
can also select the text and copy it manually, or paste in a ciphertext
produced earlier.

## 8. Decrypting

Press **Decrypt**. The recovered plaintext appears in the bottom box and the
status bar reports the number of bytes recovered.

## 9. Resetting

Press **Clear / Reset** to empty all four text areas and discard the key pair.
The key fields return to `-`.

## 10. Exporting and importing keys (optional)

**Export Keys...** asks for confirmation, then writes `public_key.json` and
`private_key.json` to a folder you choose.

> The private key file is **not encrypted**. Anyone who reads it can decrypt
> every message encrypted under the matching public key. This is acceptable for
> coursework only.

**Import Keys...** asks for the public file and then the private file. The
application verifies that `g^x mod p == y` and refuses a mismatched pair.

## 11. Understanding error messages

| Message | Cause | What to do |
|---|---|---|
| Generate or import a key pair before encrypting | No keys in memory | Press Generate Key Pair |
| Type a message before pressing Encrypt | Plaintext box empty | Enter text |
| Paste a ciphertext before pressing Decrypt | Ciphertext box empty | Paste or copy a ciphertext |
| Line *n* is malformed: expected exactly one ':' | A ciphertext line is not `c1:c2` | Check for a truncated or joined line |
| Line *n* contains a value that is not valid hexadecimal | Non-hex characters | Re-copy the ciphertext |
| Block *n* is larger than the modulus p | Ciphertext belongs to a different, larger key | Load the matching key pair |
| Block *n* does not carry the expected marker byte | Wrong private key, or corrupted ciphertext | Use the key pair that produced the ciphertext |
| Decrypted bytes are not valid UTF-8 text | Wrong private key, or corrupted ciphertext | Same |
| The private key does not correspond to the public key | Mismatched key files on import | Import the matching pair |

An error never leaves stale output on screen: the recovered-plaintext box is
cleared before the message is shown.
