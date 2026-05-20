# TODO

## Near-Term

- Print `output/demo_loose` and record real fit notes for TPU hardness, nozzle size, and extrusion multiplier.
- Add a combined bed-layout coupon with labels embossed or raised near each clearance.
- Tune slider entry mouths after physical testing.
- Compare the `reference-like` ladder strip against a printed screenshot-style coupon and tune rail/rib dimensions.
- Add optional per-strip left/right latch variants if mirrored latch behavior is useful.
- Add a mesh repair/export option for users whose slicers dislike overlapping shells.

## Future Work

- Replace or supplement the simplified bead/C-clip with a more faithful ball-node/socket mechanism.
- Add a real interlocking latch for the open ladder strip style.
- Add explicit flexible bridge/hinge geometry instead of relying only on the continuous membrane.
- Model the slider as a true progressive funnel that brings three strips from flat input into the triangular output.
- Add force/clearance annotations from physical test results.
- Add optional OpenSCAD export generated from the same config so the SCAD file stays secondary but synchronized.
