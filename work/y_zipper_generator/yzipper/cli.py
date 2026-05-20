from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from .assembly import coupon_meshes, make_zipped_preview, standard_part_meshes, sweep_configs
from .config import ConfigError, YZipperConfig, validate_config
from .mesh import export_stl, mesh_stats
from .presets import apply_preset, preset_names
from .slider import make_slider
from .strip import make_strip, make_three_strips_plate


PARTS = ("strip", "strips3", "slider", "preview", "coupon", "sweep", "all")


def clearance_tag(value: float) -> str:
    return f"{int(round(value * 100)):03d}"


def number_tag(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.2f}".rstrip("0").rstrip(".").replace(".", "p")


def part_filename(part: str, config: YZipperConfig) -> str:
    pitch = number_tag(config.pitch)
    clip = clearance_tag(config.clip_clearance)
    slider = clearance_tag(config.slider_clearance)
    style = "" if config.strip_style == "membrane" else f"_{config.strip_style}"
    if part == "strip":
        return f"strip{style}_teeth{config.teeth}_pitch{pitch}_clearance{clip}.stl"
    if part == "strips3":
        return f"strips3{style}_teeth{config.teeth}_pitch{pitch}_clearance{clip}.stl"
    if part == "slider":
        return f"slider_clearance{slider}_len{number_tag(config.slider_length)}.stl"
    if part == "preview":
        return f"preview{style}_teeth{config.teeth}_pitch{pitch}_tube{number_tag(config.tube_side)}_not_for_printing.stl"
    if part.startswith("coupon"):
        return f"{part}{style}_teeth{config.teeth}_pitch{pitch}_clearance{clip}.stl"
    raise ValueError(f"no filename rule for part {part!r}")


def make_config(args: argparse.Namespace) -> YZipperConfig:
    config = apply_preset(YZipperConfig(), args.preset)
    updates = {
        "teeth": args.teeth,
        "pitch": args.pitch,
        "strip_width": args.strip_width,
        "margin": args.margin,
        "strip_thickness": args.strip_thickness,
        "rib_radius": args.rib_radius,
        "rib_y": args.rib_y,
        "strip_style": args.strip_style,
        "latch_style": args.latch_style,
        "rail_width": args.rail_width,
        "bead_radius": args.bead_radius,
        "bead_segment": args.bead_segment,
        "clip_clearance": args.clip_clearance,
        "clip_wall": args.clip_wall,
        "sections": args.sections,
        "plate_spacing": args.plate_spacing,
        "slider_clearance": args.slider_clearance,
        "slider_length": args.slider_length,
        "slider_plate_thickness": args.slider_plate_thickness,
        "slider_wall_thickness": args.slider_wall_thickness,
        "slider_wall_height": args.slider_wall_height,
        "screw_boss_radius": args.screw_boss_radius,
        "screw_hole_radius": args.screw_hole_radius,
        "triangular_tube_size": args.triangular_tube_size,
    }
    config = config.with_updates(**updates)
    if args.tooth_height is not None:
        config = config.with_updates(rib_radius=args.tooth_height / 2.0)
    if args.no_snap_lip:
        config = config.with_updates(snap_lip=False)
    if args.snap_lip:
        config = config.with_updates(snap_lip=True)
    validate_config(config)
    return config


def selected_meshes(part: str, config: YZipperConfig) -> dict[str, object]:
    if part == "strip":
        return {"strip": make_strip(config)}
    if part == "strips3":
        strip = make_strip(config)
        return {"strips3": make_three_strips_plate(strip, spacing=config.plate_spacing)}
    if part == "slider":
        return {"slider": make_slider(config)}
    if part == "preview":
        return {"preview": make_zipped_preview(config)}
    if part == "coupon":
        return coupon_meshes(config)
    if part == "all":
        return standard_part_meshes(config)
    raise ValueError(f"unsupported part {part!r}")


def print_summary(config: YZipperConfig, part: str, out: Path, planned_files: Iterable[Path]) -> None:
    print("Y-Zipper generator parameter summary")
    print(f"  part: {part}")
    print(f"  output: {out}")
    print(f"  teeth: {config.teeth}")
    print(f"  pitch: {config.pitch:.3f} mm")
    print(f"  strip length: {config.strip_length:.3f} mm")
    print(f"  strip width/thickness: {config.strip_width:.3f} / {config.strip_thickness:.3f} mm")
    print(f"  strip style/latch: {config.strip_style} / {config.latch_style}")
    print(f"  rib height: {config.tooth_height:.3f} mm")
    print(f"  clip clearance: {config.clip_clearance:.3f} mm")
    print(f"  slider clearance/length: {config.slider_clearance:.3f} / {config.slider_length:.3f} mm")
    print(f"  triangular tube side: {config.tube_side:.3f} mm")
    print("  planned files:")
    for path in planned_files:
        print(f"    {path}")


def write_params(out: Path, config: YZipperConfig, part: str, generated: list[dict[str, object]]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    payload = config.to_dict()
    payload["part"] = part
    payload["generated"] = generated
    with (out / "params.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def run(args: argparse.Namespace) -> int:
    config = make_config(args)
    out = Path(args.out)

    if args.part == "sweep":
        planned = []
        for sweep_config in sweep_configs(config):
            planned.append(out / part_filename("strip", sweep_config))
            planned.append(out / part_filename("slider", sweep_config))
        print_summary(config, args.part, out, planned)
        if args.dry_run:
            print("Dry run complete; no files written.")
            return 0
        generated: list[dict[str, object]] = []
        for sweep_config in sweep_configs(config):
            validate_config(sweep_config)
            for name, mesh in {"strip": make_strip(sweep_config), "slider": make_slider(sweep_config)}.items():
                path = out / part_filename(name, sweep_config)
                export_stl(mesh, path)
                stats = mesh_stats(mesh)
                stats["file"] = str(path)
                generated.append(stats)
        write_params(out, config, args.part, generated)
        print(f"Wrote {len(generated)} STL files to {out.resolve()}")
        return 0

    meshes = selected_meshes(args.part, config)
    planned = [out / part_filename(name, config) for name in meshes]
    print_summary(config, args.part, out, planned)
    if args.dry_run:
        print("Dry run complete; no files written.")
        return 0

    generated = []
    for name, mesh in meshes.items():
        path = out / part_filename(name, config)
        export_stl(mesh, path)
        stats = mesh_stats(mesh)
        stats["file"] = str(path)
        generated.append(stats)
    write_params(out, config, args.part, generated)
    print(f"Wrote {len(generated)} STL files to {out.resolve()}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate experimental Y-zipper-inspired FDM STL files.")
    parser.add_argument("--out", default="output/demo_loose", help="Output directory")
    parser.add_argument("--part", choices=PARTS, default="all")
    parser.add_argument("--preset", choices=preset_names(), default="fdm-loose")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned files without writing STL files")
    parser.add_argument("--teeth", type=int, default=None, help="Number of repeated tooth/rib modules")
    parser.add_argument("--pitch", type=float, default=None, help="Distance between tooth centers, mm")
    parser.add_argument("--strip-width", type=float, default=None, help="Width of the flexible panel, mm")
    parser.add_argument("--margin", type=float, default=None, help="Plain length at strip ends, mm")
    parser.add_argument("--strip-thickness", "--base-t", dest="strip_thickness", type=float, default=None)
    parser.add_argument("--tooth-height", type=float, default=None, help="Approximate rib/tooth height, mm")
    parser.add_argument("--rib-radius", type=float, default=None, help="Compatibility alias: rib cylinder radius, mm")
    parser.add_argument("--rib-y", type=float, default=None, help="Flat pad width under each rib along length, mm")
    parser.add_argument("--strip-style", choices=["membrane", "ladder"], default=None)
    parser.add_argument("--latch-style", choices=["bead-clip", "none"], default=None)
    parser.add_argument("--rail-width", type=float, default=None, help="Side rail width for ladder strips, mm")
    parser.add_argument("--bead-r", "--bead-radius", dest="bead_radius", type=float, default=None)
    parser.add_argument("--bead-segment", type=float, default=None)
    parser.add_argument("--clip-clearance", type=float, default=None)
    parser.add_argument("--clip-wall", type=float, default=None)
    parser.add_argument("--snap-lip", action="store_true", help="Enable small retaining bumps in the C-clip")
    parser.add_argument("--no-snap-lip", action="store_true", help="Disable retaining bumps for first loose fits")
    parser.add_argument("--sections", type=int, default=None)
    parser.add_argument("--plate-spacing", type=float, default=None)
    parser.add_argument("--slider-clearance", type=float, default=None)
    parser.add_argument("--slider-length", "--slider-arm-len", dest="slider_length", type=float, default=None)
    parser.add_argument("--slider-plate-t", dest="slider_plate_thickness", type=float, default=None)
    parser.add_argument("--slider-wall-t", dest="slider_wall_thickness", type=float, default=None)
    parser.add_argument("--slider-wall-h", dest="slider_wall_height", type=float, default=None)
    parser.add_argument("--screw-boss-radius", type=float, default=None)
    parser.add_argument("--screw-hole-radius", type=float, default=None)
    parser.add_argument("--triangular-tube-size", type=float, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (ConfigError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
