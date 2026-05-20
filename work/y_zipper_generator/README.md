# Experimental Y-Zipper Generator

This project generates STL files for a short, printable, parametric Y-zipper-inspired FDM test coupon: three ribbed flexible strips, a simplified latch edge, a three-way guide/slider, and a closed triangular beam preview.

It is **not** the official MIT/CSAIL Y-Zipper model. The current latch is a simplified segmented bead and C-clip, not a faithful ball-node/socket mechanism.

## Quick Start

```bash
python -m pip install -e .[dev]
python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/demo_loose
```

Legacy wrapper:

```bash
python y_zipper_generator.py --part all --out output/legacy_test --teeth 8
```

Dry-run without writing STL files:

```bash
python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --dry-run
```

## Dependencies

- Python 3.10+
- `numpy`
- `trimesh`
- `pytest` for tests

OpenSCAD is optional. The extracted `y_zipper_generator_v0/y_zipper_generator.scad` is retained as a secondary v0 reference, not the authoritative generator.

## Parts

- `strip`: one TPU-oriented flexible strip with ribs and simplified bead/C-clip latch.
- `strips3`: three identical strips arranged flat for one print job.
- `slider`: PLA/PETG-oriented three-way radial U-channel guide with lead-in mouths.
- `preview`: three ribbed panels rotated 120 degrees into a triangular beam/tube visualization. It is not intended for direct printing.
- `coupon`: short calibration set: one strip, one slider, and one preview.
- `sweep`: small clearance sweep with several strip/slider pairs.
- `all`: strip, strips3, slider, and preview.

## Example Commands

```bash
python -m yzipper.cli --part strip --preset fdm-loose --teeth 8 --out output/strip_test
python -m yzipper.cli --part slider --preset pla-slider --slider-clearance 0.6 --out output/slider_test
python -m yzipper.cli --part coupon --preset fdm-loose --out output/coupon_loose
python -m yzipper.cli --part sweep --preset fdm-loose --out output/clearance_sweep
python -m yzipper.cli --part all --preset reference-like --out output/reference_like
pytest -q
```

## Presets

- `fdm-loose`: default first print, 8 teeth, loose clip/slider clearances, no snap lip.
- `fdm-medium`: moderate clearances with snap lip enabled.
- `fdm-tight`: tighter clearances for tuned printers only.
- `tpu-strip`: flexible-strip-oriented dimensions.
- `pla-slider`: slider-oriented wall and clearance defaults.
- `reference-like`: screenshot-inspired open ladder strip and triangular guide with screw-hole bosses. This is for visual/fit exploration and is not a proven latch.

## Key Parameters

| Parameter | Meaning | First-test default |
| --- | --- | --- |
| `--teeth` | repeated rib/latch modules | `8` |
| `--pitch` | tooth/rib spacing | `5.0 mm` |
| `--strip-width` | flat panel width | `16.0 mm` |
| `--strip-thickness` / `--base-t` | flexible base thickness | `0.70 mm` |
| `--strip-style` | `membrane` or open `ladder` strip | `membrane` |
| `--latch-style` | simplified `bead-clip` or `none` | `bead-clip` |
| `--rail-width` | side rail width for ladder strips | `1.20 mm` |
| `--tooth-height` | approximate rib height | `1.50 mm` |
| `--clip-clearance` | bead/C-clip clearance | `0.55 mm` loose |
| `--slider-clearance` | total channel extra width | `0.60 mm` loose |
| `--slider-length` | radial guide channel length | `42.0 mm` |
| `--triangular-tube-size` | preview triangle side | defaults to strip width |

## Recommended First Print

```bash
python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/demo_loose
```

Print the strips in TPU or another flexible material. Print the slider in PLA or PETG. Test the strip latch by hand before trying to pull all three through the slider.

## Screenshot-Inspired Reference Parts

The files in `data/reference_1.png` and `data/reference_2.png` show open blue ladder strips feeding into a white triangular guide. To generate a closer visual approximation:

```bash
python -m yzipper.cli --part all --preset reference-like --out output/reference_like
```

This creates `strip_ladder...stl`, `strips3_ladder...stl`, a triangular slider, and a not-for-printing triangular preview. The ladder strip has visible open gaps like the screenshots, but it does not yet implement a faithful interlocking tooth or ball/socket latch.

## Known Limitations

- The latch is a simplified bead/C-clip, not a faithful MIT-style ball-node/socket.
- The flexible bridges are represented by the continuous TPU membrane between ribs; there are no tuned hinge cuts yet.
- The `reference-like` ladder strip is closer to the screenshots visually, but currently latchless.
- Meshes are exported as overlapping primitive shells instead of boolean-unioned solids. Slicers usually handle this, but reloaded STL files can report `watertight=False`.
- The slider is a functional guide/funnel prototype, not a proven one-motion closure mechanism.
- The preview is for scale and visual checking only, not direct printing.
