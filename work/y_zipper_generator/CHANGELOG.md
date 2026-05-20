# Changelog

## 0.1.0

- Refactored the v0 single Python script into a `yzipper` package.
- Added config dataclass, presets, parameter validation, and reusable geometry modules.
- Added CLI support for `strip`, `strips3`, `slider`, `preview`, `coupon`, `sweep`, and `all`.
- Added `--dry-run`, `--out`, preset selection, parameter summaries, and encoded output filenames.
- Added a compatibility wrapper at `y_zipper_generator.py`.
- Added pytest smoke and mesh-validity tests.
- Added README, printing guide, TODO, and agent report.
- Kept the extracted v0 Python/OpenSCAD files for audit/reference.
- Added `reference-like` preset from the supplied screenshots, with open ladder strips and slider screw-hole bosses.
- Added `--strip-style`, `--latch-style`, `--rail-width`, `--screw-boss-radius`, and `--screw-hole-radius`.
