# FEATURE-BF15 — Frame-filling app icons in Apps/final3

**Status:** TODO
**Type:** FEATURE
**Branch:** feature/feature-bf15-phase01-fit-masters, feature/feature-bf15-phase02-small-drawings
**Run:** feature/2026-11-03-frame-filling-icons

## Objective

Create `Apps/final3/`: the nine tile-less application icons of `Apps/final2/`, with the artwork filling
the frame, so they no longer look half-size in the Windows taskbar. Every drawing — master and small —
spans the live area 16..240 of the 256-unit view box on its longest side (87.5 % of the frame) and is
centred, so the 32 px and 40 px frames match in size.

## Context & constraints

- `final2/` drawings keep the margin they had inside the tile: their visible box fills 53–83 % of the
  frame edge (launchpad 60 %, hardcopy 54 % from 40 px up), the master less than the small drawing, so the
  icon shrinks on 150–200 % displays and jumps in size between the 32 px and 40 px frames.
- `export.py` writes `final/` (tile) and `final2/` (tile-free; `tile_free` swaps in `cut=True` drawings).
  The `.ico` writer (10 PNG frames, 16–256 px, smallest first) is correct and stays as it is.
- `final/`, `final2/`, the variants in `Apps/<app>/` and the behaviour of `generate.py` must not change;
  `export.py` must still emit the `final`/`final2` SVG text byte-identically.
- `rsvg-convert`, Pillow and resvg are not installed; the draft says to install nothing without asking.
  Microsoft Edge 156 is installed and renders SVG headless with a transparent background.
- No build step or test suite in this repository; verification is by measurement scripts (scratchpad).
- Working tree is CRLF via `core.autocrlf=true`; files written by Python on Windows are fine.

## Design

- `LIVE = (16, 240)` — one constant for the live area. A target is `(tile, fit)`:
  `final` (tile, no fit), `final2` (no tile, no fit), `final3` (no tile, fit). No argument → all three.
- **Masters (fit):** the final2 tile-free body, wrapped in `<g transform="translate(tx ty) scale(s)">`.
  `s` and `t` come from the body's visible bounds, measured by rendering it with `rsvg-convert` at
  1024 px and reading the alpha channel (stdlib PNG reader in `export.py`, threshold alpha ≥ 128):
  `s = 224 / longest side`, bounds centre → (128, 128). Never estimated from coordinates.
- **Small drawings (fit):** new tile-free functions in `export.py`, drawn directly on the live area with
  straight edges on the 16-unit grid (1 px at 16 px, 2 px at 32 px) — never transformed. Apps without a
  small drawing (msi, launchpad, file-explorer) use the fitted master for every frame.
- **Weight:** a drawing that paints < 25 % of its 24 px frame gets heavier strokes / larger nodes in its
  final3 small drawing (git-client expected).
- **Rendering here:** a scratchpad driver runs `export.py` with its `rsvg-convert` calls served by headless
  Edge (inline SVG at the frame size, transparent background, device scale 1). `export.py` keeps calling
  `rsvg-convert`.

## Phases

### PHASE01 — Fit masters into final3

**Status:** TODO

Steps:
1. `export.py`: `LIVE`; the `(tile, fit)` target table with `final3`; `png_alpha` (stdlib PNG decode),
   `visible_bounds(svg)` (render at 1024 px to a temp dir, alpha ≥ 128 box in view-box units,
   `ValueError` when nothing is visible) and `fit(body)` (the `<g transform>` wrapper, 4-decimal numbers).
2. `export()`: a fit target fits the master and, in this phase, uses it for every frame; SVG header comments
   name final3 and the command `python3 Branding/Apps/export.py final3`; the printed line adds the scale.
3. Docstring describes `final3`.
4. Render `final3/` through the Edge driver; verify; write `docs/done/FEATURE-BF15-PHASE01.md`.

Acceptance criteria:
1. `Apps/final3/<app>/` for the nine apps: `<stem>.svg`, `png/<stem>-{16,20,24,32,40,48,64,96,128,256}.png`,
   `<stem>.ico`.
2. Each master is the final2 body inside one `<g transform="translate(..) scale(..)">`; no `#1E1F22`,
   `mask` or `clipPath`.
3. Size: in every frame the box of pixels with alpha > 32 has its longest side at 87.5 % of the frame
   ± 1 px (14, 17.5, 21, 28, 35, 42, 56, 84, 112, 224).
4. Centring: left/right margins differ by ≤ 1 px, top/bottom likewise, in every frame.
5. Each `.ico`: 10 PNG entries, 16→256, smallest first, each byte-equal to its folder's PNG.
6. Regression: in a scratch copy, `export.py` writes the `final`/`final2` SVGs byte-identical to the
   committed ones and `generate.py` the variants byte-identical; `git diff main --stat` touches only
   `Apps/export.py`, `Apps/final3/` and `docs/`.
7. `python export.py final4` exits 1 naming `final, final2, final3`.

### PHASE02 — Grid-drawn small icons

**Status:** TODO

Steps:
1. Six final3 small drawings in `export.py` — git-client, markdown-editor, text-editor, hardcopy, backup,
   licensing — each the design of its current small drawing re-laid on 16..240: longest side spans the
   live area, centred, every horizontal/vertical edge on a multiple of 16, tile-free (real cut-outs).
2. Fit targets use them for the 16–32 px frames and write `<stem>-small.svg` (32×32, header naming final3).
3. Weight: measure the 24 px frames; thicken the git-client (strokes, node radii) — or any other below 25 %.
4. Regenerate `final3/`; verify; comparison sheet and measurement table; write the done doc.

Acceptance criteria:
1. `final3/` has exactly the file set of `final2/` (file-list diff empty).
2. Size and centring as PHASE01, every frame of every app.
3. No jump: the 32 px and 40 px frames' fill (longest side / frame) within 3 percentage points.
4. Sharpness: in the small SVGs every `rect` x/y/width/height and every H/V path coordinate is a multiple
   of 16 (corner radii, arcs and diagonals excepted); at 16 and 32 px, edges formed by straight lines are
   whole pixels — no half-covered row or column along them.
5. Weight: every app paints ≥ 25 % of its 24 px frame (mean alpha).
6. Regression as PHASE01 criterion 6.
7. Report: final2 vs final3 table at 24 and 48 px (box, fill, painted area); an HTML comparison sheet in the
   scratchpad (16, 24, 32, 48 px at 1:1 on light and dark); 16 px legibility notes in the done doc.

## Out of scope

- Changing `final/`, `final2/`, the variants, `preview.html`, `generate.py`, colours or contrast.
- New small drawings for msi, launchpad, file-explorer; thickening any master.
- Installing `rsvg-convert` or any renderer; adopting the icons in the applications.

## Decisions taken autonomously

| Question | Chosen | Why | Alternatives rejected |
|---|---|---|---|
| Renderer without `rsvg-convert` | Headless Edge behind a scratchpad driver; `export.py` keeps `rsvg-convert` | Already installed: honours "install nothing without asking"; analytic AA like librsvg | pip-installing resvg into a venv (an install); Firefox (no transparent screenshots) |
| Draft's "Don't commit" vs `/vibe` | Commit only on the run and dev branches | `main` untouched; the user reviews `main...run` and merges — the intent of the constraint | Leave everything uncommitted (breaks the run's resumability and per-dev review) |
| Phasing | Two phases: fitted masters, then grid-drawn small drawings | Each a reviewable commit, each verifiable alone | One dev (code + 6 drawings + 2 asset sets in one commit) |
| How to measure master bounds | Render via `rsvg-convert` at 1024 px, alpha ≥ 128 box, stdlib PNG reader in `export.py` | The draft's method; ¼-unit precision; no dependency | Bounds from coordinates (the draft forbids it); caching measured values (stale on edits) |
| Where small drawings live | New functions in `export.py` beside the final2 ones | final2's stay untouched; same file as their siblings | Parameterising the existing ones (risks final2 output) |
| No-argument run | Writes all three targets | Consistent with the existing "no argument → every target" | Keeping it at final + final2 |
| Thicken the git-client master? | No — only its small drawing | The 24 px frame comes from the small drawing; the draft keeps masters as final2's | Thickening both |
| Centring | Bounds centre to (128, 128) | Measurable, as the acceptance checks require | Optical offsets |
| Scope check ("only export.py and final3/") | Also allow the run's `docs/` records | The workflow's own roadmap, plan and done files | — |
| Small SVG size attribute | 32×32 like final2 | Same file contract as final2 | 256 |
