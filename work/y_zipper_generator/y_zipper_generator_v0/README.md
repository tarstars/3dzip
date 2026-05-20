# Experimental Y-Zipper Generator v0

This package contains a **parametric prototype generator** for a 3D-printable, Y-zipper-inspired mechanism: three ribbed flexible strips plus a simplified triangular guide/slider.

It is **not** the official MIT/CSAIL Y-Zipper model and it does not reproduce the exact tooth geometry from the paper/video. It is a practical starting point for home-printer experimentation based on the visible concept.

## Files in the sample output

- `strip_single_TPU.stl` — one flexible ribbed strip.
- `strip_3x_TPU.stl` — three identical strips arranged on the bed for one print.
- `slider_PLA.stl` — simplified three-way guide/slider jig.
- `zipped_preview_not_for_printing.stl` — visual reference showing three strips as a triangular tube; use for scale/fit, not as the main print.
- `params.json` — parameters used for the sample STL files.
- `y_zipper_generator.py` — Python generator that directly writes STL files.
- `y_zipper_generator.scad` — OpenSCAD version for users who prefer editing/exporting in OpenSCAD.

## Install for the Python generator

```bash
python -m pip install numpy trimesh
```

The OpenSCAD file has no Python dependency; open `y_zipper_generator.scad`, set `part = "strip3"` or `part = "slider"`, then render/export STL.

## Generate the default sample

```bash
python y_zipper_generator.py --part all --out yz_out
```

## Generate a short tolerance test first

```bash
python y_zipper_generator.py --part all --out yz_test --teeth 8 --pitch 5.0
```

## Print settings to start

### Flexible strips

- Material: TPU first; PETG may work if your design is loose enough, PLA will be stiffer.
- Layer height: 0.20 mm.
- Perimeters: 2-3.
- Infill: 15-25%.
- Print flat on the bed.
- Slow down for TPU; direct drive helps.

### Slider / guide

- Material: PLA or PETG.
- Layer height: 0.20 mm.
- Perimeters: 3 or more.
- Infill: 25-40%.

## Tuning

If the bead will not enter the clip:

```bash
python y_zipper_generator.py --part all --out yz_loose --clip-clearance 0.55 --no-snap-lip
```

If the connection is too loose:

```bash
python y_zipper_generator.py --part all --out yz_tight --clip-clearance 0.20
```

If the strip is too stiff:

```bash
python y_zipper_generator.py --part all --out yz_flexible --base-t 0.55 --pitch 5.5
```

If the ribs are too fragile:

```bash
python y_zipper_generator.py --part all --out yz_stronger --rib-radius 0.95 --base-t 0.80
```

## Current limitations

- The generated strip uses a simple segmented bead-and-clip latch, not the exact MIT tooth/interlock geometry.
- The slider is a printable guide jig, not a proven one-click slider mechanism.
- Expect to tune clearances for your exact printer, filament, extrusion multiplier, and TPU hardness.
- Start with 6-8 teeth before printing a long strip.

## Useful parameters

```text
--teeth              number of repeated tooth/rib modules
--pitch              spacing between tooth centers, mm
--strip-width        width of each flexible side panel, mm
--base-t             flexible base thickness, mm
--rib-radius         size of the visible transverse ribs, mm
--bead-r             male bead radius, mm
--clip-clearance     clearance inside the female clip, mm
--no-snap-lip        disables retaining bumps for an easier first fit
--slider-clearance   clearance in the slider channel, mm
```
