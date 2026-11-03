#!/usr/bin/env python3
"""
Exports the icons chosen from preview.html, each into final/<app>/ on the tile, into final2/<app>/
without it, and into final3/<app>/ without it and filling the frame:

    enigma-<app>.svg            the master: the chosen variant, for the 40 px frames and up
    enigma-<app>-small.svg      a simpler drawing for the 16 to 32 px frames, where the master blurs;
                                an application without one uses its master for every frame
    png/enigma-<app>-<N>.png    every size in SIZES, each rendered by rsvg-convert from its drawing
    enigma-<app>.ico            the same PNGs, unchanged and smallest first, as 32-bit PNG entries

    python3 export.py                  writes final/, final2/ and final3/
    python3 export.py final2 final3    writes only the targets named: final, final2, final3

In final2/ and final3/, a drawing that painted in the tile's colour to show the tile through -- the
GitClient ring, the rocket's window, the QR finder holes, the gap round the licence seal -- has those
parts cut out, so the desktop shows through instead. Placed on the tile, a final2/ icon looks like its
final/ twin.

A final2/ drawing keeps the margin it had inside the tile, so without the tile it looks small next to
other applications' icons. In final3/, every drawing spans the live area LIVE -- 16 to 240 of the 256-unit
view box -- on its longest side, centred. The master is the final2/ drawing in one transform, scaled and
centred from its bounds as rsvg-convert renders them. The small drawing is not scaled, which would move its
edges off whole pixels: it is drawn again on the live area, its straight edges on the 16-unit grid -- whole
pixels at 16 and 32 px.

The variants themselves stay in <app>/ and are not touched.
"""
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

sys.dont_write_bytecode = True
import generate as g  # noqa: E402
from generate import TILE, stroke  # noqa: E402

ROOT = Path(__file__).resolve().parent
# Output folder: whether its icons are drawn on the tile, and whether they are scaled to fill LIVE.
TARGETS = {"final": (True, False), "final2": (False, False), "final3": (False, True)}
SIZES = (16, 20, 24, 32, 40, 48, 64, 96, 128, 256)
SMALL_UP_TO = 32
# The square, in view-box units, whose side the longest side of a filling drawing spans: 1 px of margin
# at 16 px, a 16-unit grid step. The masters follow it; the *_small_live drawings are laid out on it by hand,
# on the grid, and must be redrawn if it changes.
LIVE = (16, 240)
# The resolution at which a drawing is rendered to measure its bounds: 1/4 unit per pixel.
MEASURE_PX = 1024


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


def hardcopy_small(p, cut=False):
    # The three finder patterns and the accent block, without the data modules.
    out = []
    for x, y in ((32, 32), (144, 32), (32, 144)):
        if cut:
            ring = g.rounded_rect_d(x, y, 80, 80, 16) + g.rounded_rect_d(x + 16, y + 16, 48, 48, 6)
            out.append(f'<path d="{ring}" fill="{p.main}" fill-rule="evenodd"/>')
        else:
            out += [
                f'<rect x="{x}" y="{y}" width="80" height="80" rx="16" fill="{p.main}"/>',
                f'<rect x="{x + 16}" y="{y + 16}" width="48" height="48" rx="6" fill="{TILE}"/>',
            ]
        out.append(f'<rect x="{x + 32}" y="{y + 32}" width="16" height="16" fill="{p.main}"/>')
    return out + [f'<rect x="152" y="152" width="64" height="64" rx="12" fill="{p.accent}"/>']


def backup_small(p):
    teeth = [f'<rect x="{96 if i % 2 == 0 else 128}" y="{48 + i * 16}" width="32" height="16" fill="{ink(p)}"/>'
             for i in range(4)]
    return small_page(p) + teeth + [
        f'<rect x="96" y="120" width="64" height="80" rx="16" fill="{p.accent}"/>',
        f'<rect x="120" y="152" width="16" height="32" rx="4" fill="{p.main}"/>',
    ]


def licensing_small(p, cut=False):
    seal = (176, 160)
    tail_points = [g.ribbon_tail(*seal, deg, 64, 13) for deg in (-20, 20)]
    tails = ["M" + "L".join(f"{g.n(x)} {g.n(y)}" for x, y in t) + "Z" for t in tail_points]
    lines = [
        f'<rect x="48" y="72" width="96" height="16" fill="{ink(p)}"/>',
        f'<rect x="48" y="104" width="72" height="16" fill="{ink(p)}"/>',
    ]
    if cut:
        # As licensing_certificate(cut=True): the seal's gap ring, out to 48, cut out of the certificate
        # and the tails.
        gap = 48
        return [
            f'<path d="{g.subtract_circle(g.rounded_rect_outline(24, 48, 208, 128, 16), seal, gap)}" fill="{p.main}"/>',
            *lines,
            *(f'<path d="{g.subtract_circle(g.polygon_outline(t), seal, gap)}" fill="{p.accent}"/>' for t in tail_points),
            f'<circle cx="{seal[0]}" cy="{seal[1]}" r="32" fill="{p.accent}"/>',
        ]
    return [
        f'<rect x="24" y="48" width="208" height="128" rx="16" fill="{p.main}"/>',
        *lines,
        *(f'<path d="{d}" fill="none" stroke="{TILE}" stroke-width="12" stroke-linejoin="round"/>' for d in tails),
        *(f'<path d="{d}" fill="{p.accent}"/>' for d in tails),
        f'<circle cx="{seal[0]}" cy="{seal[1]}" r="40" fill="{p.accent}" stroke="{TILE}" stroke-width="16"/>',
    ]


# --- the small drawings of a target that fills the frame: each small drawing above re-laid so its longest
# side spans LIVE, centred, with every horizontal and vertical edge on the 16-unit grid -- whole pixels at
# 16 and 32 px. Drawn without the tile: what showed the tile through is a cut-out from the start. ---------

def git_client_small_live(p):
    # Heavier than git_client_small -- 32-unit lines, main nodes of radius 32 -- so it still paints a quarter
    # of its frame. The branch node stays the smaller one; that leaves the drawing 2 units left of centre,
    # the price of keeping both lines on the grid.
    return [
        stroke("M80 48V208", p.main, 32),
        stroke("M80 208H136A40 40 0 0 0 176 168V128", p.accent, 32),
        *(f'<circle cx="80" cy="{y}" r="32" fill="{p.main}"/>' for y in (48, 128, 208)),
        f'<circle cx="176" cy="128" r="28" fill="{p.accent}"/>',
    ]


def markdown_editor_small_live(p):
    # The frame's outer corners are rounded by 16, not 24: nearer the master's, and the weight it needs.
    frame = g.rounded_rect_d(16, 64, 224, 128, 16) + g.rounded_rect_d(32, 80, 192, 96, 8)
    return [
        f'<path d="{frame}" fill="{p.main}" fill-rule="evenodd"/>',
        f'<path d="M48 160V96H80L96 116L112 96H144V160H112V132L96 152L80 132V160Z" fill="{p.main}"/>',
        f'<path d="M176 96H192V128H208L184 160L160 128H176Z" fill="{p.accent}"/>',
    ]


def text_editor_small_live(p):
    return [
        f'<rect x="16" y="32" width="224" height="192" rx="24" fill="{p.main}"/>',
        f'<path d="M40 32H48V176H16V56A24 24 0 0 1 40 32Z" fill="{p.shade}"/>',
        f'<path d="M16 176H240V200A24 24 0 0 1 216 224H40A24 24 0 0 1 16 200Z" fill="{ink(p)}"/>',
        f'<rect x="32" y="192" width="48" height="16" rx="4" fill="{p.accent}"/>',
        f'<rect x="64" y="64" width="128" height="16" fill="{ink(p)}"/>',
        f'<rect x="64" y="96" width="80" height="16" fill="{ink(p)}"/>',
        f'<rect x="64" y="128" width="112" height="16" fill="{ink(p)}"/>',
        f'<rect x="160" y="80" width="16" height="48" fill="{p.accent}"/>',
    ]


def hardcopy_small_live(p):
    # The finder patterns grow to 6 grid units: a ring of 1, a hole of 1, a centre of 2.
    out = []
    for x, y in ((16, 16), (144, 16), (16, 144)):
        ring = g.rounded_rect_d(x, y, 96, 96, 16) + g.rounded_rect_d(x + 16, y + 16, 64, 64, 6)
        out += [f'<path d="{ring}" fill="{p.main}" fill-rule="evenodd"/>',
                f'<rect x="{x + 32}" y="{y + 32}" width="32" height="32" fill="{p.main}"/>']
    return out + [f'<rect x="160" y="160" width="64" height="64" rx="12" fill="{p.accent}"/>']


def backup_small_live(p):
    # Five teeth instead of four, and a keyhole 2 units wide: centred on the zip, 1 unit would straddle
    # two pixels.
    teeth = [f'<rect x="{96 if i % 2 == 0 else 128}" y="{32 + i * 16}" width="32" height="16" fill="{ink(p)}"/>'
             for i in range(5)]
    return [
        f'<path d="M48 16H160L224 80V224A16 16 0 0 1 208 240H48A16 16 0 0 1 32 224V32A16 16 0 0 1 48 16Z" fill="{p.main}"/>',
        f'<path d="M160 16V80H224Z" fill="{p.shade}"/>',
        *teeth,
        f'<rect x="96" y="128" width="64" height="80" rx="16" fill="{p.accent}"/>',
        f'<rect x="112" y="160" width="32" height="32" rx="4" fill="{p.main}"/>',
    ]


def licensing_small_live(p):
    # As licensing_small(cut=True): the seal's gap ring, out to 50, cut out of the certificate and the tails.
    # The tails end at 224, so the drawing is centred between the certificate's top and their tips.
    seal, gap = (176, 160), 50
    tails = [g.ribbon_tail(*seal, deg, 63, 14) for deg in (-20, 20)]
    return [
        f'<path d="{g.subtract_circle(g.rounded_rect_outline(16, 32, 224, 144, 16), seal, gap)}" fill="{p.main}"/>',
        f'<rect x="48" y="64" width="112" height="16" fill="{ink(p)}"/>',
        f'<rect x="48" y="96" width="80" height="16" fill="{ink(p)}"/>',
        *(f'<path d="{g.subtract_circle(g.polygon_outline(t), seal, gap)}" fill="{p.accent}"/>' for t in tails),
        f'<circle cx="{seal[0]}" cy="{seal[1]}" r="34" fill="{p.accent}"/>',
    ]


# Application key, chosen variant (shape letter, palette number), file stem, small drawing or None, and the
# small drawing of a target that fills the frame, or None.
CHOSEN = [
    ("git-client", "A", 2, "enigma-git-client", git_client_small, git_client_small_live),
    ("msi", "A", 2, "enigma-msi", None, None),
    ("launchpad", "A", 2, "enigma-launchpad", None, None),
    ("markdown-editor", "A", 2, "enigma-markdown-editor", markdown_editor_small, markdown_editor_small_live),
    ("text-editor", "B", 2, "enigma-text-editor", text_editor_small, text_editor_small_live),
    ("file-explorer", "E", 2, "enigma-file-explorer", None, None),
    ("hardcopy", "B", 2, "enigma-hardcopy", hardcopy_small, hardcopy_small_live),
    ("backup", "B", 2, "enigma-backup", backup_small, backup_small_live),
    ("licensing", "A", 2, "enigma-licensing", licensing_small, licensing_small_live),
]


def document(comment, size, body, tile):
    inner = "\n".join("  " + line for line in body)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f"<!--\n{comment}\n-->\n"
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 256 256">\n'
            + (f"  {g.TILE_RECT}\n" if tile else "") + f"{inner}\n</svg>\n")


def tile_free(draw, p):
    """draw(p) for a target without the tile: a drawing that paints in the tile's colour is drawn with
    cut=True, which cuts those parts out instead."""
    body = draw(p)
    if any(TILE in line for line in body):
        body = draw(p, cut=True)
        if any(TILE in line for line in body):
            raise ValueError(f"{draw.__name__}(cut=True) still paints in the tile's colour")
    return body


def decimals(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def png_alpha(data):
    """The alpha channel of an 8-bit RGBA, non-interlaced PNG -- what rsvg-convert writes -- one bytes
    object per row."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    pos, idat, w, h = 8, b"", 0, 0
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            w, h, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", body)
            if (depth, colour, interlace) != (8, 6, 0):
                raise ValueError(f"not an 8-bit RGBA, non-interlaced PNG: depth {depth}, colour type {colour}, "
                                 f"interlace {interlace}")
        elif kind == b"IDAT":
            idat += body
        pos += 12 + length
    raw, stride = zlib.decompress(idat), w * 4
    prev, rows = bytearray(stride), []
    for y in range(h):
        start = y * (stride + 1)
        kind, line = raw[start], bytearray(raw[start + 1:start + 1 + stride])
        if kind == 1:
            for i in range(4, stride):
                line[i] = (line[i] + line[i - 4]) & 255
        elif kind == 2:
            line = bytearray((a + b) & 255 for a, b in zip(line, prev))
        elif kind == 3:
            for i in range(stride):
                line[i] = (line[i] + ((line[i - 4] if i >= 4 else 0) + prev[i]) // 2) & 255
        elif kind == 4:
            for i in range(stride):
                a, b, c = (line[i - 4], prev[i], prev[i - 4]) if i >= 4 else (0, prev[i], 0)
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        elif kind:
            raise ValueError(f"unknown PNG filter {kind}")
        rows.append(bytes(line[3::4]))
        prev = line
    return rows


HALF_COVERED = bytes(int(a >= 128) for a in range(256))


def visible_bounds(body):
    """The box (x0, y0, x1, y1), in view-box units, of what the drawing paints: rendered by rsvg-convert at
    MEASURE_PX, the pixels at least half covered."""
    with tempfile.TemporaryDirectory() as tmp:
        src, png = Path(tmp) / "drawing.svg", Path(tmp) / "drawing.png"
        src.write_text(document("  Measured by export.py.", 256, body, False), encoding="utf-8")
        subprocess.run(["rsvg-convert", "-w", str(MEASURE_PX), "-h", str(MEASURE_PX), str(src), "-o", str(png)],
                       check=True)
        alpha = png_alpha(png.read_bytes())
    marks = [row.translate(HALF_COVERED) for row in alpha]
    rows = [y for y, m in enumerate(marks) if 1 in m]
    if not rows:
        raise ValueError("the drawing paints nothing")
    x0 = min(m.find(1) for m in marks if 1 in m)
    x1 = max(m.rfind(1) for m in marks if 1 in m) + 1
    unit = 256 / MEASURE_PX
    return x0 * unit, rows[0] * unit, x1 * unit, (rows[-1] + 1) * unit


def fill_live(body):
    """body in one transform that scales it until its longest side spans LIVE and centres it there, and
    the scale."""
    x0, y0, x1, y1 = visible_bounds(body)
    low, high = LIVE
    scale = (high - low) / max(x1 - x0, y1 - y0)
    middle = (low + high) / 2
    move = (middle - scale * (x0 + x1) / 2, middle - scale * (y0 + y1) / 2)
    return [f'<g transform="translate({decimals(move[0])} {decimals(move[1])}) scale({decimals(scale)})">',
            *("  " + line for line in body), "</g>"], scale


def write_ico(path, frames):
    """frames: (size, PNG bytes) pairs, smallest first. A 256 px entry stores its size as 0."""
    offset = 6 + 16 * len(frames)
    entries, data = b"", b""
    for size, png in frames:
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset + len(data))
        data += png
    path.write_bytes(struct.pack("<HHH", 0, 1, len(frames)) + entries + data)


def export(target, key, letter, number, stem, small, small_live):
    tile, fill = TARGETS[target]
    app = next(a for a in g.APPS if a["key"] == key)
    title, draw = next((t, d) for s, t, _, d in app["shapes"] if s == letter)
    p = next(p for p in g.PALETTES if p.number == number)
    paint = (lambda d: d(p)) if tile else (lambda d: tile_free(d, p))
    variant = f'{app["prefix"]}-{letter}{number}'
    folder = ROOT / target / key
    (folder / "png").mkdir(parents=True, exist_ok=True)

    icon = "application icon" if tile else "application icon without the tile"
    body, scale, fill_note, small_note = paint(draw), None, "", ""
    if fill:
        # A small drawing is not scaled, which would move its edges off whole pixels: it has its own on LIVE.
        icon, small = f"{icon}, filling the frame ({target})", small_live
        body, scale = fill_live(body)
        fill_note = (f"  The final2/ drawing scaled by {decimals(scale)} and centred, its longest side spanning "
                     f"{LIVE[0]} to {LIVE[1]} of the 256-unit view box.\n")
        small_note = (f"\n  Drawn on the live area, {LIVE[0]} to {LIVE[1]}, with its straight edges on the 16-unit grid."
                      f"\n  Regenerate the SVGs, the PNG frames and the .ico with: python3 Branding/Apps/export.py {target}")
    master = folder / f"{stem}.svg"
    frames_note = (f"The master for the {SIZES[SIZES.index(SMALL_UP_TO) + 1]} px frames and up; the "
                   f"{SIZES[0]} to {SMALL_UP_TO} px frames come from {stem}-small.svg, simplified for their size."
                   if small else f"The master for every frame, {SIZES[0]} to {SIZES[-1]} px.")
    master.write_text(document(
        f"  {app['name']} {icon}: {variant} in Branding/Apps/preview.html, {title} in the {p.name} palette.\n"
        f"{fill_note}"
        f"  {frames_note}\n"
        f"  Regenerate the SVGs, the PNG frames and the .ico with: python3 Branding/Apps/export.py"
        + ("" if tile else f" {target}"), 256, body, tile))
    sources = {s: master for s in SIZES}
    if small:
        small_path = folder / f"{stem}-small.svg"
        small_path.write_text(document(
            f"  {app['name']} {icon}, simplified for the {SIZES[0]} to {SMALL_UP_TO} px frames: "
            f"{stem}.svg with heavier marks and fewer details.{small_note}", 32, paint(small), tile))
        sources.update({s: small_path for s in SIZES if s <= SMALL_UP_TO})

    frames = []
    for size in SIZES:
        png = folder / "png" / f"{stem}-{size}.png"
        subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(sources[size]), "-o", str(png)], check=True)
        frames.append((size, png.read_bytes()))
    write_ico(folder / f"{stem}.ico", frames)
    return variant, folder, scale


if __name__ == "__main__":
    targets = list(dict.fromkeys(sys.argv[1:])) or list(TARGETS)
    unknown = [t for t in targets if t not in TARGETS]
    if unknown:
        sys.exit(f"export.py: unknown target {', '.join(unknown)}; expected any of: {', '.join(TARGETS)}")
    for target in targets:
        for chosen in CHOSEN:
            variant, folder, scale = export(target, *chosen)
            print(f"{variant:7} -> {folder.relative_to(ROOT)}" + (f"  (scaled by {decimals(scale)})" if scale else ""))
