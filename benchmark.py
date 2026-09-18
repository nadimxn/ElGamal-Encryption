"""
benchmark.py
============

Reproducible performance measurement for the ElGamal implementation.

Measures three things:

  1. Key generation time as a function of modulus size. Because safe-prime
     search is a random search, this varies a great deal between runs; the
     script therefore reports the median as well as the mean and the spread.
  2. Encryption and decryption time as a function of modulus size for a fixed
     message.
  3. Encryption and decryption time, ciphertext size and expansion ratio as a
     function of plaintext length for a fixed modulus size.

Usage
-----
    python benchmark.py                      # default settings
    python benchmark.py --key-trials 5 --op-trials 30
    python benchmark.py --sizes 256 512 1024 --no-plot

Output
------
    results/benchmark_keygen.csv
    results/benchmark_operations.csv
    results/benchmark_message_sizes.csv
    results/benchmark_plot.png        (only if matplotlib is installed)
    results/benchmark_environment.txt

Timing uses ``time.perf_counter``, the highest-resolution monotonic clock
available in Python. All figures depend on the machine, the Python build and
the system load at the time of the run, so the CSV files must be regenerated
on the machine used for the report rather than copied from elsewhere.
"""

from __future__ import annotations

import argparse
import csv
import os
import platform
import statistics
import sys
import time
from typing import Dict, List

from crypto_utils import block_size, decrypt_text, encrypt_text
from elgamal import decrypt_int, encrypt_int, generate_keypair

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

DEFAULT_SIZES = (256, 512, 1024)
DEFAULT_MESSAGE = "CCS2243 Cryptography Essential - ElGamal benchmark message."
DEFAULT_MESSAGE_LENGTHS = (16, 64, 256, 1024, 4096)


def ensure_results_dir() -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)


def write_csv(filename: str, fieldnames: List[str],
              rows: List[Dict]) -> str:
    path = os.path.join(RESULTS_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ---------------------------------------------------------------------------
# Benchmark 1: key generation
# ---------------------------------------------------------------------------

def benchmark_keygen(sizes, trials: int) -> List[Dict]:
    rows = []
    for bits in sizes:
        samples = []
        for _ in range(trials):
            start = time.perf_counter()
            generate_keypair(bits)
            samples.append((time.perf_counter() - start) * 1000.0)
        rows.append({
            "key_bits": bits,
            "trials": trials,
            "mean_ms": round(statistics.mean(samples), 3),
            "median_ms": round(statistics.median(samples), 3),
            "min_ms": round(min(samples), 3),
            "max_ms": round(max(samples), 3),
            "stdev_ms": round(statistics.stdev(samples), 3)
            if trials > 1 else 0.0,
        })
        print(f"  key generation {bits:>5} bits: "
              f"median {rows[-1]['median_ms']:>10.2f} ms  "
              f"(min {rows[-1]['min_ms']:.1f}, max {rows[-1]['max_ms']:.1f})")
    return rows


# ---------------------------------------------------------------------------
# Benchmark 2: encryption / decryption against key size
# ---------------------------------------------------------------------------

def benchmark_operations(sizes, trials: int, message: str) -> List[Dict]:
    rows = []
    for bits in sizes:
        keypair = generate_keypair(bits)
        pub, priv = keypair.public, keypair.private

        # Single-block integer operations isolate the modular exponentiation
        # cost from the encoding cost.
        m = 123456789
        enc_samples, dec_samples = [], []
        for _ in range(trials):
            start = time.perf_counter()
            c1, c2 = encrypt_int(m, pub)
            enc_samples.append((time.perf_counter() - start) * 1000.0)
            start = time.perf_counter()
            decrypt_int(c1, c2, priv)
            dec_samples.append((time.perf_counter() - start) * 1000.0)

        # Full text pipeline, including UTF-8 encoding and hex serialisation.
        text_enc, text_dec = [], []
        ciphertext = ""
        for _ in range(trials):
            start = time.perf_counter()
            ciphertext = encrypt_text(message, pub)
            text_enc.append((time.perf_counter() - start) * 1000.0)
            start = time.perf_counter()
            recovered = decrypt_text(ciphertext, priv)
            text_dec.append((time.perf_counter() - start) * 1000.0)
            assert recovered == message, "round trip failed during benchmark"

        rows.append({
            "key_bits": bits,
            "trials": trials,
            "block_bytes": block_size(pub.p),
            "blocks_used": len(ciphertext.splitlines()),
            "encrypt_int_mean_ms": round(statistics.mean(enc_samples), 4),
            "decrypt_int_mean_ms": round(statistics.mean(dec_samples), 4),
            "encrypt_text_mean_ms": round(statistics.mean(text_enc), 4),
            "decrypt_text_mean_ms": round(statistics.mean(text_dec), 4),
            "plaintext_bytes": len(message.encode("utf-8")),
            "ciphertext_bytes": len(ciphertext.encode("utf-8")),
            "expansion_ratio": round(
                len(ciphertext.encode("utf-8"))
                / len(message.encode("utf-8")), 3),
        })
        print(f"  {bits:>5} bits: encrypt {rows[-1]['encrypt_int_mean_ms']:.3f} ms, "
              f"decrypt {rows[-1]['decrypt_int_mean_ms']:.3f} ms per block")
    return rows


# ---------------------------------------------------------------------------
# Benchmark 3: message size scaling at a fixed key size
# ---------------------------------------------------------------------------

def benchmark_message_sizes(bits: int, lengths, trials: int) -> List[Dict]:
    keypair = generate_keypair(bits)
    pub, priv = keypair.public, keypair.private
    rows = []
    for length in lengths:
        message = "A" * length
        enc, dec = [], []
        ciphertext = ""
        for _ in range(trials):
            start = time.perf_counter()
            ciphertext = encrypt_text(message, pub)
            enc.append((time.perf_counter() - start) * 1000.0)
            start = time.perf_counter()
            recovered = decrypt_text(ciphertext, priv)
            dec.append((time.perf_counter() - start) * 1000.0)
            assert recovered == message, "round trip failed during benchmark"
        rows.append({
            "key_bits": bits,
            "plaintext_bytes": length,
            "blocks": len(ciphertext.splitlines()),
            "ciphertext_bytes": len(ciphertext.encode("utf-8")),
            "expansion_ratio": round(
                len(ciphertext.encode("utf-8")) / length, 3),
            "encrypt_mean_ms": round(statistics.mean(enc), 4),
            "decrypt_mean_ms": round(statistics.mean(dec), 4),
        })
        print(f"  {length:>6} bytes -> {rows[-1]['blocks']:>4} blocks, "
              f"encrypt {rows[-1]['encrypt_mean_ms']:.2f} ms, "
              f"decrypt {rows[-1]['decrypt_mean_ms']:.2f} ms")
    return rows


# ---------------------------------------------------------------------------
# Plotting (optional)
# ---------------------------------------------------------------------------

def make_plot(keygen_rows, op_rows, size_rows) -> str:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib is not installed; skipping the graph.")
        return ""

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

    axes[0].bar([str(r["key_bits"]) for r in keygen_rows],
                [r["median_ms"] for r in keygen_rows], color="#3b6ea5")
    axes[0].set_title("Median key generation time")
    axes[0].set_xlabel("Key size (bits)")
    axes[0].set_ylabel("Time (ms)")
    axes[0].set_yscale("log")

    bits = [r["key_bits"] for r in op_rows]
    axes[1].plot(bits, [r["encrypt_int_mean_ms"] for r in op_rows],
                 marker="o", label="Encrypt (one block)")
    axes[1].plot(bits, [r["decrypt_int_mean_ms"] for r in op_rows],
                 marker="s", label="Decrypt (one block)")
    axes[1].set_title("Per-block operation time")
    axes[1].set_xlabel("Key size (bits)")
    axes[1].set_ylabel("Time (ms)")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    lengths = [r["plaintext_bytes"] for r in size_rows]
    axes[2].plot(lengths, [r["encrypt_mean_ms"] for r in size_rows],
                 marker="o", label="Encrypt")
    axes[2].plot(lengths, [r["decrypt_mean_ms"] for r in size_rows],
                 marker="s", label="Decrypt")
    axes[2].set_title(f"Message size scaling ({size_rows[0]['key_bits']}-bit key)")
    axes[2].set_xlabel("Plaintext size (bytes)")
    axes[2].set_ylabel("Time (ms)")
    axes[2].legend()
    axes[2].grid(alpha=0.3)

    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, "benchmark_plot.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


# ---------------------------------------------------------------------------
# Environment record
# ---------------------------------------------------------------------------

def write_environment(path_note: str) -> str:
    path = os.path.join(RESULTS_DIR, "benchmark_environment.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("ElGamal benchmark environment\n")
        handle.write("=============================\n")
        handle.write(f"Timestamp (local) : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        handle.write(f"Python            : {sys.version.splitlines()[0]}\n")
        handle.write(f"Implementation    : {platform.python_implementation()}\n")
        handle.write(f"Operating system  : {platform.platform()}\n")
        handle.write(f"Processor         : {platform.processor() or 'unknown'}\n")
        handle.write(f"Machine           : {platform.machine()}\n")
        handle.write(f"Notes             : {path_note}\n")
    return path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark the ElGamal implementation.")
    parser.add_argument("--sizes", type=int, nargs="+", default=list(DEFAULT_SIZES),
                        help="Key sizes in bits to measure.")
    parser.add_argument("--key-trials", type=int, default=5,
                        help="Key generations per size (default 5).")
    parser.add_argument("--op-trials", type=int, default=50,
                        help="Encrypt/decrypt repetitions (default 50).")
    parser.add_argument("--message-key-bits", type=int, default=512,
                        help="Key size used for the message-scaling test.")
    parser.add_argument("--message-lengths", type=int, nargs="+",
                        default=list(DEFAULT_MESSAGE_LENGTHS))
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip graph generation.")
    parser.add_argument("--note", default="",
                        help="Free-text note recorded with the environment.")
    args = parser.parse_args()

    ensure_results_dir()

    print("1. Key generation")
    keygen_rows = benchmark_keygen(args.sizes, args.key_trials)
    write_csv("benchmark_keygen.csv",
              ["key_bits", "trials", "mean_ms", "median_ms", "min_ms",
               "max_ms", "stdev_ms"], keygen_rows)

    print("2. Encryption and decryption against key size")
    op_rows = benchmark_operations(args.sizes, args.op_trials, DEFAULT_MESSAGE)
    write_csv("benchmark_operations.csv",
              ["key_bits", "trials", "block_bytes", "blocks_used",
               "encrypt_int_mean_ms", "decrypt_int_mean_ms",
               "encrypt_text_mean_ms", "decrypt_text_mean_ms",
               "plaintext_bytes", "ciphertext_bytes", "expansion_ratio"],
              op_rows)

    print("3. Message size scaling")
    size_rows = benchmark_message_sizes(args.message_key_bits,
                                        args.message_lengths,
                                        max(5, args.op_trials // 10))
    write_csv("benchmark_message_sizes.csv",
              ["key_bits", "plaintext_bytes", "blocks", "ciphertext_bytes",
               "expansion_ratio", "encrypt_mean_ms", "decrypt_mean_ms"],
              size_rows)

    if not args.no_plot:
        plot_path = make_plot(keygen_rows, op_rows, size_rows)
        if plot_path:
            print(f"\nGraph written to {plot_path}")

    env_path = write_environment(args.note or "No note supplied.")
    print(f"Environment recorded in {env_path}")
    print(f"CSV results written to {RESULTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
