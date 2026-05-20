# Printing Guide

## First Print

Start loose and short:

```bash
python -m yzipper.cli --part all --preset fdm-loose --teeth 8 --out output/demo_loose
```

Print one strip first if you want to conserve TPU:

```bash
python -m yzipper.cli --part strip --preset fdm-loose --teeth 8 --out output/strip_first
```

For a screenshot-inspired visual coupon with open ladder strips:

```bash
python -m yzipper.cli --part all --preset reference-like --out output/reference_like
```

Treat that as a form/fit print first. It is not yet a proven locking latch.

## TPU Strip Advice

- Print flat on the bed.
- Layer height: `0.20 mm`.
- Perimeters: `2-3`.
- Infill: `15-25%`.
- Slow TPU down, especially on Bowden printers.
- Disable tiny snap lips for the first fit by using `fdm-loose` or `--no-snap-lip`.
- For `reference-like` ladder strips, inspect the open slots after slicing; if small rail segments disappear, increase `--rail-width` or `--strip-thickness`.

## PLA/PETG Slider Advice

- Layer height: `0.20 mm`.
- Perimeters: `3+`.
- Infill: `25-40%`.
- Print the slider flat with the channels open upward.
- Prefer PETG if you expect repeated flexing or impact.

## If The Slider Jams

- Increase `--slider-clearance` by `0.10-0.20 mm`.
- Check extrusion multiplier; over-extrusion closes the channel quickly.
- Sand or deburr the channel lead-ins.
- Try `--part sweep` and test the slider files from loose to tight.

## If The Zipper Does Not Hold

- Reduce `--clip-clearance` gradually, for example from `0.55` to `0.42`.
- Enable `--snap-lip` only after the bead enters the clip reliably.
- Print a shorter coupon before changing long strips.

## If Flexible Bridges Tear

- Increase `--strip-thickness` slightly.
- Increase `--pitch` to reduce bending strain between ribs.
- Lower print cooling for TPU if layer bonding is weak.
- Avoid sharp post-processing marks at the latch edge.

## Clearance Sweep

```bash
python -m yzipper.cli --part sweep --preset fdm-loose --out output/clearance_sweep
```

The sweep creates several strip/slider pairs with encoded clearances. Start with the loosest part that slides freely, then move tighter until holding force is useful without jamming.
