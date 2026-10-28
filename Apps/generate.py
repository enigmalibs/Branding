#!/usr/bin/env python3
"""
Generates the Enigma application icon variants and the page that shows them side by side.

Every icon is drawn on the Enigma.GitClient tile -- a #1E1F22 square of 240 units, inset by 8 and
rounded by 48, in a 256-unit view box -- and in one of the palettes below. A variant is named by its
application prefix, its shape letter and its palette number: MSI-A1 is the first Enigma.Msi shape in
the Classic palette.

    python3 generate.py        writes <app>/<app>-<shape><palette>.svg and preview.html next to it
"""
import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TILE = "#1E1F22"
TILE_RECT = f'<rect x="8" y="8" width="240" height="240" rx="48" fill="{TILE}"/>'


class Palette:
    """main: the body. shade: its darker side. deep: marks drawn on main. accent: the one highlight.
    light: a lit face or a page."""

    def __init__(self, number, name, main, shade, deep, accent, light):
        self.number, self.name = number, name
        self.main, self.shade, self.deep, self.accent, self.light = main, shade, deep, accent, light


PALETTES = [
    Palette(1, "Classic", "#3574F0", "#2558C4", "#2D56A8", "#3FB950", "#CFDDFB"),
    Palette(2, "Soft", "#6A9BF4", "#4F7FDB", "#4A72C4", "#63C77D", "#D9E5FC"),
    Palette(3, "Sky & Mint", "#9DC4F5", "#74A3E6", "#5F8BCB", "#93DDBA", "#E1EDFD"),
    Palette(4, "Lavender & Peach", "#B8A6F2", "#957FE0", "#7F6AC6", "#FFB894", "#EAE4FD"),
    Palette(5, "Mint & Pink", "#93DDBA", "#68C29A", "#4FA581", "#F4A2C0", "#DDF5EA"),
    Palette(6, "Peach & Sky", "#FFB894", "#F2956A", "#D97A50", "#9DC4F5", "#FFE6D9"),
]


# --- geometry helpers ---------------------------------------------------------------------------

def n(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def poly(points, fill):
    d = "M" + "L".join(f"{n(x)} {n(y)}" for x, y in points) + "Z"
    return f'<path d="{d}" fill="{fill}"/>'


def cube(cx, cy, r):
    """The six corners and the centre of an isometric cube whose outline has radius r."""
    w = r * math.cos(math.pi / 6)
    return {
        "T": (cx, cy - r), "UR": (cx + w, cy - r / 2), "LR": (cx + w, cy + r / 2), "B": (cx, cy + r),
        "LL": (cx - w, cy + r / 2), "UL": (cx - w, cy - r / 2), "C": (cx, cy),
    }


def cube_faces(v, p):
    # The silhouette goes first, so the anti-aliased seams between faces show a face colour, not the tile.
    return [
        poly([v["T"], v["UR"], v["LR"], v["B"], v["LL"], v["UL"]], p.main),
        poly([v["T"], v["UR"], v["C"], v["UL"]], p.light),
        poly([v["UL"], v["C"], v["B"], v["LL"]], p.main),
        poly([v["C"], v["UR"], v["LR"], v["B"]], p.shade),
    ]


def folder(x, y, w, h, tab, r, fill):
    """A folder silhouette: a tab of width `tab` on the top left, sloping down to the body."""
    th = 14
    d = (f"M{x} {y + r}A{r} {r} 0 0 1 {x + r} {y}H{x + tab}L{x + tab + th} {y + th}H{x + w - r}"
         f"A{r} {r} 0 0 1 {x + w} {y + th + r}V{y + h - r}A{r} {r} 0 0 1 {x + w - r} {y + h}"
         f"H{x + r}A{r} {r} 0 0 1 {x} {y + h - r}Z")
    return f'<path d="{d}" fill="{fill}"/>'


def page(p):
    return [
        f'<path d="M74 44H158L194 80V200A12 12 0 0 1 182 212H74A12 12 0 0 1 62 200V56A12 12 0 0 1 74 44Z" fill="{p.main}"/>',
        f'<path d="M158 44V80H194Z" fill="{p.shade}"/>',
    ]


def stroke(d, color, width, cap="butt", join="miter"):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"'
            + (f' stroke-linecap="{cap}"' if cap != "butt" else "")
            + (f' stroke-linejoin="{join}"' if join != "miter" else "") + "/>")


# --- Enigma.GitClient -----------------------------------------------------------------------------

def git_branch(p):
    # The current icon, unchanged in the Classic palette.
    return [
        stroke("M92 64V192", p.main, 18),
        stroke("M92 192H136A32 32 0 0 0 168 160V128", p.accent, 18),
        f'<circle cx="92" cy="128" r="26" fill="{p.main}"/>',
        f'<circle cx="92" cy="192" r="26" fill="{p.main}"/>',
        f'<circle cx="168" cy="128" r="22" fill="{p.accent}"/>',
        f'<circle cx="92" cy="64" r="19.5" fill="{TILE}" stroke="{p.main}" stroke-width="13"/>',
    ]


def git_merge(p):
    return [
        stroke("M92 192H136A32 32 0 0 0 168 160V96A32 32 0 0 0 136 64H92", p.accent, 18),
        stroke("M92 64V192", p.main, 18),
        f'<circle cx="92" cy="128" r="24" fill="{p.main}"/>',
        f'<circle cx="92" cy="192" r="26" fill="{p.main}"/>',
        f'<circle cx="168" cy="128" r="22" fill="{p.accent}"/>',
        f'<circle cx="92" cy="64" r="19.5" fill="{TILE}" stroke="{p.main}" stroke-width="13"/>',
    ]


def git_fork(p):
    return [
        stroke("M128 192C128 146 172 152 172 112V72", p.accent, 18),
        stroke("M128 192C128 146 84 152 84 112V72", p.main, 18),
        f'<circle cx="128" cy="192" r="26" fill="{p.main}"/>',
        f'<circle cx="84" cy="68" r="22" fill="{p.main}"/>',
        f'<circle cx="172" cy="68" r="19.5" fill="{TILE}" stroke="{p.accent}" stroke-width="13"/>',
    ]


def git_history(p):
    return [
        stroke("M72 64V192", p.main, 14),
        stroke("M72 184H90A22 22 0 0 0 112 162V128", p.accent, 14),
        *(f'<circle cx="72" cy="{y}" r="17" fill="{p.main}"/>' for y in (72, 128, 184)),
        f'<circle cx="112" cy="128" r="15" fill="{p.accent}"/>',
        f'<rect x="140" y="64" width="72" height="16" rx="8" fill="{p.shade}"/>',
        f'<rect x="140" y="120" width="56" height="16" rx="8" fill="{p.accent}"/>',
        f'<rect x="140" y="176" width="64" height="16" rx="8" fill="{p.shade}"/>',
    ]


# --- Enigma.Msi -----------------------------------------------------------------------------------

def msi_taped_cube(p):
    v = cube(128, 128, 88)
    half = 11
    m = ((v["UL"][0] + v["C"][0]) / 2, (v["UL"][1] + v["C"][1]) / 2)
    o = (math.cos(math.pi / 6) * half, 0.5 * half)
    a, b = (m[0] - o[0], m[1] - o[1]), (m[0] + o[0], m[1] + o[1])
    back = (v["T"][0] - v["UL"][0], v["T"][1] - v["UL"][1])
    down = (0, 88)
    return cube_faces(v, p) + [
        poly([a, b, add(b, back), add(a, back)], p.accent),
        poly([a, b, add(b, down), add(a, down)], p.accent),
    ]


def msi_checked_box(p):
    return [
        f'<rect x="44" y="56" width="168" height="38" rx="12" fill="{p.main}"/>',
        f'<path d="M56 102H200V186A16 16 0 0 1 184 202H72A16 16 0 0 1 56 186Z" fill="{p.main}"/>',
        f'<rect x="100" y="122" width="56" height="16" rx="8" fill="{p.deep}"/>',
        f'<circle cx="190" cy="186" r="36" fill="{p.accent}" stroke="{TILE}" stroke-width="10"/>',
        stroke("M173 187L185 199L207 175", TILE, 12, "round", "round"),
    ]


def msi_dropping_cube(p):
    v = cube(128, 152, 66)
    arrow = "M117 28H139V74H162L128 110L94 74H117Z"
    return cube_faces(v, p) + [
        f'<path d="{arrow}" fill="none" stroke="{TILE}" stroke-width="14" stroke-linejoin="round"/>',
        f'<path d="{arrow}" fill="{p.accent}"/>',
    ]


# --- Enigma.Launchpad -----------------------------------------------------------------------------

def launchpad_rocket(p):
    return [
        '<g transform="translate(6 -6) rotate(45 128 128)">',
        f'<path d="M94 126L66 156V190L94 170Z" fill="{p.shade}"/>',
        f'<path d="M162 126L190 156V190L162 170Z" fill="{p.shade}"/>',
        f'<path d="M128 34C153 52 164 84 164 120V170H92V120C92 84 103 52 128 34Z" fill="{p.main}"/>',
        f'<circle cx="128" cy="100" r="16" fill="{TILE}"/>',
        f'<path d="M106 180H150C150 198 142 210 128 226C114 210 106 198 106 180Z" fill="{p.accent}"/>',
        "</g>",
    ]


def launchpad_grid(p):
    out = []
    for row, y in enumerate((54, 108, 162)):
        for col, x in enumerate((54, 108, 162)):
            fill = p.accent if (row, col) == (0, 2) else p.main
            out.append(f'<rect x="{x}" y="{y}" width="40" height="40" rx="12" fill="{fill}"/>')
    return out


def launchpad_launch_tile(p):
    return [
        f'<rect x="56" y="56" width="64" height="64" rx="18" fill="{p.main}"/>',
        f'<rect x="56" y="136" width="64" height="64" rx="18" fill="{p.main}"/>',
        f'<rect x="136" y="136" width="64" height="64" rx="18" fill="{p.main}"/>',
        stroke("M144 112L194 62M156 60H196V100", p.accent, 18, "round", "round"),
    ]


# --- Enigma.MarkdownEditor ------------------------------------------------------------------------

# The Markdown mark (github.com/dcurtis/markdown-mark), in its 208 x 128 box: the M and the arrow.
MARK_M = "M30 98V30h20l20 25 20-25h20v68H90V59L70 84 50 59v39z"
MARK_ARROW = "M155 98l-30-33h20V30h20v35h20z"


def markdown_outline_mark(p):
    return [
        '<g transform="translate(34.4 70.4) scale(0.9)">',
        f'<rect x="5" y="5" width="198" height="118" rx="12" fill="none" stroke="{p.main}" stroke-width="12"/>',
        f'<path d="{MARK_M}" fill="{p.main}"/>',
        f'<path d="{MARK_ARROW}" fill="{p.accent}"/>',
        "</g>",
    ]


def markdown_split_mark(p):
    # The M on the left in a main block, the arrow on the right in an accent block.
    m_box, a_box, k = (30, 30, 80, 68), (125, 30, 40, 68), 0.86

    def place(path, box, cx):
        x, y, w, h = box
        return (f'<path d="{path}" fill="{TILE}" transform="translate({n(cx - (x + w / 2) * k)} '
                f'{n(128 - (y + h / 2) * k)}) scale({k})"/>')

    return [
        f'<path d="M50 72H146V184H50A18 18 0 0 1 32 166V90A18 18 0 0 1 50 72Z" fill="{p.main}"/>',
        f'<path d="M154 72H206A18 18 0 0 1 224 90V166A18 18 0 0 1 206 184H154Z" fill="{p.accent}"/>',
        place(MARK_M, m_box, 89),
        place(MARK_ARROW, a_box, 189),
    ]


def markdown_heading_page(p):
    return page(p) + [
        stroke("M93 90V126M109 90V126M80 101H122M80 115H122", p.accent, 8),
        f'<rect x="130" y="100" width="44" height="16" rx="5" fill="{p.deep}"/>',
        f'<rect x="82" y="142" width="92" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="82" y="164" width="76" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="82" y="186" width="56" height="12" rx="4" fill="{p.deep}"/>',
    ]


def markdown_split_view(p):
    return [
        f'<rect x="36" y="56" width="184" height="144" rx="18" fill="{p.main}"/>',
        f'<rect x="134" y="70" width="72" height="116" rx="8" fill="{p.light}"/>',
        f'<rect x="52" y="78" width="66" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="52" y="102" width="52" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="52" y="126" width="62" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="52" y="150" width="40" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="146" y="82" width="48" height="16" rx="5" fill="{p.accent}"/>',
        f'<rect x="146" y="110" width="48" height="10" rx="4" fill="{p.main}"/>',
        f'<rect x="146" y="130" width="36" height="10" rx="4" fill="{p.main}"/>',
        f'<rect x="146" y="150" width="44" height="10" rx="4" fill="{p.main}"/>',
    ]


# --- Enigma.TextEditor ----------------------------------------------------------------------------

def text_page_cursor(p):
    return page(p) + [
        f'<rect x="82" y="100" width="92" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="82" y="124" width="68" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="82" y="148" width="84" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="82" y="172" width="40" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="128" y="164" width="18" height="28" rx="3" fill="{p.accent}"/>',
    ]


def text_vim_window(p):
    return [
        f'<rect x="40" y="52" width="176" height="152" rx="16" fill="{p.main}"/>',
        f'<path d="M56 52H72V174H40V68A16 16 0 0 1 56 52Z" fill="{p.shade}"/>',
        f'<path d="M40 174H216V188A16 16 0 0 1 200 204H56A16 16 0 0 1 40 188Z" fill="{p.deep}"/>',
        f'<rect x="52" y="182" width="40" height="14" rx="7" fill="{p.accent}"/>',
        *(f'<rect x="50" y="{y + 2}" width="12" height="8" rx="3" fill="{p.main}"/>' for y in (72, 96, 120, 144)),
        f'<rect x="84" y="72" width="100" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="84" y="96" width="60" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="84" y="120" width="112" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="84" y="144" width="44" height="12" rx="4" fill="{p.deep}"/>',
        f'<rect x="150" y="88" width="16" height="28" rx="3" fill="{p.accent}"/>',
    ]


def text_braces_cursor(p):
    brace = ("M102 52H92A16 16 0 0 0 76 68V106A22 22 0 0 1 54 128A22 22 0 0 1 76 150V188A16 16 0 0 0 92 204H102"
             "M154 52H164A16 16 0 0 1 180 68V106A22 22 0 0 0 202 128A22 22 0 0 0 180 150V188A16 16 0 0 1 164 204H154")
    return [
        stroke(brace, p.main, 18),
        f'<rect x="116" y="98" width="24" height="60" rx="4" fill="{p.accent}"/>',
    ]


# --- Enigma.FileExplorer --------------------------------------------------------------------------

def explorer_listing(p):
    return [
        f'<path d="M60 60H98Q104 60 108 64L122 78H196A12 12 0 0 1 208 90V184A12 12 0 0 1 196 196H60A12 12 0 0 1 48 184V72A12 12 0 0 1 60 60Z" fill="{p.shade}"/>',
        f'<rect x="48" y="98" width="160" height="98" rx="12" fill="{p.main}"/>',
        f'<rect x="64" y="114" width="128" height="18" rx="5" fill="{p.deep}"/>',
        f'<rect x="64" y="138" width="128" height="18" rx="5" fill="{p.accent}"/>',
        f'<rect x="64" y="162" width="128" height="18" rx="5" fill="{p.deep}"/>',
    ]


def explorer_tree(p):
    return [
        stroke("M76 100V164A20 20 0 0 0 96 184H120M76 132H120", p.shade, 14),
        folder(44, 42, 72, 58, 30, 10, p.main),
        folder(120, 110, 88, 46, 34, 10, p.main),
        folder(120, 162, 88, 46, 34, 10, p.accent),
    ]


def explorer_search(p):
    return [
        f'<path d="M52 52H88Q94 52 98 56L110 68H172A12 12 0 0 1 184 80V168A12 12 0 0 1 172 180H52A12 12 0 0 1 40 168V64A12 12 0 0 1 52 52Z" fill="{p.shade}"/>',
        f'<rect x="40" y="88" width="144" height="92" rx="12" fill="{p.main}"/>',
        f'<circle cx="164" cy="160" r="52" fill="{TILE}"/>',
        f'<circle cx="164" cy="160" r="30" fill="{TILE}" stroke="{p.accent}" stroke-width="16"/>',
        stroke("M192 188L214 210", p.accent, 18, "round"),
    ]


def explorer_dual_pane(p):
    out = [f'<rect x="36" y="52" width="184" height="152" rx="18" fill="{p.main}"/>']
    for x, widths, lit in ((48, (60, 44, 52, 36), None), (132, (60, 60, 40, 50), 1)):
        out.append(f'<rect x="{x}" y="64" width="76" height="128" rx="9" fill="{p.deep}"/>')
        for i, w in enumerate(widths):
            out.append(f'<rect x="{x + 8}" y="{76 + i * 28}" width="{w}" height="14" rx="5" '
                       f'fill="{p.accent if i == lit else p.main}"/>')
    return out


def explorer_open_folder(p):
    return [
        folder(36, 50, 164, 146, 58, 12, p.shade),
        f'<rect x="64" y="72" width="116" height="92" rx="8" fill="{p.accent}"/>',
        f'<path d="M66 112H218L198 192H42Z" fill="{p.main}" stroke="{p.main}" stroke-width="12" stroke-linejoin="round"/>',
    ]


def explorer_folder_grid(p):
    return [folder(x, y, 68, 56, 26, 9, p.accent if (x, y) == (136, 62) else p.main)
            for y in (62, 138) for x in (52, 136)]


# --- Enigma.HardCopy ------------------------------------------------------------------------------

def qr(x, y, u, gap, fg, bg, accent):
    """A stylised QR code on a 7 x 7 grid of pitch u: three finder patterns three modules wide, a few
    data modules, and the alignment pattern in the bottom right corner, in the accent."""
    out = []
    f = 3 * u - gap
    for cx, cy in ((0, 0), (4, 0), (0, 4)):
        fx, fy = x + cx * u + gap / 2, y + cy * u + gap / 2
        out += [
            f'<rect x="{n(fx)}" y="{n(fy)}" width="{n(f)}" height="{n(f)}" rx="{n(f * 0.24)}" fill="{fg}"/>',
            f'<rect x="{n(fx + f * 0.18)}" y="{n(fy + f * 0.18)}" width="{n(f * 0.64)}" height="{n(f * 0.64)}" rx="{n(f * 0.14)}" fill="{bg}"/>',
            f'<rect x="{n(fx + f * 0.33)}" y="{n(fy + f * 0.33)}" width="{n(f * 0.34)}" height="{n(f * 0.34)}" rx="{n(f * 0.08)}" fill="{fg}"/>',
        ]
    m = u - gap
    for c, r in ((3, 0), (3, 2), (0, 3), (1, 3), (3, 3), (5, 3), (6, 3), (3, 4), (4, 4), (6, 4), (3, 6), (4, 6)):
        out.append(f'<rect x="{n(x + c * u + gap / 2)}" y="{n(y + r * u + gap / 2)}" width="{n(m)}" height="{n(m)}" '
                   f'rx="{n(m * 0.25)}" fill="{fg}"/>')
    a = 2 * u - gap
    out.append(f'<rect x="{n(x + 5 * u + gap / 2)}" y="{n(y + 5 * u + gap / 2)}" width="{n(a)}" height="{n(a)}" '
               f'rx="{n(a * 0.25)}" fill="{accent}"/>')
    return out


def hardcopy_qr_page(p):
    return [
        f'<path d="M74 44H158L194 80V200A12 12 0 0 1 182 212H74A12 12 0 0 1 62 200V56A12 12 0 0 1 74 44Z" fill="{p.light}"/>',
        f'<path d="M158 44V80H194Z" fill="{p.shade}"/>',
        *qr(84.25, 82, 12.5, 2.5, p.main, p.light, p.accent),
        f'<rect x="82" y="182" width="92" height="9" rx="4" fill="{p.main}"/>',
        f'<rect x="82" y="197" width="58" height="9" rx="4" fill="{p.main}"/>',
    ]


def hardcopy_qr(p):
    return qr(58, 58, 20, 4, p.main, TILE, p.accent)


def hardcopy_printer(p):
    return [
        f'<path d="M84 44H172A8 8 0 0 1 180 52V100H76V52A8 8 0 0 1 84 44Z" fill="{p.light}"/>',
        f'<rect x="40" y="92" width="176" height="92" rx="22" fill="{p.main}"/>',
        f'<rect x="64" y="148" width="128" height="12" rx="6" fill="{p.deep}"/>',
        f'<circle cx="190" cy="118" r="8" fill="{p.accent}"/>',
        f'<path d="M76 156H180V212A8 8 0 0 1 172 220H84A8 8 0 0 1 76 212Z" fill="{p.light}"/>',
        *qr(103, 166, 7, 1.5, p.main, p.light, p.accent),
    ]


def hardcopy_paper_key(p):
    return [
        f'<path d="M74 44H158L194 80V200A12 12 0 0 1 182 212H74A12 12 0 0 1 62 200V56A12 12 0 0 1 74 44Z" fill="{p.light}"/>',
        f'<path d="M158 44V80H194Z" fill="{p.shade}"/>',
        *key(p, "translate(128 116) scale(0.64) translate(-128 -128) ", p.light),
        f'<rect x="82" y="178" width="92" height="10" rx="4" fill="{p.main}"/>',
        f'<rect x="82" y="196" width="58" height="10" rx="4" fill="{p.main}"/>',
    ]


def hardcopy_scan(p):
    corners = ("M44 88V64A20 20 0 0 1 64 44H88M168 44H192A20 20 0 0 1 212 64V88"
               "M212 168V192A20 20 0 0 1 192 212H168M88 212H64A20 20 0 0 1 44 192V168")
    return [
        stroke(corners, p.main, 14, "round"),
        *qr(79, 79, 14, 3, p.main, TILE, p.main),
        f'<rect x="54" y="121" width="148" height="14" rx="7" fill="{p.accent}" stroke="{TILE}" stroke-width="6"/>',
    ]


def hardcopy_finder(p):
    u, gap, x0 = 33, 5, 48
    cell = lambda c, r, size=1, fill=p.main: (
        f'<rect x="{x0 + c * u}" y="{x0 + r * u}" width="{size * u - gap}" height="{size * u - gap}" '
        f'rx="{n((size * u - gap) * 0.24)}" fill="{fill}"/>')
    return [
        f'<rect x="48" y="48" width="94" height="94" rx="22" fill="{p.main}"/>',
        f'<rect x="64" y="64" width="62" height="62" rx="13" fill="{TILE}"/>',
        f'<rect x="78" y="78" width="34" height="34" rx="8" fill="{p.main}"/>',
        *(cell(c, r) for c, r in ((3, 0), (4, 1), (3, 2), (0, 3), (2, 3), (1, 4))),
        cell(3, 3, 2, p.accent),
    ]


# --- Enigma.Backup --------------------------------------------------------------------------------

def history_arrow(cx, cy, r, width, color):
    """A ring open on the left, turning back in time: its arrowhead at the upper end, pointing down."""
    at = lambda deg: (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))
    start, end = at(215), at(145)
    t = (math.sin(math.radians(215)), -math.cos(math.radians(215)))
    rad = (math.cos(math.radians(215)), math.sin(math.radians(215)))
    h = width * 4 / 3
    head = [(start[0] + h * rad[0], start[1] + h * rad[1]), (start[0] + h * 1.25 * t[0], start[1] + h * 1.25 * t[1]),
            (start[0] - h * rad[0], start[1] - h * rad[1])]
    return [stroke(f"M{n(start[0])} {n(start[1])}A{r} {r} 0 1 1 {n(end[0])} {n(end[1])}", color, width), poly(head, color)]


def backup_history(p):
    return history_arrow(128, 128, 72, 18, p.main) + [stroke("M128 92V128L154 146", p.accent, 16, "round", "round")]


def backup_zip(p):
    teeth = [f'<rect x="{112 if i % 2 == 0 else 128}" y="{50 + i * 13}" width="16" height="9" rx="3" fill="{p.deep}"/>'
             for i in range(6)]
    return page(p) + teeth + [
        f'<rect x="106" y="128" width="44" height="58" rx="12" fill="{p.accent}"/>',
        f'<rect x="119" y="152" width="18" height="22" rx="6" fill="{p.main}"/>',
    ]


def backup_vault(p):
    hub = (128, 122)
    spokes = "".join(f"M{hub[0]} {hub[1]}L{n(hub[0] + 32 * math.cos(math.radians(a)))} {n(hub[1] + 32 * math.sin(math.radians(a)))}"
                     for a in (-90, 30, 150))
    return [
        f'<rect x="62" y="190" width="28" height="22" rx="5" fill="{p.shade}"/>',
        f'<rect x="166" y="190" width="28" height="22" rx="5" fill="{p.shade}"/>',
        f'<rect x="40" y="40" width="176" height="160" rx="26" fill="{p.main}"/>',
        f'<rect x="58" y="58" width="140" height="124" rx="16" fill="{p.shade}"/>',
        f'<rect x="46" y="78" width="16" height="26" rx="5" fill="{p.deep}"/>',
        f'<rect x="46" y="136" width="16" height="26" rx="5" fill="{p.deep}"/>',
        f'<circle cx="{hub[0]}" cy="{hub[1]}" r="46" fill="{TILE}"/>',
        f'<circle cx="{hub[0]}" cy="{hub[1]}" r="32" fill="none" stroke="{p.accent}" stroke-width="10"/>',
        stroke(spokes, p.accent, 10, "round"),
        f'<circle cx="{hub[0]}" cy="{hub[1]}" r="11" fill="{p.accent}"/>',
    ]


def backup_locked_folder(p):
    return [
        f'<path d="M52 52H88Q94 52 98 56L110 68H172A12 12 0 0 1 184 80V168A12 12 0 0 1 172 180H52A12 12 0 0 1 40 168V64A12 12 0 0 1 52 52Z" fill="{p.shade}"/>',
        f'<rect x="40" y="88" width="144" height="92" rx="12" fill="{p.main}"/>',
        stroke("M154 162V146A18 18 0 0 1 190 146V162", TILE, 24),
        f'<rect x="140" y="156" width="64" height="52" rx="10" fill="{p.accent}" stroke="{TILE}" stroke-width="10"/>',
        stroke("M154 158V146A18 18 0 0 1 190 146V158", p.accent, 10),
        f'<circle cx="172" cy="178" r="7" fill="{TILE}"/>',
        f'<rect x="168.5" y="178" width="7" height="16" rx="3" fill="{TILE}"/>',
    ]


def backup_storage(p):
    band = lambda y: f"M56 {y}A72 22 0 0 0 200 {y}"
    return [
        f'<path d="M56 64V188A72 22 0 0 0 200 188V64Z" fill="{p.main}"/>',
        stroke(band(106) + band(148), TILE, 8),
        f'<ellipse cx="128" cy="64" rx="72" ry="22" fill="{p.accent}"/>',
    ]


def backup_shield(p):
    return [
        f'<path d="M128 40L198 64V122C198 166 170 196 128 214C86 196 58 166 58 122V64Z" fill="{p.main}" '
        f'stroke="{p.main}" stroke-width="12" stroke-linejoin="round"/>',
        *history_arrow(131, 124, 40, 12, TILE),
        stroke("M131 102V124L147 135", p.accent, 11, "round", "round"),
    ]


# --- Enigma.Licensing -----------------------------------------------------------------------------

def ribbon_tail(cx, cy, deg, length, half):
    a = math.radians(deg)
    d, o = (math.sin(a), math.cos(a)), (math.cos(a), -math.sin(a))
    at = lambda along, across: (cx + along * d[0] + across * o[0], cy + along * d[1] + across * o[1])
    return [at(0, -half), at(length, -half), at(length - 11, 0), at(length, half), at(0, half)]


def licensing_certificate(p):
    seal = (174, 158)
    tails = [ribbon_tail(*seal, deg, 62, 10) for deg in (-20, 20)]
    tail_paths = ["M" + "L".join(f"{n(x)} {n(y)}" for x, y in t) + "Z" for t in tails]
    return [
        f'<rect x="34" y="54" width="188" height="124" rx="14" fill="{p.main}"/>',
        f'<rect x="54" y="76" width="96" height="16" rx="5" fill="{p.deep}"/>',
        f'<rect x="54" y="106" width="110" height="10" rx="4" fill="{p.deep}"/>',
        f'<rect x="54" y="126" width="72" height="10" rx="4" fill="{p.deep}"/>',
        *(f'<path d="{d}" fill="none" stroke="{TILE}" stroke-width="10" stroke-linejoin="round"/>' for d in tail_paths),
        *(f'<path d="{d}" fill="{p.accent}"/>' for d in tail_paths),
        f'<circle cx="{seal[0]}" cy="{seal[1]}" r="30" fill="{p.accent}" stroke="{TILE}" stroke-width="10"/>',
        f'<circle cx="{seal[0]}" cy="{seal[1]}" r="17" fill="none" stroke="{TILE}" stroke-width="5"/>',
    ]


def key(p, transform, hole):
    return [
        f'<g transform="{transform}rotate(-45 128 128) translate(8 -6)">',
        f'<path d="M100 116H202V166H182V140H170V158H152V140H100Z" fill="{p.main}"/>',
        f'<circle cx="72" cy="128" r="40" fill="{p.accent}"/>',
        f'<circle cx="64" cy="128" r="15" fill="{hole}"/>',
        "</g>",
    ]


def licensing_key(p):
    return key(p, "", TILE)


def licensing_seal(p):
    points = [(128 + (86 if i % 2 == 0 else 74) * math.cos(math.pi * i / 12),
               128 + (86 if i % 2 == 0 else 74) * math.sin(math.pi * i / 12)) for i in range(24)]
    d = "M" + "L".join(f"{n(x)} {n(y)}" for x, y in points) + "Z"
    return [
        f'<path d="{d}" fill="{p.main}" stroke="{p.main}" stroke-width="12" stroke-linejoin="round"/>',
        f'<circle cx="128" cy="128" r="56" fill="{p.accent}"/>',
        stroke("M100 130L120 150L158 110", TILE, 18, "round", "round"),
    ]


def licensing_signed_page(p):
    return page(p) + [
        stroke("M90 92H80V140H90M166 92H176V140H166", p.deep, 8),
        f'<rect x="96" y="100" width="48" height="10" rx="4" fill="{p.deep}"/>',
        f'<rect x="96" y="122" width="62" height="10" rx="4" fill="{p.deep}"/>',
        stroke("M80 186C88 162 104 160 100 180C97 196 112 174 122 170C128 168 126 186 134 184C142 182 150 172 178 172",
               p.accent, 8, "round", "round"),
    ]


APPS = [
    {
        "key": "git-client", "prefix": "GC", "name": "Enigma.GitClient",
        "about": "The reference: GC-A1 is the current icon.",
        "shapes": [
            ("A", "Branch", "The current icon: a line of commits and a branch leaving its base.", git_branch),
            ("B", "Merge", "The branch leaves the base commit and merges back into the head.", git_merge),
            ("C", "Fork", "One commit forking into two lines, the new one ending on a ring.", git_fork),
            ("D", "History", "The history graph beside its commit rows, the branch's row lit.", git_history),
        ],
    },
    {
        "key": "msi", "prefix": "MSI", "name": "Enigma.Msi",
        "about": "Builds Windows MSI installers from one declarative profile.",
        "shapes": [
            ("A", "Taped cube", "An isometric package with the accent tape across its lid and down its side.", msi_taped_cube),
            ("B", "Checked box", "An archive box with its lid, and a validated build badge on its corner.", msi_checked_box),
            ("C", "Into the box", "An accent arrow dropping onto an isometric package.", msi_dropping_cube),
        ],
    },
    {
        "key": "launchpad", "prefix": "LP", "name": "Enigma.Launchpad",
        "about": "A launcher for applications, folders, links and documents.",
        "shapes": [
            ("A", "Rocket", "A rocket climbing to the top right, its flame in the accent.", launchpad_rocket),
            ("B", "App grid", "Nine launcher tiles, one of them lit.", launchpad_grid),
            ("C", "Launch tile", "Three shortcuts and a launch arrow in place of the fourth.", launchpad_launch_tile),
        ],
    },
    {
        "key": "markdown-editor", "prefix": "MD", "name": "Enigma.MarkdownEditor",
        "about": "Markdown notes as files, with vim keys and a live preview.",
        "shapes": [
            ("A", "Outline mark", "The Markdown mark: a framed M and its arrow, the arrow in the accent.", markdown_outline_mark),
            ("B", "Split mark", "The Markdown mark in two solid blocks, M and arrow cut out of them.", markdown_split_mark),
            ("C", "Heading page", "A page opening on a # heading, then its paragraph.", markdown_heading_page),
            ("D", "Split view", "Source on the left, the rendered preview on the right.", markdown_split_view),
        ],
    },
    {
        "key": "text-editor", "prefix": "TE", "name": "Enigma.TextEditor", "family": "B",
        "about": "A text editor in Vim's normal mode.",
        "shapes": [
            ("A", "Page and cursor", "The current icon: a page of text with the block cursor at the end.", text_page_cursor),
            ("B", "Vim window", "An editor with its line gutter, a block cursor and the mode in the status line.", text_vim_window),
            ("C", "Braces", "A block cursor between braces.", text_braces_cursor),
        ],
    },
    {
        "key": "file-explorer", "prefix": "FE", "name": "Enigma.FileExplorer",
        "about": "A file explorer with a keyboard-driven listing.",
        "shapes": [
            ("A", "Folder listing", "The current icon: a folder holding a listing, the cursor row in the accent.", explorer_listing),
            ("B", "Tree", "A folder and its two children, joined like the GitClient history graph.", explorer_tree),
            ("C", "Search", "A folder under a magnifying glass.", explorer_search),
            ("D", "Dual pane", "Two listings side by side, the cursor row lit in the right one.", explorer_dual_pane),
            ("E", "Open folder", "An open folder, a file rising out of it in the accent.", explorer_open_folder),
            ("F", "Folder grid", "Four folders in an icon view, one of them selected.", explorer_folder_grid),
        ],
    },
    {
        "key": "hardcopy", "prefix": "HC", "name": "Enigma.HardCopy",
        "about": "Backs up small critical files to paper, as printed QR codes.",
        "shapes": [
            ("A", "QR page", "A printed page carrying a QR code, its alignment block in the accent.", hardcopy_qr_page),
            ("B", "QR code", "The code alone, filling the tile.", hardcopy_qr),
            ("C", "Printer", "A printer handing out a page with a code on it.", hardcopy_printer),
            ("D", "Paper key", "A key printed on a page: the private key, kept on paper.", hardcopy_paper_key),
            ("E", "Scan", "A code in a camera viewfinder, the scan line in the accent: the recovery.", hardcopy_scan),
            ("F", "Finder", "A close-up on one corner of a code: its finder pattern, bold at any size.", hardcopy_finder),
        ],
    },
    {
        "key": "backup", "prefix": "BK", "name": "Enigma.Backup",
        "about": "Packs files into compressed, optionally encrypted archives, and restores them.",
        "shapes": [
            ("A", "History", "An arrow turning back round a clock, its hands in the accent.", backup_history),
            ("B", "Zipped page", "A page closed by a zipper, the pull in the accent.", backup_zip),
            ("C", "Vault", "A safe whose dial is in the accent, for the encrypted archive.", backup_vault),
            ("D", "Locked folder", "A folder under an accent padlock: the encrypted backup.", backup_locked_folder),
            ("E", "Storage", "A storage cylinder in three layers, the newest on top in the accent.", backup_storage),
            ("F", "Shield", "A shield carrying the history arrow and the clock's hands.", backup_shield),
        ],
    },
    {
        "key": "licensing", "prefix": "LIC", "name": "Enigma.Licensing",
        "about": "Signs software licenses and checks them.",
        "shapes": [
            ("A", "Certificate", "A certificate with its seal and ribbons in the accent.", licensing_certificate),
            ("B", "Key", "A key, its bow in the accent.", licensing_key),
            ("C", "Seal", "A rosette seal with a check in the accent: a verified license.", licensing_seal),
            ("D", "Signed envelope", "A JSON page signed at the bottom in the accent.", licensing_signed_page),
        ],
    },
]


# --- output ---------------------------------------------------------------------------------------

def svg(variant_id, title, body):
    inner = "\n".join("  " + line for line in body)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f"<!-- {variant_id}: {title} -->\n"
            '<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">\n'
            f"  {TILE_RECT}\n{inner}\n</svg>\n")


def write_icons():
    variants = []
    for app in APPS:
        folder_path = ROOT / app["key"]
        folder_path.mkdir(exist_ok=True)
        for old in folder_path.glob("*.svg"):
            old.unlink()
        for letter, title, _, draw in app["shapes"]:
            for p in PALETTES:
                variant_id = f'{app["prefix"]}-{letter}{p.number}'
                rel = f'{app["key"]}/{app["key"]}-{letter}{p.number}.svg'
                (ROOT / rel).write_text(svg(variant_id, f'{app["name"]}, {title}, {p.name}', draw(p)))
                variants.append(rel)
    return variants


def write_preview():
    e = html.escape
    legend = "".join(
        f'<div class="pal"><span class="num">{p.number}</span><b>{e(p.name)}</b>'
        + "".join(f'<i title="{role} {c}" style="background:{c}"></i>'
                  for role, c in (("main", p.main), ("shade", p.shade), ("deep", p.deep),
                                  ("accent", p.accent), ("light", p.light)))
        + "</div>" for p in PALETTES)

    family = "".join(
        f'<div class="fam"><span class="fam-label">{p.number} · {e(p.name)}</span><div class="dock">'
        + "".join(f'<figure><img src="{a["key"]}/{a["key"]}-{a.get("family", "A")}{p.number}.svg" alt="">'
                  f'<figcaption>{a["prefix"]}-{a.get("family", "A")}{p.number}</figcaption></figure>' for a in APPS)
        + "</div></div>" for p in PALETTES)

    sections = []
    for app in APPS:
        rows = []
        for letter, title, desc, _ in app["shapes"]:
            first = f'{app["key"]}/{app["key"]}-{letter}1.svg'
            sizes = "".join(f'<img src="{first}" width="{s}" height="{s}" alt="" title="{s} px">'
                            for s in (64, 48, 32, 24, 16))
            cells = "".join(
                f'<button class="cell" data-id="{app["prefix"]}-{letter}{p.number}" title="{e(p.name)}">'
                f'<img src="{app["key"]}/{app["key"]}-{letter}{p.number}.svg" alt="{app["prefix"]}-{letter}{p.number}">'
                f'<span>{app["prefix"]}-{letter}{p.number}</span></button>' for p in PALETTES)
            rows.append(f'<div class="row"><div class="meta"><h3><span class="letter">{letter}</span>{e(title)}</h3>'
                        f'<p>{e(desc)}</p><div class="sizes">{sizes}</div></div><div class="cells">{cells}</div></div>')
        sections.append(f'<section id="{app["key"]}"><header><h2>{e(app["name"])}</h2><p>{e(app["about"])}</p>'
                        f'</header>{"".join(rows)}</section>')

    nav = "".join(f'<a href="#{a["key"]}">{e(a["name"].removeprefix("Enigma."))}</a>' for a in APPS)
    page_html = PAGE.replace("{{LEGEND}}", legend).replace("{{FAMILY}}", family) \
        .replace("{{SECTIONS}}", "".join(sections)).replace("{{NAV}}", nav) \
        .replace("{{APPCOUNT}}", str(len(APPS))).replace("{{COUNT}}", str(sum(len(a["shapes"]) for a in APPS) * len(PALETTES)))
    (ROOT / "preview.html").write_text(page_html)


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Enigma App Icons</title>
<style>
  :root {
    --bg: #F7F6FB; --card: #FFFFFF; --text: #2E2A3A; --muted: #7A7590; --border: #E7E4F0;
    --pick: #3574F0; --dock: #ECEAF3;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #17161C; --card: #211F28; --text: #ECE9F5; --muted: #9C97B0; --border: #2F2C38;
      --pick: #9DC4F5; --dock: #2A2833;
    }
  }
  :root[data-theme="dark"] {
    --bg: #17161C; --card: #211F28; --text: #ECE9F5; --muted: #9C97B0; --border: #2F2C38;
    --pick: #9DC4F5; --dock: #2A2833;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 40px 16px 120px; background: var(--bg); color: var(--text);
    font: 15px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  main { max-width: 1240px; margin: 0 auto; }
  h1 { font-size: 28px; margin: 0 0 4px; letter-spacing: -0.01em; }
  h2 { font-size: 21px; margin: 0; letter-spacing: -0.01em; }
  h3 { font-size: 15px; margin: 0; display: flex; align-items: center; gap: 8px; }
  .lead { color: var(--muted); margin: 0 0 20px; max-width: 760px; }
  .top { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; justify-content: space-between; margin-bottom: 20px; }
  nav { display: flex; flex-wrap: wrap; gap: 6px; }
  nav a, .theme button {
    font: 13px system-ui, sans-serif; color: var(--text); text-decoration: none; background: var(--card);
    border: 1px solid var(--border); border-radius: 999px; padding: 5px 12px; cursor: pointer;
  }
  .theme { display: flex; gap: 6px; }
  .theme button[aria-pressed="true"] { border-color: var(--pick); color: var(--pick); }
  .legend { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 32px; }
  .pal {
    display: flex; align-items: center; gap: 6px; padding: 6px 12px 6px 6px; background: var(--card);
    border: 1px solid var(--border); border-radius: 999px; font-size: 13px;
  }
  .pal b { font-weight: 600; margin-right: 4px; }
  .pal i { width: 16px; height: 16px; border-radius: 50%; display: block; }
  .num {
    width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
    background: #1E1F22; color: #ECE9F5; font-size: 12px; font-weight: 600;
  }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 20px; padding: 20px; margin-bottom: 24px; }
  .family { display: grid; gap: 10px; }
  .fam { display: grid; grid-template-columns: 150px 1fr; align-items: center; gap: 12px; }
  .fam-label { font-size: 13px; color: var(--muted); }
  .dock {
    display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 14px; background: var(--dock);
    border-radius: 18px; width: fit-content;
  }
  .dock figure { margin: 0; display: grid; justify-items: center; gap: 2px; }
  .dock img, .dock svg { width: 64px; height: 64px; display: block; }
  .dock figcaption { font: 11px ui-monospace, monospace; color: var(--muted); }
  section header { margin-bottom: 8px; }
  section header p { margin: 2px 0 0; color: var(--muted); font-size: 14px; }
  .row { display: grid; grid-template-columns: 250px 1fr; gap: 20px; padding: 18px 0; border-top: 1px solid var(--border); }
  .row:first-of-type { border-top: 0; }
  .meta p { margin: 4px 0 12px; color: var(--muted); font-size: 13px; }
  .letter {
    width: 24px; height: 24px; border-radius: 7px; background: #1E1F22; color: #ECE9F5;
    display: grid; place-items: center; font-size: 13px;
  }
  .sizes { display: flex; align-items: end; gap: 10px; }
  .sizes img { display: block; }
  .cells { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
  .cell {
    all: unset; cursor: pointer; display: grid; justify-items: center; gap: 4px; padding: 8px 4px 6px;
    border-radius: 14px; border: 2px solid transparent;
  }
  .cell:hover { background: var(--bg); }
  .cell:focus-visible { outline: 2px solid var(--pick); outline-offset: 2px; }
  .cell img { width: 100%; max-width: 128px; aspect-ratio: 1; display: block; }
  .cell span { font: 12px ui-monospace, monospace; color: var(--muted); }
  .cell.picked { border-color: var(--pick); }
  .cell.picked span { color: var(--pick); font-weight: 700; }
  .bar {
    position: fixed; left: 16px; right: 16px; bottom: 16px; max-width: 1240px; margin: 0 auto;
    background: var(--card); border: 1px solid var(--border); border-radius: 16px; padding: 10px 14px;
    display: flex; gap: 12px; align-items: center; box-shadow: 0 8px 30px rgba(0,0,0,.18);
  }
  .bar output { flex: 1; font: 13px ui-monospace, monospace; color: var(--muted); overflow-wrap: anywhere; }
  .bar button {
    font: 13px system-ui, sans-serif; border: 1px solid var(--border); background: var(--bg); color: var(--text);
    border-radius: 10px; padding: 6px 12px; cursor: pointer; white-space: nowrap;
  }
  @media (max-width: 860px) {
    .row { grid-template-columns: 1fr; gap: 10px; }
    .cells { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .fam { grid-template-columns: 1fr; gap: 4px; }
    .dock img, .dock svg { width: 44px; height: 44px; }
  }
</style>
</head>
<body>
<main>
  <h1>Enigma app icons</h1>
  <p class="lead">{{COUNT}} variants for {{APPCOUNT}} applications, each on the Enigma.GitClient tile (#1E1F22, a 240-unit square
  rounded by 48). A variant is named by application, shape letter and palette number: <code>MSI-A1</code> is the
  first Msi shape in the Classic palette. Click variants to pick them, then copy the list into your feedback.</p>

  <div class="top">
    <nav>{{NAV}}</nav>
    <div class="theme" role="group" aria-label="Page background">
      <button data-theme="light">Light desktop</button><button data-theme="dark">Dark desktop</button>
    </div>
  </div>

  <div class="legend">{{LEGEND}}</div>

  <div class="card">
    <h2>Family</h2>
    <p class="lead" style="margin:2px 0 14px">One shape of every application, one palette per row: GC-A1 is the current GitClient icon.</p>
    <div class="family">{{FAMILY}}</div>
  </div>

  {{SECTIONS}}
</main>

<div class="bar">
  <output id="picks">Nothing picked yet: click a variant.</output>
  <button id="copy">Copy</button><button id="clear">Clear</button>
</div>

<script>
  const KEY = "enigma-app-icons-picks";
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return []; } };
  const save = v => { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch {} };
  let picks = load();
  const out = document.getElementById("picks");

  function render() {
    document.querySelectorAll(".cell").forEach(c => c.classList.toggle("picked", picks.includes(c.dataset.id)));
    out.textContent = picks.length ? "Picked: " + picks.join(", ") : "Nothing picked yet: click a variant.";
  }
  document.querySelectorAll(".cell").forEach(c => c.addEventListener("click", () => {
    const id = c.dataset.id;
    picks = picks.includes(id) ? picks.filter(p => p !== id) : [...picks, id];
    save(picks); render();
  }));
  document.getElementById("clear").addEventListener("click", () => { picks = []; save(picks); render(); });
  document.getElementById("copy").addEventListener("click", async () => {
    const text = picks.join(", ");
    try { await navigator.clipboard.writeText(text); } catch { prompt("Copy the picks:", text); }
  });

  const root = document.documentElement;
  const buttons = document.querySelectorAll(".theme button");
  function setTheme(t) {
    if (t) root.dataset.theme = t; else delete root.dataset.theme;
    buttons.forEach(b => b.setAttribute("aria-pressed", String(b.dataset.theme === t)));
    try { t ? localStorage.setItem(KEY + "-theme", t) : localStorage.removeItem(KEY + "-theme"); } catch {}
  }
  buttons.forEach(b => b.addEventListener("click", () => setTheme(root.dataset.theme === b.dataset.theme ? null : b.dataset.theme)));
  let saved = null; try { saved = localStorage.getItem(KEY + "-theme"); } catch {}
  setTheme(saved);
  render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    count = len(write_icons())
    write_preview()
    print(f"{count} icons and preview.html written to {ROOT}")
