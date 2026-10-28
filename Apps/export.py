#!/usr/bin/env python3
"""
Exports the icons chosen from preview.html, each into final/<app>/:

    enigma-<app>.svg            the master: the chosen variant, for the 40 px frames and up
    enigma-<app>-small.svg      a simpler drawing for the 16 to 32 px frames, where the master blurs;
                                an application without one uses its master for every frame
    png/enigma-<app>-<N>.png    every size in SIZES, each rendered by rsvg-convert from its drawing
    enigma-<app>.ico            the same PNGs, unchanged and smallest first, as 32-bit PNG entries

    python3 export.py

The variants themselves stay in <app>/ and are not touched.
"""
import struct
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import generate as g  # noqa: E402
from generate import TILE, stroke  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "final"
SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
SMALL_UP_TO = 32


def ink(p):
    """The marks drawn on main at small sizes: deep, darkened until it still reads at 16 px."""
    r, gr, b = (int(p.deep[i:i + 2], 16) for i in (1, 3, 5))
    return "#{:02X}{:02X}{:02X}".format(*(round(c * 0.65) for c in (r, gr, b)))


def small_page(p):
    return [
        f'<path d="M64 32H160L208 80V208A16 16 0 0 1 192 224H64A16 16 0 0 1 48 208V48A16 16 0 0 1 64 32Z" fill="{p.main}"/>',
        f'<path d="M160 32V80H208Z" fill="{p.shade}"/>',
    ]


# --- the small drawings: heavier marks, fewer details, edges on the 16-unit grid of a 16 px frame -----

def git_client_small(p):
    # The current enigma-git-client-small.svg: the ring filled, the lines and nodes heavier.
    return [
        stroke("M92 64V192", p.main, 24),
        stroke("M92 192H136A32 32 0 0 0 168 160V128", p.accent, 24),
        *(f'<circle cx="92" cy="{y}" r="28" fill="{p.main}"/>' for y in (64, 128, 192)),
        f'<circle cx="168" cy="128" r="24" fill="{p.accent}"/>',
    ]


def markdown_editor_small(p):
    return [
        f'<rect x="32" y="72" width="192" height="112" rx="16" fill="none" stroke="{p.main}" stroke-width="16"/>',
        f'<path d="M48 160V96H72L88 116L104 96H128V160H104V132L88 152L72 132V160Z" fill="{p.main}"/>',
        f'<path d="M168 96H192V124H208L180 160L152 124H168Z" fill="{p.accent}"/>',
    ]


def text_editor_small(p):
    return [
        f'<rect x="32" y="40" width="192" height="176" rx="24" fill="{p.main}"/>',
        f'<path d="M56 40H64V176H32V64A24 24 0 0 1 56 40Z" fill="{p.shade}"/>',
        f'<path d="M32 176H224V192A24 24 0 0 1 200 216H56A24 24 0 0 1 32 192Z" fill="{ink(p)}"/>',
        f'<rect x="48" y="184" width="48" height="16" rx="4" fill="{p.accent}"/>',
        f'<rect x="80" y="64" width="112" height="16" fill="{ink(p)}"/>',
        f'<rect x="80" y="96" width="64" height="16" fill="{ink(p)}"/>',
        f'<rect x="80" y="128" width="96" height="16" fill="{ink(p)}"/>',
        f'<rect x="160" y="88" width="24" height="32" fill="{p.accent}"/>',
    ]


def hardcopy_small(p):
    # The three finder patterns and the accent block, without the data modules.
    out = []
    for x, y in ((32, 32), (144, 32), (32, 144)):
        out += [
            f'<rect x="{x}" y="{y}" width="80" height="80" rx="16" fill="{p.main}"/>',
            f'<rect x="{x + 16}" y="{y + 16}" width="48" height="48" rx="6" fill="{TILE}"/>',
            f'<rect x="{x + 32}" y="{y + 32}" width="16" height="16" fill="{p.main}"/>',
        ]
    return out + [f'<rect x="152" y="152" width="64" height="64" rx="12" fill="{p.accent}"/>']


def backup_small(p):
    teeth = [f'<rect x="{96 if i % 2 == 0 else 128}" y="{48 + i * 16}" width="32" height="16" fill="{ink(p)}"/>'
             for i in range(4)]
    return small_page(p) + teeth + [
        f'<rect x="96" y="120" width="64" height="80" rx="16" fill="{p.accent}"/>',
        f'<rect x="120" y="152" width="16" height="32" rx="4" fill="{p.main}"/>',
    ]


def licensing_small(p):
    seal = (176, 160)
    tails = ["M" + "L".join(f"{g.n(x)} {g.n(y)}" for x, y in g.ribbon_tail(*seal, deg, 64, 13)) + "Z"
             for deg in (-20, 20)]
    return [
        f'<rect x="24" y="48" width="208" height="128" rx="16" fill="{p.main}"/>',
        f'<rect x="48" y="72" width="96" height="16" fill="{ink(p)}"/>',
        f'<rect x="48" y="104" width="72" height="16" fill="{ink(p)}"/>',
        *(f'<path d="{d}" fill="none" stroke="{TILE}" stroke-width="12" stroke-linejoin="round"/>' for d in tails),
        *(f'<path d="{d}" fill="{p.accent}"/>' for d in tails),
        f'<circle cx="{seal[0]}" cy="{seal[1]}" r="40" fill="{p.accent}" stroke="{TILE}" stroke-width="16"/>',
    ]


# Application key, chosen variant (shape letter, palette number), file stem, small drawing or None.
CHOSEN = [
    ("git-client", "A", 2, "enigma-git-client", git_client_small),
    ("msi", "A", 2, "enigma-msi", None),
    ("launchpad", "A", 2, "enigma-launchpad", None),
    ("markdown-editor", "A", 2, "enigma-markdown-editor", markdown_editor_small),
    ("text-editor", "B", 2, "enigma-text-editor", text_editor_small),
    ("file-explorer", "E", 2, "enigma-file-explorer", None),
    ("hardcopy", "B", 2, "enigma-hardcopy", hardcopy_small),
    ("backup", "B", 2, "enigma-backup", backup_small),
    ("licensing", "A", 2, "enigma-licensing", licensing_small),
]


def document(comment, size, body):
    inner = "\n".join("  " + line for line in body)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f"<!--\n{comment}\n-->\n"
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 256 256">\n'
            f"  {g.TILE_RECT}\n{inner}\n</svg>\n")


def write_ico(path, frames):
    """frames: (size, PNG bytes) pairs, smallest first. A 256 px entry stores its size as 0."""
    offset = 6 + 16 * len(frames)
    entries, data = b"", b""
    for size, png in frames:
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset + len(data))
        data += png
    path.write_bytes(struct.pack("<HHH", 0, 1, len(frames)) + entries + data)


def export(key, letter, number, stem, small):
    app = next(a for a in g.APPS if a["key"] == key)
    title, draw = next((t, d) for s, t, _, d in app["shapes"] if s == letter)
    p = next(p for p in g.PALETTES if p.number == number)
    variant = f'{app["prefix"]}-{letter}{number}'
    folder = OUT / key
    (folder / "png").mkdir(parents=True, exist_ok=True)

    master = folder / f"{stem}.svg"
    frames_note = (f"The master for the {SIZES[SIZES.index(SMALL_UP_TO) + 1]} px frames and up; the "
                   f"{SIZES[0]} to {SMALL_UP_TO} px frames come from {stem}-small.svg, simplified for their size."
                   if small else f"The master for every frame, {SIZES[0]} to {SIZES[-1]} px.")
    master.write_text(document(
        f"  {app['name']} application icon: {variant} in Branding/Apps/preview.html, {title} in the {p.name} palette.\n"
        f"  {frames_note}\n"
        f"  Regenerate the SVGs, the PNG frames and the .ico with: python3 Branding/Apps/export.py", 256, draw(p)))
    sources = {s: master for s in SIZES}
    if small:
        small_path = folder / f"{stem}-small.svg"
        small_path.write_text(document(
            f"  {app['name']} application icon, simplified for the {SIZES[0]} to {SMALL_UP_TO} px frames: "
            f"{stem}.svg with heavier marks and fewer details.", 32, small(p)))
        sources.update({s: small_path for s in SIZES if s <= SMALL_UP_TO})

    frames = []
    for size in SIZES:
        png = folder / "png" / f"{stem}-{size}.png"
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(sources[size]), "-o", str(png)], check=True)
        frames.append((size, png.read_bytes()))
    write_ico(folder / f"{stem}.ico", frames)
    return variant, folder


if __name__ == "__main__":
    for chosen in CHOSEN:
        variant, folder = export(*chosen)
        print(f"{variant:7} -> {folder.relative_to(ROOT)}")
