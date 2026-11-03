# FEATURE-8F6B — Tile-free app icons in Apps/final2

**Status:** DONE
**Type:** FEATURE
**Branch:** feature/feature-8f6b-tile-free-icons
**Run:** feature/2026-11-02-tile-free-app-icons

## Objective

Create `Apps/final2/` with the nine chosen application icons of `Apps/final/` — the same shapes, colours,
sizes and positions — without the dark rounded tile (`#1E1F22`, 240 units rounded by 48) behind them:
an SVG master, the small SVG where `final/` has one, PNG frames 16 to 256 px and an `.ico` per application.

## Context & constraints

- `Apps/export.py` writes `final/` from the shapes in `Apps/generate.py`; every SVG starts with
  `generate.TILE_RECT`, and six drawings also paint in the tile colour to fake a hole or a gap:
  - git-client master — the open ring of the top commit (`fill=TILE`, the main line runs under it);
  - launchpad master — the rocket window;
  - hardcopy master and small — the hole of the three QR finder patterns;
  - licensing master and small — the gap ring round the seal (`stroke=TILE`), the outline of the ribbon
    tails, and (master only) the thin ring inside the seal.
  Removing only the tile rect would leave these as dark marks on a light desktop.
- `final/` and the 150 variants under `Apps/<app>/` are not to change; `python3 export.py` must still
  write `final/` byte-identically.
- `rsvg-convert`, which `export.py` calls, is not installed on this machine.
- Working tree is CRLF via `core.autocrlf=true`, index LF: files written by Python on Windows are fine.

## Design

- `export.py` gains a second target: `python3 export.py [final] [final2]` (no argument → both).
  `final` is unchanged. `final2` writes the same tree under `final2/` with `document(..., tile=False)`
  and, for the six drawings above, a tile-free replacement whose knockouts are real cut-outs:
  - git-client: the ring keeps `fill="none"`; the main line starts inside the ring's stroke (y 83.5)
    instead of its centre, so the hole stays empty.
  - launchpad: the window becomes an even-odd hole in the rocket body.
  - hardcopy: each finder's outer and inner squares become one even-odd path (via a backward-compatible
    `bg=None` mode of `generate.qr` and a `rounded_rect_d` path helper in `generate.py`).
  - licensing: the certificate body and the ribbon tails are cut by the seal's gap circle with exact
    path geometry (lines and arcs); the seal is an even-odd disc (and, in the master, ring).
- No SVG masks or clip paths: the originals use none, and plain paths survive every SVG consumer.
- Each `final2` SVG composited over `TILE_RECT` must render as its `final` twin.

## Steps (single phase)

1. `generate.py`: add `rounded_rect_d(x, y, w, h, r)`; let `qr(..., bg=None)` cut the finder hole
   instead of painting it. Existing calls keep passing a colour, so the variants are unchanged.
2. `export.py`: `document(..., tile=True)`; a `subtract_circle` helper (boundary of lines and arcs minus
   a circle, exactly two crossings, else `ValueError`); the six tile-free drawings; a target table
   (`final`, `final2`) with CLI selection; docstring and SVG header comments updated for `final2`.
3. Render `final2/` (here through a resvg stand-in for `rsvg-convert`, see decisions).
4. Verify the acceptance criteria with scratch scripts; record the evidence in `docs/done/FEATURE-8F6B.md`.

## Acceptance criteria

1. `Apps/final2/<app>/` exists for the nine applications with exactly the file set of `Apps/final/<app>/`
   (SVG master, small SVG where `final/` has one, `png/<stem>-{16,20,24,32,40,48,64,96,128,256}.png`,
   `<stem>.ico`).
2. No `final2` SVG contains the tile rect or the colour `#1E1F22`, nor `mask`/`clipPath` elements.
3. Every `final2` SVG composited over the tile renders like its `final` twin (same renderer, 512 px):
   no pixel differs by more than an anti-aliasing step except along cut edges, under 0.5 % of pixels.
4. Every `final2` PNG has a transparent background (alpha 0 at the tile's former corners and margins)
   and no opaque `#1E1F22`-coloured pixel.
5. Each `.ico` holds the ten PNG frames of its folder, smallest first, unchanged.
6. `Apps/final/` and the variant SVGs are byte-identical before and after (re-running `generate.py` in a
   scratch copy yields no diff); `export.py` still emits the `final` SVGs byte-identically.

## Out of scope

- Changing `Apps/final/`, the variants, `preview.html` or any shape, colour or size.
- Enlarging the glyphs to fill the frame now that the tile is gone.
- Light-desktop contrast tuning (e.g. the MSI cube's light top face).
- Adopting the new icons in the applications.

## Decisions taken autonomously

| Question | Chosen | Why | Alternatives rejected |
|---|---|---|---|
| What becomes of the tile-coloured marks (ring, window, finder holes, seal gaps)? | Real transparent cut-outs | They exist to show the tile through; cut out, the icon composited on the tile is pixel-identical to `final/`, and on any other desktop shows that desktop | Keep them `#1E1F22` — dark blots on light desktops, i.e. remnants of the tile |
| Rescale the glyphs now that the frame is empty? | No — same size and position | "The shapes … are exactly what I want" | Enlarge to fill the frame — a visible change not asked for; listed as a follow-up |
| How to produce `final2/`? | A `final2` target in `export.py` | Regenerable like `final/`, one source of truth for the drawings | A separate script (duplicated pipeline); hand-edited SVGs (not regenerable) |
| How to build the cut-outs? | Exact path geometry, even-odd holes | Same SVG feature set as the originals; robust in Avalonia, design tools, icon converters | SVG `<mask>` / `clip-path` — shorter code, weaker support outside browsers |
| Touch `generate.py`? | Only an opt-in `qr(bg=None)` mode and a path helper | Reuses the QR layout instead of duplicating it; variants unchanged | Copy `qr()` into `export.py` |
| `final2/` layout and names | Mirror `final/` exactly | Drop-in replacement for `final/` | `-transparent` suffixes — breaks drop-in use |
| Rendering here without `rsvg-convert` | Run `export.py` with its `rsvg-convert` call served by resvg 0.48 (16× supersampled, box-filtered) from a scratchpad venv; `export.py` itself keeps `rsvg-convert` | Calibrated on `final/`: same coverage as librsvg; differs only where two shapes share an edge, where librsvg bleeds the lower colour — the exact result is the better one on transparency | Plain resvg (coarse 1/16 AA, uneven edges at 16–24 px); installing librsvg system-wide (no MSYS2 here, outward change); adding a renderer dependency to the project |
| Phasing | One dev | ~150 lines of code plus generated assets: one reviewable commit | Splitting code and generated assets — neither half verifiable alone |
