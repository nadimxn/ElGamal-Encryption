"""
diagrams/make_diagrams.py
=========================

Generates the editable draw.io (diagrams.net) source files used in the
project report.

Run from the project root:

    python diagrams/make_diagrams.py

Each diagram is written as a ``.drawio`` file containing uncompressed
mxGraphModel XML, which draw.io opens and edits directly. To produce the
image files for the report: open the ``.drawio`` file at https://app.diagrams.net
(or in the draw.io desktop application) and choose File > Export as > PNG
with a transparent background and a zoom of 200 percent.

The diagrams are generated from a script rather than drawn by hand so that
every node label can be checked against the source code, and so that a change
to the implementation can be reflected in the diagrams by editing one file.
"""

from __future__ import annotations

import os
from typing import List, Optional, Tuple

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- reusable styles -------------------------------------------------------

S_PROCESS = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;"
             "strokeColor=#6c8ebf;fontSize=12;")
S_CRYPTO = ("rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;"
            "strokeColor=#82b366;fontSize=12;")
S_IO = ("shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;"
        "html=1;fixedSize=1;fillColor=#ffe6cc;strokeColor=#d79b00;fontSize=12;")
S_DECISION = ("rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;"
              "strokeColor=#d6b656;fontSize=11;")
S_TERMINAL = ("ellipse;whiteSpace=wrap;html=1;fillColor=#f5f5f5;"
              "strokeColor=#666666;fontSize=12;")
S_ACTOR = "shape=umlActor;verticalLabelPosition=bottom;html=1;verticalAlign=top;"
S_USECASE = ("ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;"
             "strokeColor=#6c8ebf;fontSize=11;")
S_STORE = ("shape=partialRectangle;top=0;bottom=0;html=1;whiteSpace=wrap;"
           "fillColor=#f8cecc;strokeColor=#b85450;fontSize=11;align=center;")
S_EXTERNAL = ("whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;"
              "fontSize=12;")
S_CLASS = ("swimlane;fontStyle=1;childLayout=stackLayout;horizontal=1;"
           "startSize=26;fillColor=#ffffff;horizontalStack=0;resizeParent=1;"
           "resizeParentMax=0;html=1;fontSize=12;")
S_CLASS_ROW = ("text;strokeColor=none;fillColor=none;align=left;"
               "verticalAlign=middle;spacingLeft=6;html=1;fontSize=11;")
S_EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=block;"
          "endFill=1;fontSize=10;")
S_EDGE_PLAIN = "endArrow=none;html=1;fontSize=10;"
S_NOTE = ("shape=note;whiteSpace=wrap;html=1;size=14;fillColor=#ffffcc;"
          "strokeColor=#d6b656;fontSize=11;align=left;")


class Diagram:
    """Minimal builder for uncompressed draw.io XML."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.cells: List[str] = []
        self.counter = 1

    def _next_id(self) -> str:
        self.counter += 1
        return f"n{self.counter}"

    def node(self, label: str, x: int, y: int, w: int, h: int,
             style: str = S_PROCESS) -> str:
        cid = self._next_id()
        safe = (label.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
        self.cells.append(
            f'<mxCell id="{cid}" value="{safe}" style="{style}" vertex="1" '
            f'parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" '
            f'height="{h}" as="geometry"/></mxCell>'
        )
        return cid

    def edge(self, source: str, target: str, label: str = "",
             style: str = S_EDGE) -> str:
        cid = self._next_id()
        safe = (label.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))
        self.cells.append(
            f'<mxCell id="{cid}" value="{safe}" style="{style}" edge="1" '
            f'parent="1" source="{source}" target="{target}">'
            f'<mxGeometry relative="1" as="geometry"/></mxCell>'
        )
        return cid

    def swimlane_class(self, title: str, rows: List[str], x: int, y: int,
                       w: int = 240) -> str:
        cid = self._next_id()
        height = 26 + 20 * len(rows)
        body = (f'<mxCell id="{cid}" value="{title}" style="{S_CLASS}" '
                f'vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" '
                f'width="{w}" height="{height}" as="geometry"/></mxCell>')
        self.cells.append(body)
        for index, row in enumerate(rows):
            rid = self._next_id()
            safe = (row.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;"))
            self.cells.append(
                f'<mxCell id="{rid}" value="{safe}" style="{S_CLASS_ROW}" '
                f'vertex="1" parent="{cid}"><mxGeometry y="{26 + 20 * index}" '
                f'width="{w}" height="20" as="geometry"/></mxCell>'
            )
        return cid

    def write(self, filename: str) -> str:
        xml = (
            '<mxfile host="app.diagrams.net" type="device">\n'
            f'  <diagram name="{self.name}" id="{self.name.replace(" ", "-")}">\n'
            '    <mxGraphModel dx="1100" dy="800" grid="1" gridSize="10" '
            'guides="1" tooltips="1" connect="1" arrows="1" fold="1" '
            'page="1" pageScale="1" pageWidth="1100" pageHeight="1700" '
            'math="0" shadow="0">\n'
            '      <root>\n'
            '        <mxCell id="0"/>\n'
            '        <mxCell id="1" parent="0"/>\n'
            + "\n".join("        " + c for c in self.cells) + "\n"
            '      </root>\n'
            '    </mxGraphModel>\n'
            '  </diagram>\n'
            '</mxfile>\n'
        )
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(xml)
        return path


# ---------------------------------------------------------------------------
# 1. System architecture
# ---------------------------------------------------------------------------

def system_architecture() -> str:
    d = Diagram("System Architecture")
    user = d.node("User", 400, 40, 200, 40, S_EXTERNAL)
    gui = d.node("Presentation Layer\ngui.py - Tkinter interface\n"
                 "(key panel, encryption pane, decryption pane, status bar)",
                 320, 120, 360, 80)
    val = d.node("Input Validation\ngui.py handlers + crypto_utils.py\n"
                 "(empty input, key present, ciphertext format)",
                 320, 230, 360, 70)
    enc_util = d.node("Message Representation\ncrypto_utils.py\n"
                      "UTF-8 encoding, block splitting (m < p),\n"
                      "hex ciphertext serialisation",
                      60, 340, 320, 90, S_CRYPTO)
    core = d.node("ElGamal Cryptographic Engine\nelgamal.py\n"
                  "safe prime + generator, key generation,\n"
                  "modular exponentiation, modular inverse,\n"
                  "encrypt_int / decrypt_int",
                  400, 340, 340, 90, S_CRYPTO)
    keys = d.node("Key Management\nkey_manager.py\n"
                  "in-memory key pair, JSON export/import,\n"
                  "key-pair consistency check",
                  760, 340, 280, 90, S_CRYPTO)
    rng = d.node("Operating System CSPRNG\nPython 'secrets' module",
                 400, 470, 340, 50, S_EXTERNAL)
    files = d.node("Key files (optional)\npublic_key.json / private_key.json\n"
                   "unencrypted - educational use only",
                   760, 470, 280, 60, S_STORE)
    out = d.node("Output to user\nciphertext, recovered plaintext,\n"
                 "status and error messages", 320, 570, 360, 60, S_IO)
    note = d.node("Note: no database, no network service and no external\n"
                  "cryptographic library are present. All ElGamal arithmetic\n"
                  "is implemented in elgamal.py using Python integers.",
                  60, 470, 320, 80, S_NOTE)

    d.edge(user, gui, "plaintext / ciphertext / commands")
    d.edge(gui, val)
    d.edge(val, enc_util, "valid input")
    d.edge(val, core)
    d.edge(val, keys, "key requests")
    d.edge(enc_util, core, "message blocks m < p")
    d.edge(core, keys, "(p, g, y), x", S_EDGE_PLAIN)
    d.edge(core, rng, "ephemeral k, x, prime search")
    d.edge(keys, files, "export / import")
    d.edge(core, out)
    d.edge(out, user)
    return d.write("system_architecture.drawio")


# ---------------------------------------------------------------------------
# 2. Use case diagram
# ---------------------------------------------------------------------------

def use_case() -> str:
    d = Diagram("Use Case Diagram")
    d.node("System boundary: ElGamal Encryption Application", 260, 40, 520, 700,
           "rounded=0;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#666666;"
           "verticalAlign=top;fontSize=12;fontStyle=1;dashed=1;")
    actor = d.node("User\n(student / demonstrator)", 80, 340, 60, 90, S_ACTOR)

    uc_gen = d.node("Generate Key Pair", 330, 100, 200, 60, S_USECASE)
    uc_view = d.node("View Key Values", 330, 180, 200, 60, S_USECASE)
    uc_store = d.node("Export / Import Keys", 330, 260, 200, 60, S_USECASE)
    uc_enter = d.node("Enter Plaintext", 330, 340, 200, 60, S_USECASE)
    uc_enc = d.node("Encrypt Message", 330, 420, 200, 60, S_USECASE)
    uc_cin = d.node("Enter Ciphertext", 330, 500, 200, 60, S_USECASE)
    uc_dec = d.node("Decrypt Message", 330, 580, 200, 60, S_USECASE)
    uc_reset = d.node("Clear / Reset", 330, 660, 200, 60, S_USECASE)

    uc_valid = d.node("Validate Input", 590, 380, 170, 55, S_USECASE)
    uc_status = d.node("Display Status\nor Error Message", 590, 470, 170, 55,
                       S_USECASE)

    for uc in (uc_gen, uc_view, uc_store, uc_enter, uc_enc, uc_cin, uc_dec,
               uc_reset):
        d.edge(actor, uc, "", S_EDGE_PLAIN)

    inc = S_EDGE + "dashed=1;"
    d.edge(uc_enc, uc_valid, "<<include>>", inc)
    d.edge(uc_dec, uc_valid, "<<include>>", inc)
    d.edge(uc_gen, uc_status, "<<include>>", inc)
    d.edge(uc_enc, uc_status, "<<include>>", inc)
    d.edge(uc_dec, uc_status, "<<include>>", inc)
    d.edge(uc_enc, uc_gen, "<<precondition>>\nkey pair exists",
           S_EDGE + "dashed=1;endArrow=open;")
    d.edge(uc_dec, uc_gen, "<<precondition>>\nkey pair exists",
           S_EDGE + "dashed=1;endArrow=open;")
    return d.write("use_case.drawio")


# ---------------------------------------------------------------------------
# 3. Data flow diagram (context + level 1)
# ---------------------------------------------------------------------------

def dfd() -> str:
    d = Diagram("Data Flow Diagram")
    d.node("Context Diagram (Level 0)", 60, 20, 300, 30,
           "text;html=1;fontStyle=1;fontSize=14;align=left;")
    ext = d.node("User", 60, 90, 140, 60, S_EXTERNAL)
    proc0 = d.node("0\nElGamal Encryption\nApplication", 340, 80, 220, 80,
                   "ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;"
                   "strokeColor=#6c8ebf;fontSize=12;")
    d.edge(ext, proc0, "plaintext, ciphertext,\nkey size, commands")
    d.edge(proc0, ext, "ciphertext, recovered plaintext,\nkey values, errors")

    d.node("Level 1 Data Flow Diagram", 60, 220, 300, 30,
           "text;html=1;fontStyle=1;fontSize=14;align=left;")
    user = d.node("User", 60, 380, 120, 60, S_EXTERNAL)
    p1 = d.node("1.0\nValidate Input", 240, 290, 170, 60)
    p2 = d.node("2.0\nGenerate Key Pair", 240, 380, 170, 60, S_CRYPTO)
    p3 = d.node("3.0\nEncode Plaintext\ninto Blocks", 240, 470, 170, 70,
                S_CRYPTO)
    p4 = d.node("4.0\nEncrypt Blocks\n(c1, c2)", 480, 470, 170, 70, S_CRYPTO)
    p5 = d.node("5.0\nDecrypt Blocks", 480, 580, 170, 60, S_CRYPTO)
    p6 = d.node("6.0\nDecode Blocks\ninto Plaintext", 240, 580, 170, 70,
                S_CRYPTO)
    p7 = d.node("7.0\nFormat Output\nand Status", 720, 380, 170, 70)
    ds1 = d.node("D1 | Active key pair (in memory)", 480, 290, 260, 40,
                 S_STORE)
    ds2 = d.node("D2 | Key files: public_key.json / private_key.json (optional)",
                 720, 290, 300, 50, S_STORE)
    csprng = d.node("Operating system CSPRNG", 720, 480, 200, 50, S_EXTERNAL)

    d.edge(user, p1, "raw input")
    d.edge(p1, p2, "key size")
    d.edge(p1, p3, "valid plaintext")
    d.edge(p1, p5, "parsed (c1, c2)")
    d.edge(p2, ds1, "(p, g, y), x")
    d.edge(ds1, p4, "public key")
    d.edge(ds1, p5, "private key x")
    d.edge(p3, p4, "message blocks m < p")
    d.edge(p4, p7, "ciphertext blocks")
    d.edge(p5, p6, "recovered integers")
    d.edge(p6, p7, "plaintext string")
    d.edge(p2, csprng, "prime search, x", S_EDGE + "dashed=1;")
    d.edge(p4, csprng, "fresh ephemeral k", S_EDGE + "dashed=1;")
    d.edge(ds1, ds2, "export / import", S_EDGE + "dashed=1;")
    d.edge(p7, user, "ciphertext, plaintext,\nkey values, error messages")
    d.node("The application holds no persistent structured data other than the\n"
           "optional key files, so no relational database appears in this DFD.",
           60, 470, 150, 110, S_NOTE)
    return d.write("dfd.drawio")


# ---------------------------------------------------------------------------
# 4-7. Flowcharts
# ---------------------------------------------------------------------------

def _flow(name: str, filename: str,
          steps: List[Tuple[str, str]],
          branches: Optional[List[Tuple[int, str, str]]] = None) -> str:
    """Build a simple vertical flowchart.

    steps: list of (style_key, label); style_key in {start, io, proc, dec, end}
    branches: list of (index_of_decision, label, target_label_of_error_node)
    """
    styles = {"start": S_TERMINAL, "end": S_TERMINAL, "io": S_IO,
              "proc": S_PROCESS, "crypto": S_CRYPTO, "dec": S_DECISION}
    d = Diagram(name)
    ids = []
    y = 40
    for kind, label in steps:
        width, height = (200, 50)
        if kind == "dec":
            width, height = (240, 80)
        cid = d.node(label, 300, y, width, height, styles[kind])
        ids.append(cid)
        y += height + 40
    for a, b in zip(ids, ids[1:]):
        d.edge(a, b, "Yes" if "dec" in [s[0] for s in steps] and False else "")
    # Error branches from decision nodes
    if branches:
        for index, label, message in branches:
            err = d.node(message, 620, 40 + index * 0, 230, 60,
                         "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                         "strokeColor=#b85450;fontSize=11;")
            d.edge(ids[index], err, label)
            d.edge(err, ids[-1], "")
    return d.write(filename)


def system_flowchart() -> str:
    d = Diagram("System Flowchart")
    start = d.node("Start", 320, 40, 160, 45, S_TERMINAL)
    launch = d.node("Launch application\n(python main.py)", 300, 120, 200, 50)
    idle = d.node("Wait for user action", 300, 200, 200, 50)
    dec = d.node("Which action?", 290, 280, 220, 70, S_DECISION)

    gen = d.node("Generate key pair\n(see key generation flowchart)",
                 60, 400, 220, 60, S_CRYPTO)
    enc = d.node("Encrypt message\n(see encryption flowchart)",
                 300, 400, 200, 60, S_CRYPTO)
    dec_op = d.node("Decrypt message\n(see decryption flowchart)",
                    520, 400, 210, 60, S_CRYPTO)
    reset = d.node("Clear all fields and\ndiscard the key pair",
                   760, 400, 200, 60)

    keycheck = d.node("Key pair available?", 290, 500, 220, 70, S_DECISION)
    err = d.node("Display error message\nin the status bar", 620, 510, 200, 50,
                 "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                 "strokeColor=#b85450;fontSize=12;")
    show = d.node("Display result and\nupdate status bar", 300, 610, 200, 50,
                  S_IO)
    exit_dec = d.node("Exit application?", 290, 700, 220, 70, S_DECISION)
    end = d.node("End", 320, 810, 160, 45, S_TERMINAL)

    d.edge(start, launch)
    d.edge(launch, idle)
    d.edge(idle, dec)
    d.edge(dec, gen, "Generate keys")
    d.edge(dec, enc, "Encrypt")
    d.edge(dec, dec_op, "Decrypt")
    d.edge(dec, reset, "Reset")
    d.edge(enc, keycheck)
    d.edge(dec_op, keycheck)
    d.edge(keycheck, err, "No")
    d.edge(keycheck, show, "Yes")
    d.edge(gen, show)
    d.edge(reset, show)
    d.edge(err, exit_dec)
    d.edge(show, exit_dec)
    d.edge(exit_dec, end, "Yes")
    d.edge(exit_dec, idle, "No")
    return d.write("system_flowchart.drawio")


def keygen_flowchart() -> str:
    d = Diagram("Key Generation Flowchart")
    y = 40
    def n(label, style=S_PROCESS, w=300, h=50):
        nonlocal y
        cid = d.node(label, 260, y, w, h, style)
        y += h + 35
        return cid

    start = n("Start", S_TERMINAL, 160, 45)
    size = n("Read requested key size (bits)", S_IO)
    valid = n("bits >= 64 ?", S_DECISION, 300, 70)
    q = n("Choose random odd candidate q\nof (bits - 1) bits", S_CRYPTO, 300, 55)
    p = n("Compute p = 2q + 1", S_CRYPTO)
    filt = n("q and p pass trial division\nby small primes?", S_DECISION, 300, 75)
    mr = n("q and p pass Miller-Rabin\n(5 rounds, then 40 rounds)?",
           S_DECISION, 300, 75)
    gen = n("Choose random g in [2, p-2] with\ng^2 mod p != 1 and g^q mod p != 1",
            S_CRYPTO, 340, 55)
    x = n("Choose private key x at random\nfrom [2, p-2] using secrets", S_CRYPTO,
          320, 55)
    yv = n("Compute y = g^x mod p", S_CRYPTO)
    out = n("Display public key (p, g, y)\nand private key x", S_IO, 300, 55)
    end = n("End", S_TERMINAL, 160, 45)

    err = d.node("Raise InvalidParameterError:\nkey size too small", 640, 190,
                 240, 55, "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                          "strokeColor=#b85450;fontSize=11;")

    d.edge(start, size)
    d.edge(size, valid)
    d.edge(valid, err, "No")
    d.edge(err, end)
    d.edge(valid, q, "Yes")
    d.edge(q, p)
    d.edge(p, filt)
    d.edge(filt, mr, "Yes")
    d.edge(filt, q, "No: discard candidate",
           S_EDGE + "exitX=0;exitY=0.5;entryX=0;entryY=0.5;")
    d.edge(mr, q, "No: discard candidate",
           S_EDGE + "exitX=0;exitY=0.5;entryX=0;entryY=0.5;")
    d.edge(mr, gen, "Yes: p is a safe prime")
    d.edge(gen, x)
    d.edge(x, yv)
    d.edge(yv, out)
    d.edge(out, end)
    return d.write("key_generation_flowchart.drawio")


def encryption_flowchart() -> str:
    d = Diagram("Encryption Flowchart")
    y = 40
    def n(label, style=S_PROCESS, w=310, h=50):
        nonlocal y
        cid = d.node(label, 250, y, w, h, style)
        y += h + 35
        return cid

    start = n("Start", S_TERMINAL, 160, 45)
    read = n("Read plaintext from the interface", S_IO)
    keychk = n("Public key available?", S_DECISION, 300, 70)
    empty = n("Plaintext is non-empty?", S_DECISION, 300, 70)
    utf8 = n("Encode plaintext as UTF-8 bytes")
    split = n("Split bytes into blocks of\n(bit_length(p) - 1)/8 - 1 bytes")
    prefix = n("Prefix each block with 0x01 and\nconvert to integer m")
    check = n("Every block satisfies 0 < m < p ?", S_DECISION, 330, 70)
    k = n("For each block: draw a fresh\nephemeral k in [2, p-2] from secrets",
          S_CRYPTO, 330, 55)
    c1 = n("Compute c1 = g^k mod p", S_CRYPTO)
    c2 = n("Compute c2 = m * y^k mod p", S_CRYPTO)
    ser = n("Serialise blocks as\n'c1:c2' in hexadecimal, one per line")
    show = n("Display ciphertext and status", S_IO)
    end = n("End", S_TERMINAL, 160, 45)

    e1 = d.node("Error: generate or import\na key pair first", 640, 160, 230, 55,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")
    e2 = d.node("Error: plaintext is empty", 640, 255, 230, 45,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")
    e3 = d.node("Raise MessageTooLargeError\n(cannot happen with correct\n"
                "block sizing; checked defensively)", 640, 610, 250, 65,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")

    d.edge(start, read)
    d.edge(read, keychk)
    d.edge(keychk, e1, "No")
    d.edge(keychk, empty, "Yes")
    d.edge(empty, e2, "No")
    d.edge(empty, utf8, "Yes")
    d.edge(utf8, split)
    d.edge(split, prefix)
    d.edge(prefix, check)
    d.edge(check, e3, "No")
    d.edge(check, k, "Yes")
    d.edge(k, c1)
    d.edge(c1, c2)
    d.edge(c2, ser)
    d.edge(ser, show)
    d.edge(show, end)
    for err in (e1, e2, e3):
        d.edge(err, end, "show message")
    return d.write("encryption_flowchart.drawio")


def decryption_flowchart() -> str:
    d = Diagram("Decryption Flowchart")
    y = 40
    def n(label, style=S_PROCESS, w=320, h=50):
        nonlocal y
        cid = d.node(label, 250, y, w, h, style)
        y += h + 35
        return cid

    start = n("Start", S_TERMINAL, 160, 45)
    read = n("Read ciphertext from the interface", S_IO)
    keychk = n("Private key available?", S_DECISION, 300, 70)
    parse = n("Parse each line as hexadecimal\nc1 and c2")
    fmt = n("Format valid and\n1 <= c1, c2 <= p - 1 ?", S_DECISION, 320, 75)
    s = n("For each block: compute\ns = c1^x mod p", S_CRYPTO)
    inv = n("Compute s^-1 mod p using the\nExtended Euclidean Algorithm",
            S_CRYPTO, 320, 55)
    m = n("Recover m = c2 * s^-1 mod p", S_CRYPTO)
    bytes_ = n("Convert m to bytes and remove\nthe 0x01 marker byte")
    marker = n("Marker byte present and\nbytes decode as UTF-8 ?", S_DECISION,
               330, 75)
    join = n("Concatenate blocks into the\nrecovered plaintext string")
    show = n("Display recovered plaintext\nand status", S_IO, 320, 55)
    end = n("End", S_TERMINAL, 160, 45)

    e1 = d.node("Error: generate or import\na key pair first", 650, 160, 230, 55,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")
    e2 = d.node("CiphertextFormatError:\nmalformed or out-of-range ciphertext",
                650, 330, 250, 55,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")
    e3 = d.node("EncodingError: wrong private key\nor corrupted ciphertext",
                650, 690, 250, 55,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;"
                "strokeColor=#b85450;fontSize=11;")

    d.edge(start, read)
    d.edge(read, keychk)
    d.edge(keychk, e1, "No")
    d.edge(keychk, parse, "Yes")
    d.edge(parse, fmt)
    d.edge(fmt, e2, "No")
    d.edge(fmt, s, "Yes")
    d.edge(s, inv)
    d.edge(inv, m)
    d.edge(m, bytes_)
    d.edge(bytes_, marker)
    d.edge(marker, e3, "No")
    d.edge(marker, join, "Yes")
    d.edge(join, show)
    d.edge(show, end)
    for err in (e1, e2, e3):
        d.edge(err, end, "show message")
    return d.write("decryption_flowchart.drawio")


# ---------------------------------------------------------------------------
# 8. Class diagram
# ---------------------------------------------------------------------------

def class_diagram() -> str:
    d = Diagram("Class Diagram")
    pub = d.swimlane_class("PublicKey  «dataclass»", [
        "+ p: int", "+ g: int", "+ y: int",
        "+ bit_length: int", "+ as_dict(): dict"], 40, 40)
    priv = d.swimlane_class("PrivateKey  «dataclass»", [
        "+ p: int", "+ g: int", "+ x: int", "+ as_dict(): dict"], 40, 220)
    pair = d.swimlane_class("KeyPair  «dataclass»", [
        "+ public: PublicKey", "+ private: PrivateKey"], 40, 380)
    manager = d.swimlane_class("KeyManager", [
        "- _keypair: KeyPair | None",
        "+ has_keys: bool",
        "+ keypair: KeyPair",
        "+ public_key: PublicKey",
        "+ private_key: PrivateKey",
        "+ generate(bits): KeyPair",
        "+ clear(): None",
        "+ set_keypair(kp): None",
        "+ export_public(path): None",
        "+ export_private(path): None",
        "+ load_public(path): PublicKey",
        "+ load_private(path): PrivateKey",
        "+ load_pair(pub, priv): KeyPair"], 360, 40, 280)
    app = d.swimlane_class("ElGamalApp  (ttk.Frame)", [
        "- keys: KeyManager",
        "- _result_queue: Queue",
        "+ on_generate_keys(): None",
        "+ on_show_keys(): None",
        "+ on_export_keys(): None",
        "+ on_import_keys(): None",
        "+ on_encrypt(): None",
        "+ on_decrypt(): None",
        "+ on_copy_ciphertext(): None",
        "+ on_reset(): None",
        "+ set_status(msg, error): None"], 700, 40, 280)

    mod_elgamal = d.swimlane_class("«module» elgamal.py", [
        "+ is_probable_prime(n, rounds)",
        "+ generate_prime(bits)",
        "+ generate_safe_prime(bits)",
        "+ find_generator(p, q)",
        "+ extended_gcd(a, b)",
        "+ mod_inverse(a, m)",
        "+ generate_keypair(bits)",
        "+ validate_public_key(key)",
        "+ encrypt_int(m, pub)",
        "+ decrypt_int(c1, c2, priv)",
        "+ encrypt_blocks(blocks, pub)",
        "+ decrypt_blocks(pairs, priv)"], 360, 400, 280)
    mod_utils = d.swimlane_class("«module» crypto_utils.py", [
        "+ block_size(p)",
        "+ text_to_blocks(text, p)",
        "+ blocks_to_text(blocks)",
        "+ pairs_to_string(pairs)",
        "+ string_to_pairs(text)",
        "+ encrypt_text(text, pub)",
        "+ decrypt_text(ct, priv)",
        "+ ciphertext_expansion(pt, ct)"], 700, 400, 280)

    exc = d.swimlane_class("ElGamalError  (Exception)", [
        "InvalidParameterError",
        "MessageTooLargeError",
        "DecryptionError",
        "EncodingError",
        "CiphertextFormatError",
        "KeyManagerError"], 40, 520, 280)

    agg = S_EDGE + "endArrow=diamondThin;endFill=0;"
    d.edge(pair, pub, "1", agg)
    d.edge(pair, priv, "1", agg)
    d.edge(manager, pair, "manages 0..1", agg)
    d.edge(app, manager, "uses")
    d.edge(app, mod_utils, "calls encrypt_text / decrypt_text")
    d.edge(mod_utils, mod_elgamal, "calls encrypt_blocks / decrypt_blocks")
    d.edge(manager, mod_elgamal, "calls generate_keypair")
    d.edge(mod_elgamal, exc, "raises", S_EDGE + "dashed=1;")
    d.edge(mod_utils, exc, "raises", S_EDGE + "dashed=1;")
    return d.write("class_diagram.drawio")


def main() -> None:
    produced = [
        system_architecture(),
        use_case(),
        dfd(),
        system_flowchart(),
        keygen_flowchart(),
        encryption_flowchart(),
        decryption_flowchart(),
        class_diagram(),
    ]
    for path in produced:
        print("written:", os.path.basename(path))
    print(f"\n{len(produced)} draw.io files written to {OUT_DIR}")
    print("Open each file at https://app.diagrams.net and export as PNG "
          "for the report.")


if __name__ == "__main__":
    main()
