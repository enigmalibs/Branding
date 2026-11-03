# FEATURE-8F6B — Tile-free app icons in Apps/final2

## Summary

`Apps/final2/` holds the nine chosen icons of `Apps/final/` without the dark rounded tile: same shapes,
colours, sizes and positions; same files (SVG master, small SVG, PNG frames 16–256 px, `.ico`).
Where a drawing painted in the tile's colour to fake a hole or a gap — the GitClient ring, the rocket's
window, the QR finder holes, the gaps round the licence seal — those parts are now real cut-outs, so the
desktop shows through. Put back on the tile, every `final2` icon renders as its `final` twin.

`python3 Apps/export.py` now writes both `final/` (unchanged) and `final2/`; `python3 Apps/export.py final2`
writes only the latter.

## Files/modules touched

- Modified: `Apps/export.py`, `Apps/generate.py`
- Created: `Apps/final2/<app>/` for backup, file-explorer, git-client, hardcopy, launchpad, licensing,
  markdown-editor, msi, text-editor — 15 SVGs, 90 PNGs, 9 `.ico`
- Created: `docs/done/FEATURE-8F6B.md`; modified: `docs/roadmap.md`, `docs/plan/FEATURE-8F6B.md`

## Deviations & follow-ups

- **Deviation — where the cut geometry lives.** The plan put tile-free copies of the four affected
  masters in `export.py`. They are instead a `cut=True` mode of the drawings themselves (`git_branch`,
  `launchpad_rocket`, `hardcopy_qr`, `licensing_certificate` in `generate.py`; `hardcopy_small`,
  `licensing_small` in `export.py`), so a later tweak to a shape reaches both targets. `export.tile_free`
  asks for `cut=True` only when a drawing paints in the tile's colour, and fails if the cut one still does.
  Geometry helpers added to `generate.py`: `pt`, `circle_d`, `rounded_rect_d`, `rounded_rect_outline`,
  `polygon_outline`, `subtract_circle`. Default output is byte-identical (see evidence).
- **Deviation — renderer.** `rsvg-convert` is not installed here. The PNGs were rendered by running
  `export.py` with its `rsvg-convert` calls served by resvg 0.48.1 (resvg-py 0.5.0, scratchpad venv), each
  frame drawn 16× larger and box-filtered down. `export.py` itself still calls `rsvg-convert`. Measured
  on `final/`: the same edge coverage as librsvg, except where two shapes share an edge, which librsvg
  blends with the colour underneath (e.g. 74 vs the exact 55 in a red channel); without the tile that
  blend would be a faint halo, so the exact result is preferable. Re-running `python3 Apps/export.py final2`
  where `rsvg-convert` exists re-renders the PNGs with librsvg, looking the same but differing byte-wise.
- Follow-up: `generate.py` writes `preview.html` without `encoding="utf-8"`. On Windows the `·` becomes
  cp1252 (pre-existing, seen at baseline; not touched).
- Follow-up: now that the tile is gone, the glyphs could be enlarged to fill more of the 256-unit frame.
  Also, the MSI cube's light top face (`#D9E5FC`) has little contrast on white desktops. Both left as the
  draft asked ("shapes and colours exactly").

## Build/test evidence

No build step or test suite in this repository. The criteria were checked by scratch scripts (not committed):

- **Baseline** (run branch at `2e50b27`, before the dev branch): in a scratch copy, `generate.py` regenerated
  all 234 variant SVGs byte-identically (`preview.html` differs only by the encoding follow-up above).
  `export.py` regenerated the 15 `final/` SVGs byte-identically. No warnings or failures to carry.
- **AC1:** `final2/` has exactly the file set of `final/` (`diff` of both trees' file lists: none).
- **AC2:** `grep` for `1E1F22`, `<mask`, `clipPath` and the tile rect in `final2/*/*.svg`: none.
- **AC3:** each `final2` SVG with the tile re-inserted vs its `final` twin, rendered at 512 px:
  max channel diff 0–3 for 13 SVGs. Licensing master and small reach 10/255 on 0.135 % and 0.109 % of
  pixels, along the cut circle's anti-aliased edge (all < 0.5 %).
- **AC4:** 90 PNGs, all RGBA; alpha 0 at the four corners and four edge midpoints; no opaque pixel within
  6 levels of `#1E1F22`. Contact sheet checked on white, light grey, dark and checkerboard backgrounds.
- **AC5:** 9 `.ico` files: 10 entries each (16…256, the 256 stored as 0, 1 plane, 32 bpp), each entry the
  folder's PNG byte for byte.
- **AC6:** after the change, the 234 variants and the 15 `final/` SVGs still regenerate byte-identically.
  `git status` shows no change under `Apps/final/` or the variant folders.
- `python3 export.py final3` exits 1 with `unknown target final3; expected any of: final, final2`.

## Decisions taken at build time

| Question | Chosen | Why | Alternatives rejected |
|---|---|---|---|
| Where the cut-out geometry lives | `cut=True` on each affected drawing | One function per shape: `final/` and `final2/` cannot drift apart | Separate copies in `export.py` (the plan's wording) |
| GitClient ring's hole | `fill="none"`, main line starts at y 83.5 (the ring stroke's centre line) | The line no longer shows through the hole; its top edge stays hidden under the stroke at every x | A mask over the line |
| Licence seal gap | Certificate and tails cut by the r 35 circle (r 48 small); seal as even-odd disc 25 / ring 19.5–14.5 | Exactly the area the tile-coloured strokes covered; the tails' own tile outline lay only on the tile, so it needs no cut | Offsetting every tail outline (no visible effect) |
| Supersampling factor of the stand-in renderer | 16× | Calibrated on `final/`; 4× left uneven coverage at 20–96 px | Plain resvg (coarse 1/16 AA, edges up to 64/255 off) |
| SVG header of `final2` files | "application icon without the tile", regenerate with `export.py final2` | Says what the file is and how to rebuild only it | Keeping `final/`'s wording |
| Documentation sweep | No edit: the repo has no README/CHANGELOG/CLAUDE.md; `export.py`'s docstring was updated in this dev | — | — |
