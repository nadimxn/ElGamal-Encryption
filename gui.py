"""
gui.py
======

Tkinter graphical user interface for the ElGamal encryption application.

The GUI is a presentation layer only. It performs input validation and
formatting, then delegates every cryptographic operation to ``elgamal.py``
and ``crypto_utils.py``. Keeping the mathematics out of the interface code is
what allows the same core to be exercised directly by the unit tests and by
the benchmark script.

Key generation for larger moduli can take several seconds, so it runs on a
worker thread; the interface stays responsive and the result is handed back
to the main thread through a queue, because Tkinter widgets must only be
touched from the thread that created them.
"""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from crypto_utils import (
    CiphertextFormatError,
    EncodingError,
    block_size,
    decrypt_text,
    encrypt_text,
)
from elgamal import ElGamalError, SUPPORTED_KEY_SIZES
from key_manager import KeyManager, KeyManagerError

APP_TITLE = "ElGamal Encryption Implementation"
SUBTITLE = "CCS2243 Cryptography Essential - Educational Prototype"

FONT_HEADING = ("Segoe UI", 13, "bold")
FONT_LABEL = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 9)


def shorten(value: int, head: int = 28, tail: int = 12) -> str:
    """Return a shortened decimal rendering of a very large integer.

    Full values are always available through the 'Show full key values'
    dialog; the main panel shows an abbreviated form so that the layout stays
    readable in report screenshots.
    """
    text = str(value)
    if len(text) <= head + tail + 5:
        return text
    return f"{text[:head]}...{text[-tail:]}  ({len(text)} digits)"


class ElGamalApp(ttk.Frame):
    """Main application window."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
        self.master = master
        self.keys = KeyManager()
        self._result_queue: "queue.Queue[tuple]" = queue.Queue()

        master.title(APP_TITLE)
        master.geometry("860x760")
        master.minsize(760, 680)

        self.key_size_var = tk.StringVar(value="512")
        self.status_var = tk.StringVar(value="Ready. Generate a key pair to begin.")
        self.p_var = tk.StringVar(value="-")
        self.g_var = tk.StringVar(value="-")
        self.x_var = tk.StringVar(value="-")
        self.y_var = tk.StringVar(value="-")
        self.block_var = tk.StringVar(value="-")

        self.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self._build_header()
        self._build_key_section()
        self._build_encrypt_section()
        self._build_decrypt_section()
        self._build_footer()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ttk.Label(header, text=APP_TITLE, font=FONT_HEADING).pack(anchor="w")
        ttk.Label(header, text=SUBTITLE, font=FONT_LABEL,
                  foreground="#555555").pack(anchor="w")
        ttk.Separator(self, orient="horizontal").grid(row=1, column=0,
                                                      sticky="ew", pady=4)

    def _build_key_section(self) -> None:
        frame = ttk.LabelFrame(self, text=" 1. Key Generation ", padding=10)
        frame.grid(row=2, column=0, sticky="ew", pady=6)
        frame.columnconfigure(1, weight=1)

        controls = ttk.Frame(frame)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        ttk.Label(controls, text="Key size (bits):",
                  font=FONT_LABEL).pack(side="left")
        self.size_box = ttk.Combobox(
            controls, textvariable=self.key_size_var, width=8, state="readonly",
            values=[str(s) for s in SUPPORTED_KEY_SIZES],
        )
        self.size_box.pack(side="left", padx=(6, 12))

        self.generate_btn = ttk.Button(controls, text="Generate Key Pair",
                                       command=self.on_generate_keys)
        self.generate_btn.pack(side="left")
        ttk.Button(controls, text="Show Full Key Values",
                   command=self.on_show_keys).pack(side="left", padx=6)
        ttk.Button(controls, text="Export Keys...",
                   command=self.on_export_keys).pack(side="left")
        ttk.Button(controls, text="Import Keys...",
                   command=self.on_import_keys).pack(side="left", padx=6)

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.grid(row=1, column=0, columnspan=2, sticky="ew",
                           pady=(0, 8))

        rows = [
            ("Prime p:", self.p_var),
            ("Generator g:", self.g_var),
            ("Private key x:", self.x_var),
            ("Public value y = g^x mod p:", self.y_var),
            ("Plaintext bytes per block:", self.block_var),
        ]
        for index, (label, var) in enumerate(rows, start=2):
            ttk.Label(frame, text=label, font=FONT_LABEL).grid(
                row=index, column=0, sticky="w", pady=2)
            ttk.Label(frame, textvariable=var, font=FONT_MONO,
                      foreground="#1a3d6d").grid(row=index, column=1,
                                                 sticky="w", padx=8, pady=2)

    def _build_encrypt_section(self) -> None:
        frame = ttk.LabelFrame(self, text=" 2. Encryption ", padding=10)
        frame.grid(row=3, column=0, sticky="nsew", pady=6)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Plaintext:", font=FONT_LABEL).grid(
            row=0, column=0, sticky="w")
        self.plaintext_box = tk.Text(frame, height=4, font=FONT_MONO,
                                     wrap="word")
        self.plaintext_box.grid(row=1, column=0, sticky="ew", pady=(2, 6))

        ttk.Button(frame, text="Encrypt", command=self.on_encrypt).grid(
            row=2, column=0, sticky="w")

        ttk.Label(frame, text="Ciphertext (c1:c2 in hexadecimal, one block "
                              "per line):", font=FONT_LABEL).grid(
            row=3, column=0, sticky="w", pady=(8, 0))
        self.ciphertext_out = tk.Text(frame, height=5, font=FONT_MONO,
                                      wrap="char")
        self.ciphertext_out.grid(row=4, column=0, sticky="ew", pady=2)

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, sticky="w", pady=(4, 0))
        ttk.Button(buttons, text="Copy to Decryption Pane",
                   command=self.on_copy_ciphertext).pack(side="left")

    def _build_decrypt_section(self) -> None:
        frame = ttk.LabelFrame(self, text=" 3. Decryption ", padding=10)
        frame.grid(row=4, column=0, sticky="nsew", pady=6)
        frame.columnconfigure(0, weight=1)

        ttk.Label(frame, text="Ciphertext to decrypt:",
                  font=FONT_LABEL).grid(row=0, column=0, sticky="w")
        self.ciphertext_in = tk.Text(frame, height=5, font=FONT_MONO,
                                     wrap="char")
        self.ciphertext_in.grid(row=1, column=0, sticky="ew", pady=(2, 6))

        ttk.Button(frame, text="Decrypt", command=self.on_decrypt).grid(
            row=2, column=0, sticky="w")

        ttk.Label(frame, text="Recovered plaintext:", font=FONT_LABEL).grid(
            row=3, column=0, sticky="w", pady=(8, 0))
        self.plaintext_out = tk.Text(frame, height=4, font=FONT_MONO,
                                     wrap="word")
        self.plaintext_out.grid(row=4, column=0, sticky="ew", pady=2)

    def _build_footer(self) -> None:
        footer = ttk.Frame(self)
        footer.grid(row=5, column=0, sticky="ew", pady=(8, 0))
        footer.columnconfigure(1, weight=1)
        ttk.Button(footer, text="Clear / Reset",
                   command=self.on_reset).grid(row=0, column=0, sticky="w")
        ttk.Label(footer, textvariable=self.status_var, font=FONT_LABEL,
                  foreground="#1a5d2f", anchor="w").grid(
            row=0, column=1, sticky="ew", padx=10)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(message)
        for child in self.grid_slaves(row=5, column=0):
            for label in child.grid_slaves(row=0, column=1):
                label.configure(foreground="#a11414" if error else "#1a5d2f")

    def show_error(self, title: str, message: str) -> None:
        self.set_status(f"{title}: {message}", error=True)
        messagebox.showerror(title, message)

    @staticmethod
    def _read_text(widget: tk.Text) -> str:
        return widget.get("1.0", "end-1c")

    @staticmethod
    def _write_text(widget: tk.Text, value: str) -> None:
        widget.delete("1.0", "end")
        widget.insert("1.0", value)

    # ------------------------------------------------------------------
    # Key generation
    # ------------------------------------------------------------------

    def on_generate_keys(self) -> None:
        try:
            bits = int(self.key_size_var.get())
        except ValueError:
            self.show_error("Invalid key size",
                            "Select a key size from the list.")
            return

        self.generate_btn.state(["disabled"])
        self.progress.start(12)
        self.set_status(f"Generating a {bits}-bit safe prime. Please wait...")

        worker = threading.Thread(target=self._generate_worker, args=(bits,),
                                  daemon=True)
        worker.start()
        self.after(120, self._poll_generation)

    def _generate_worker(self, bits: int) -> None:
        try:
            self.keys.generate(bits)
            self._result_queue.put(("ok", bits))
        except Exception as exc:                  # surfaced on the UI thread
            self._result_queue.put(("error", str(exc)))

    def _poll_generation(self) -> None:
        try:
            outcome, payload = self._result_queue.get_nowait()
        except queue.Empty:
            self.after(120, self._poll_generation)
            return

        self.progress.stop()
        self.generate_btn.state(["!disabled"])

        if outcome == "error":
            self.show_error("Key generation failed", str(payload))
            return

        public = self.keys.public_key
        private = self.keys.private_key
        self.p_var.set(shorten(public.p))
        self.g_var.set(shorten(public.g))
        self.x_var.set(shorten(private.x))
        self.y_var.set(shorten(public.y))
        self.block_var.set(f"{block_size(public.p)} bytes "
                           f"(modulus is {public.bit_length} bits)")
        self.set_status(f"Key pair generated successfully ({payload} bits).")

    def on_show_keys(self) -> None:
        if not self.keys.has_keys:
            self.show_error("No keys", "Generate a key pair first.")
            return
        public, private = self.keys.public_key, self.keys.private_key
        window = tk.Toplevel(self)
        window.title("Full Key Values")
        window.geometry("720x420")
        box = tk.Text(window, font=FONT_MONO, wrap="char")
        box.pack(fill="both", expand=True, padx=8, pady=8)
        box.insert("1.0",
                   "PUBLIC KEY (p, g, y) - may be shared\n\n"
                   f"p = {public.p}\n\ng = {public.g}\n\ny = {public.y}\n\n"
                   "-------------------------------------------------\n\n"
                   "PRIVATE KEY x - must be kept secret\n\n"
                   f"x = {private.x}\n")
        box.configure(state="disabled")

    def on_export_keys(self) -> None:
        if not self.keys.has_keys:
            self.show_error("No keys", "Generate a key pair first.")
            return
        if not messagebox.askokcancel(
                "Export keys",
                "The private key will be written as an UNENCRYPTED JSON "
                "file.\nThis is acceptable for coursework demonstration only."):
            return
        directory = filedialog.askdirectory(title="Choose an export folder")
        if not directory:
            return
        try:
            self.keys.export_public(f"{directory}/public_key.json")
            self.keys.export_private(f"{directory}/private_key.json")
        except KeyManagerError as exc:
            self.show_error("Export failed", str(exc))
            return
        self.set_status(f"Keys exported to {directory}.")

    def on_import_keys(self) -> None:
        public_path = filedialog.askopenfilename(
            title="Select public_key.json", filetypes=[("JSON", "*.json")])
        if not public_path:
            return
        private_path = filedialog.askopenfilename(
            title="Select private_key.json", filetypes=[("JSON", "*.json")])
        if not private_path:
            return
        try:
            self.keys.load_pair(public_path, private_path)
        except KeyManagerError as exc:
            self.show_error("Import failed", str(exc))
            return
        public, private = self.keys.public_key, self.keys.private_key
        self.p_var.set(shorten(public.p))
        self.g_var.set(shorten(public.g))
        self.x_var.set(shorten(private.x))
        self.y_var.set(shorten(public.y))
        self.block_var.set(f"{block_size(public.p)} bytes "
                           f"(modulus is {public.bit_length} bits)")
        self.set_status("Key pair imported and verified (g^x mod p == y).")

    # ------------------------------------------------------------------
    # Encryption / decryption
    # ------------------------------------------------------------------

    def on_encrypt(self) -> None:
        if not self.keys.has_keys:
            self.show_error("No keys",
                            "Generate or import a key pair before encrypting.")
            return
        plaintext = self._read_text(self.plaintext_box)
        if plaintext.strip() == "":
            self.show_error("Empty plaintext",
                            "Type a message before pressing Encrypt.")
            return
        try:
            ciphertext = encrypt_text(plaintext, self.keys.public_key)
        except (EncodingError, ElGamalError) as exc:
            self.show_error("Encryption failed", str(exc))
            return

        self._write_text(self.ciphertext_out, ciphertext)
        blocks = len(ciphertext.splitlines())
        self.set_status(
            f"Encrypted {len(plaintext.encode('utf-8'))} plaintext bytes into "
            f"{blocks} ciphertext block(s). Encrypt again to see a different "
            "ciphertext for the same message.")

    def on_copy_ciphertext(self) -> None:
        ciphertext = self._read_text(self.ciphertext_out)
        if ciphertext.strip() == "":
            self.show_error("Nothing to copy", "Encrypt a message first.")
            return
        self._write_text(self.ciphertext_in, ciphertext)
        self.set_status("Ciphertext copied into the decryption pane.")

    def on_decrypt(self) -> None:
        if not self.keys.has_keys:
            self.show_error("No keys",
                            "Generate or import a key pair before decrypting.")
            return
        ciphertext = self._read_text(self.ciphertext_in)
        if ciphertext.strip() == "":
            self.show_error("Empty ciphertext",
                            "Paste a ciphertext before pressing Decrypt.")
            return
        try:
            plaintext = decrypt_text(ciphertext, self.keys.private_key)
        except (CiphertextFormatError, EncodingError, ElGamalError) as exc:
            self._write_text(self.plaintext_out, "")
            self.show_error("Decryption failed", str(exc))
            return

        self._write_text(self.plaintext_out, plaintext)
        self.set_status(
            f"Decryption successful: recovered "
            f"{len(plaintext.encode('utf-8'))} bytes of plaintext.")

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def on_reset(self) -> None:
        self._write_text(self.plaintext_box, "")
        self._write_text(self.ciphertext_out, "")
        self._write_text(self.ciphertext_in, "")
        self._write_text(self.plaintext_out, "")
        self.keys.clear()
        for var in (self.p_var, self.g_var, self.x_var, self.y_var,
                    self.block_var):
            var.set("-")
        self.set_status("Application reset. Generate a key pair to begin.")


def launch() -> None:
    """Create the Tk root window and start the event loop."""
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:                            # pragma: no cover
        pass
    ElGamalApp(root)
    root.mainloop()
