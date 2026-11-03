# FEATURE-BF15-PHASE01 — Fit masters into final3

## Summary

`export.py` has a third target, `final3`: the tile-free icons of `final2/`, each master drawn in one
`<g transform="translate(..) scale(..)">` that scales it until its longest side spans the live area
`LIVE = (16, 240)` (87.5 % of the frame) and centres it. The transform comes from the drawing's bounds as
`rsvg-convert` renders them at 1024 px (pixels at least half covered), read by a stdlib PNG reader in
`export.py` — never from coordinates. In this phase every `final3` frame, 16 to 256 px, comes from the
fitted master; PHASE02 adds the grid-drawn small drawings.

Scales: git-client 1.2444, msi 1.2727, launchpad 1.4452, markdown-editor 1.1852, text-editor 1.2727,
file-explorer 1.1915, hardcopy 1.6471, backup 1.3333, licensing 1.1915.

## Files/modules touched

- Modified: `Apps/export.py`
- Created: `Apps/final3/<app>/` for the nine applications — 9 SVG masters, 90 PNGs, 9 `.ico`
- Created: `docs/done/FEATURE-BF15-PHASE01.md`; modified: `docs/roadmap.md`, `docs/plan/FEATURE-BF15.md`

## Deviations & follow-ups

- **Renderer.** `rsvg-convert` is not installed and the draft forbids installing anything without asking.
  The PNGs (and the 1024 px bounds renders) were produced by running `export.py` with its `rsvg-convert`
  calls served by headless Microsoft Edge 156 (scratchpad driver: the `<svg>` inlined at the frame size,
  transparent background, device scale 1). Edge's analytic anti-aliasing behaves like librsvg's (an edge
  shared by two shapes blends like librsvg, not like the 16× supersampled resvg used for `final2/`).
  `export.py` still calls `rsvg-convert`; re-running it where librsvg exists re-renders the PNGs
  byte-differently but alike, and may move a transform's last decimals by the renderers' AA difference.
- `TARGETS` values became `(tile, fill)` pairs; `export()` returns `(variant, folder, scale)` and the CLI
  prints the scale for `final3`. Running `export.py` with no argument now writes all three targets.
- Follow-up (unchanged from FEATURE-8F6B): `generate.py` writes `preview.html` without
  `encoding="utf-8"`; not touched.

## Build/test evidence

No build step or test suite; nothing to build or test. Checks by scratchpad scripts (not committed):

- **Run baseline** (run branch `feature/2026-11-03-frame-filling-icons` at `dbcf03a`, before this dev's
  branch): in a scratch copy of `Apps/`, `generate.py` and `export.py final final2` (renderer stubbed)
  regenerated all 264 committed SVGs — 234 variants, 15 `final/`, 15 `final2/` — byte-identically.
  No pre-existing failure to carry.
- **AC1:** `final3/` holds the file set of `final2/` minus the `-small.svg` files (as planned for PHASE01).
- **AC2:** each master's body is `final2`'s, line for line, inside one outer fit group; no `#1E1F22`,
  `mask` or `clipPath`.
- **AC3:** longest side of the alpha > 32 box = 87.5 % ± 1 px in all 90 frames: 14 at 16 px, 21–22 at
  24, 28 at 32, 36 at 40, 42 at 48, 224 at 256.
- **AC4:** left/right and top/bottom margins differ by ≤ 1 px in all 90 frames.
- **AC5:** 9 `.ico`, 10 entries each (16→256, 1 plane, 32 bpp, PNG), each byte-equal to its folder PNG.
- **AC6:** after the change the 264 SVGs still regenerate byte-identically; `git status` shows only
  `Apps/export.py`, `Apps/final3/` and the `docs/` records.
- **AC7:** `python export.py final4` exits 1: `unknown target final4; expected any of: final, final2, final3`.
- Looked at the 256 px hardcopy and launchpad renders: holes cut, nothing clipped.

## Decisions taken at build time

| Question | Chosen | Why | Alternatives rejected |
|---|---|---|---|
| Where the small drawings are bypassed for `final3` | `export()` drops `small` when the target fills, with a comment | One line PHASE02 replaces with the grid-drawn table | An empty placeholder table now |
| Number format in the transform | 4 decimals (`decimals()`) | `generate.n`'s 2 decimals would shift a 256 px edge by up to ~0.8 unit | `n()` |
| Bounds threshold | alpha ≥ 128 at 1024 px | The edge position within ±1/8 unit, whatever the AA | alpha > 0 (overstates by up to one pixel) |
| Speed of the PNG reader | Plain per-byte unfiltering | Nine 1024 px reads per export; the whole `final3` export, Edge renders included, took about a minute here | A faster, harder-to-read decoder |
| Documentation sweep | No edit: no README/CHANGELOG/CLAUDE.md; the `export.py` docstring was updated in this dev | — | — |
