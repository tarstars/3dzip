# Agent Report

## Extraction And Inventory

Source ZIP left untouched:

- `data/y_zipper_generator_v0.zip`

Extracted to:

- `work/y_zipper_generator/y_zipper_generator_v0/`

Extracted files:

- `y_zipper_generator_v0/README.md`
- `y_zipper_generator_v0/requirements.txt`
- `y_zipper_generator_v0/y_zipper_generator.py`
- `y_zipper_generator_v0/y_zipper_generator.scad`
- `y_zipper_generator_v0/sample_12tooth/params.json`
- `y_zipper_generator_v0/sample_12tooth/slider_PLA.stl`
- `y_zipper_generator_v0/sample_12tooth/strip_3x_TPU.stl`
- `y_zipper_generator_v0/sample_12tooth/strip_single_TPU.stl`
- `y_zipper_generator_v0/sample_12tooth/zipped_preview_not_for_printing.stl`

An existing parent git repository was already present at `/home/tarstars/prj/3dzip`, so no nested git repo was initialized.

## V0 Audit

What worked:

- The v0 README correctly states this is not the official MIT/CSAIL geometry.
- The Python generator is pure `numpy` + `trimesh` and can generate STL files once dependencies are installed.
- The OpenSCAD file exists as an alternate hand-editable prototype.
- Generated v0 scale is plausible in millimeters.
- Three-strip preview uses a 120-degree triangular arrangement.
- Teeth/ribs repeat deterministically by `pitch`.

What was broken or weak:

- Running documented commands in the base environment initially failed with `ModuleNotFoundError: No module named 'trimesh'`.
- Import-time dependency failure prevents `--help` from working without installed dependencies.
- No parameter validation for impossible dimensions.
- CLI only supported `all`, `strip`, `slider`, and `preview`.
- No presets, dry-run, coupon, sweep, or encoded output filenames.
- Slider was a useful guide concept but had limited explicit lead-in/funnel behavior.
- The latch is a simplified segmented bead/C-clip, not a ball-node/socket.
- Exported STL files reload as `watertight=False` because the geometry is overlapping primitive shells rather than boolean-unioned CAD solids.
- Zipped preview reports negative signed volume after import; it is usable as a visual reference but not a direct print.

## Changes Made

- Added package structure under `yzipper/`:
  - `config.py`
  - `geometry.py`
  - `mesh.py`
  - `strip.py`
  - `slider.py`
  - `assembly.py`
  - `presets.py`
  - `validate.py`
  - `cli.py`
- Added a compatibility wrapper: `y_zipper_generator.py`.
- Added `pyproject.toml`, root `requirements.txt`, tests, and example script.
- Added presets: `fdm-loose`, `fdm-medium`, `fdm-tight`, `tpu-strip`, `pla-slider`.
- Added screenshot-inspired `reference-like` preset after inspecting:
  - `data/reference_1.png`
  - `data/reference_2.png`
- Added CLI parts: `strip`, `strips3`, `slider`, `preview`, `coupon`, `sweep`, `all`.
- Added `--dry-run`, `--out`, parameter summaries, and parameter validation.
- Added `--strip-style ladder`, `--latch-style none`, side-rail sizing, and slider screw-hole boss parameters.
- Added output filenames that encode major parameters.
- Added docs:
  - `README.md`
  - `PRINTING_GUIDE.md`
  - `CHANGELOG.md`
  - `TODO.md`
- Left intentional sample output in `output/demo_loose/`.

## Commands Run

Initial extraction/audit:

```bash
unzip -q data/y_zipper_generator_v0.zip -d work/y_zipper_generator
python y_zipper_generator.py --help
```

Initial `--help` failed before dependency installation:

```text
ModuleNotFoundError: No module named 'trimesh'
```

Dependency setup and v0 generation audit:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r y_zipper_generator_v0/requirements.txt
../.venv/bin/python y_zipper_generator.py --part all --out audit_out_default
../.venv/bin/python y_zipper_generator.py --part all --out audit_out_test --teeth 8 --pitch 5.0
```

Refactored generator smoke commands:

```bash
.venv/bin/python -m yzipper.cli --help
.venv/bin/python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/smoke --dry-run
.venv/bin/python y_zipper_generator.py --part all --out output/legacy_test --teeth 8 --dry-run
.venv/bin/python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/demo_loose
.venv/bin/python -m yzipper.cli --part sweep --preset fdm-loose --out output/sweep_smoke --dry-run
.venv/bin/python -m yzipper.cli --part all --preset reference-like --out output/reference_like
```

Generation output summary:

```text
Y-Zipper generator parameter summary
  part: all
  output: output/demo_loose
  teeth: 8
  pitch: 5.000 mm
  strip length: 50.000 mm
  strip width/thickness: 16.000 / 0.700 mm
  rib height: 1.500 mm
  clip clearance: 0.550 mm
  slider clearance/length: 0.600 / 42.000 mm
  triangular tube side: 16.000 mm
  planned files:
    output/demo_loose/strip_teeth8_pitch5_clearance055.stl
    output/demo_loose/strips3_teeth8_pitch5_clearance055.stl
    output/demo_loose/slider_clearance060_len42.stl
    output/demo_loose/preview_teeth8_pitch5_tube16_not_for_printing.stl
Wrote 4 STL files to /home/tarstars/prj/3dzip/work/y_zipper_generator/output/demo_loose
```

Test command:

```bash
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest -q
```

## Test Results

```text
18 passed in 3.46s
```

Covered:

- CLI help.
- Dry-run.
- Strip generation.
- Slider generation.
- Coupon generation.
- Mesh bounds/finite geometry.
- Tooth count and strip length relationship.
- Invalid parameter failure.

## Generated Sample Files

Directory:

- `output/demo_loose/`
- `output/reference_like/`

Generated files and imported STL stats:

| File | Vertices | Faces | Finite | Watertight | Volume | Extents mm |
| --- | ---: | ---: | --- | --- | ---: | --- |
| `strip_teeth8_pitch5_clearance055.stl` | 912 | 1656 | true | false | 1143.500 | `[21.967, 50.0, 5.054]` |
| `strips3_teeth8_pitch5_clearance055.stl` | 2736 | 4968 | true | false | 3430.499 | `[81.903, 50.0, 5.054]` |
| `slider_clearance060_len42.stl` | 306 | 540 | true | false | 11829.132 | `[100.508, 87.39, 8.7]` |
| `preview_teeth8_pitch5_tube16_not_for_printing.stl` | 1122 | 2052 | true | false | -2424.240 | `[18.386, 50.0, 16.219]` |

Reference-like screenshot-inspired files:

| File | Vertices | Faces | Finite | Watertight | Volume | Extents mm |
| --- | ---: | ---: | --- | --- | ---: | --- |
| `strip_ladder_teeth10_pitch4p6_clearance060.stl` | 560 | 1032 | true | false | 778.398 | `[17.0, 56.0, 2.237]` |
| `strips3_ladder_teeth10_pitch4p6_clearance060.stl` | 1680 | 3096 | true | false | 2335.194 | `[67.0, 56.0, 2.237]` |
| `slider_clearance080_len45.stl` | 540 | 1020 | true | false | 13412.329 | `[107.074, 93.076, 9.2]` |
| `preview_ladder_teeth10_pitch4p6_tube17_not_for_printing.stl` | 1614 | 3096 | true | false | -2335.194 | `[20.875, 56.0, 18.079]` |

The in-memory primitive-shell meshes are closed before export, but imported STL processing reports `watertight=False` because overlapping shells are not boolean-unioned.

## Remaining Limitations

- This is still an approximate Y-zipper mechanism, not verified MIT geometry.
- Simplified bead/C-clip latch remains in place; ball-node/socket is future work.
- Slider geometry needs physical test feedback before calling it reliable.
- The new `reference-like` ladder strip matches the screenshots more closely, but it is currently latchless and should be treated as a visual/form/fit coupon.
- Preview is a visualization, not a direct print.
- Meshes are not boolean-unioned; slicer behavior should be checked on the target slicer.
- No physical print results are available yet.

## Recommended First Print Command

```bash
python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/demo_loose
```
