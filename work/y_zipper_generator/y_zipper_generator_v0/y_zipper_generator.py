#!/usr/bin/env python3
"""
y_zipper_generator.py

Parametric generator for an experimental, Y-zipper-inspired 3D-printable
prototype. This is NOT the official MIT/CSAIL Y-Zipper model. It is a
home-printer-friendly approximation built from the visible concept:
three flexible ribbed strips plus a triangular guide/slider.

Outputs STL files:
  - strip_single_TPU.stl      : one flexible strip with ribs and bead/clip edges
  - strip_3x_TPU.stl          : three identical strips laid out for one print job
  - slider_PLA.stl            : simplified 3-way guide/slider jig
  - zipped_preview.stl        : non-print/fit preview of three panels as a triangular tube
  - params.json               : dimensions used

Install:
  python -m pip install numpy trimesh

Example:
  python y_zipper_generator.py --part all --out yz_out --teeth 18 --pitch 5.0

Printing suggestion for first tests:
  - strips: TPU, 0.20 mm layer, 2-3 perimeters, 15-25% infill
  - slider: PLA/PETG, 0.20 mm layer, 3+ perimeters
  - start with --teeth 8 to tune bead_r / clearance before a long strip
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
import trimesh


Vec3 = Tuple[float, float, float]


def box_mesh(size: Vec3, center: Vec3) -> trimesh.Trimesh:
    """Create an axis-aligned rectangular box."""
    mesh = trimesh.creation.box(extents=size)
    mesh.apply_translation(center)
    return mesh


def cylinder_along(axis: str, radius: float, length: float, center: Vec3, sections: int = 18) -> trimesh.Trimesh:
    """Create a capped cylinder along X, Y, or Z."""
    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    if axis.lower() == "x":
        # default cylinder axis is Z; rotate Z -> X
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0]))
    elif axis.lower() == "y":
        # default cylinder axis is Z; rotate Z -> Y
        mesh.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2.0, [1, 0, 0]))
    elif axis.lower() == "z":
        pass
    else:
        raise ValueError("axis must be 'x', 'y', or 'z'")
    mesh.apply_translation(center)
    return mesh


def oriented_box(length: float, width: float, height: float, center_xy: Tuple[float, float], angle_rad: float, z_center: float) -> trimesh.Trimesh:
    """Box with local X=length, local Y=width, local Z=height, rotated about Z."""
    mesh = trimesh.creation.box(extents=[length, width, height])
    mesh.apply_transform(trimesh.transformations.rotation_matrix(angle_rad, [0, 0, 1]))
    mesh.apply_translation([center_xy[0], center_xy[1], z_center])
    return mesh


def concat(meshes: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    meshes = [m for m in meshes if m is not None]
    if not meshes:
        return trimesh.Trimesh(vertices=[], faces=[])
    # Keep each primitive as a closed shell. We intentionally avoid boolean
    # unions so the script works without OpenSCAD/Blender/CGAL. Most slicers
    # merge overlapping shells during slicing.
    out = trimesh.util.concatenate(meshes)
    return out


def make_flat_strip(
    teeth: int = 18,
    pitch: float = 5.0,
    strip_width: float = 16.0,
    margin: float = 5.0,
    base_t: float = 0.70,
    rib_radius: float = 0.75,
    rib_y: float = 1.25,
    bead_r: float = 1.05,
    bead_segment: float | None = None,
    clip_clearance: float = 0.35,
    clip_wall: float = 0.85,
    clip_depth: float | None = None,
    snap_lip: bool = True,
    sections: int = 18,
    include_edges: bool = True,
) -> trimesh.Trimesh:
    """
    Build a flat strip. Coordinate convention:
      X = strip width, Y = strip length, Z = height above bed.

    Edges are an intentionally simple bead/clip latch:
      - left edge: segmented round bead + neck
      - right edge: segmented C-channel clip, with optional small snap lips
    """
    length = 2 * margin + teeth * pitch
    meshes: List[trimesh.Trimesh] = []

    # Thin flexible membrane.
    meshes.append(box_mesh([strip_width, length, base_t], [0, length / 2, base_t / 2]))

    # Transverse ribs/corrugations. Cylinders partly embedded into the membrane
    # to create a round top with a flat printable contact.
    rib_len = max(2.0, strip_width - 2.2)
    for i in range(teeth):
        y = margin + (i + 0.5) * pitch
        # A small flat pad below the rod improves slicer/manifold behavior.
        meshes.append(box_mesh([rib_len, rib_y, rib_radius * 0.55], [0, y, base_t + rib_radius * 0.15]))
        meshes.append(cylinder_along("x", rib_radius, rib_len, [0, y, base_t + rib_radius * 0.75], sections=sections))

    if not include_edges:
        return concat(meshes)

    bead_segment = bead_segment if bead_segment is not None else pitch * 0.62
    clip_depth = clip_depth if clip_depth is not None else bead_r * 2.2 + clip_clearance
    slot_h = bead_r * 2.0 + clip_clearance
    clip_h = slot_h + 2.0 * clip_wall

    # Male bead edge: segmented bead plus neck. Broken into teeth to keep it flexible.
    bead_x = -strip_width / 2.0 - bead_r * 1.15
    neck_w = bead_r * 0.55
    neck_x = -strip_width / 2.0 - neck_w / 2.0
    bead_z = base_t + bead_r
    for i in range(teeth):
        y = margin + (i + 0.5) * pitch
        seg = min(bead_segment, pitch * 0.82)
        meshes.append(box_mesh([neck_w, seg, bead_r * 0.80], [neck_x, y, bead_z]))
        meshes.append(cylinder_along("y", bead_r, seg, [bead_x, y, bead_z], sections=sections))

    # Female clip edge: segmented C-channel. It is deliberately loose on v0;
    # tighten clip_clearance or enable snap_lip for more holding force.
    back_x = strip_width / 2.0 + clip_wall / 2.0
    depth_center_x = strip_width / 2.0 + clip_wall + clip_depth / 2.0
    lip_z_bottom = base_t + clip_wall / 2.0
    lip_z_top = base_t + clip_wall + slot_h + clip_wall / 2.0
    back_z = base_t + clip_h / 2.0
    for i in range(teeth):
        y = margin + (i + 0.5) * pitch
        seg = min(bead_segment, pitch * 0.82)
        meshes.append(box_mesh([clip_wall, seg, clip_h], [back_x, y, back_z]))              # back wall
        meshes.append(box_mesh([clip_depth, seg, clip_wall], [depth_center_x, y, lip_z_bottom]))  # bottom lip
        meshes.append(box_mesh([clip_depth, seg, clip_wall], [depth_center_x, y, lip_z_top]))     # top lip
        if snap_lip:
            # Little bumps near the mouth reduce the opening; TPU can flex over them.
            catch_t = max(0.35, bead_r * 0.35)
            catch_h = max(0.25, bead_r * 0.28)
            catch_x = strip_width / 2.0 + clip_wall + clip_depth - catch_t / 2.0
            lower_z = base_t + clip_wall + catch_h / 2.0
            upper_z = base_t + clip_wall + slot_h - catch_h / 2.0
            meshes.append(box_mesh([catch_t, seg, catch_h], [catch_x, y, lower_z]))
            meshes.append(box_mesh([catch_t, seg, catch_h], [catch_x, y, upper_z]))

    # Pull tab / handle at the first end.
    tab_y = margin * 0.45
    meshes.append(box_mesh([strip_width * 0.70, margin * 0.55, base_t * 1.25], [0, tab_y, base_t * 0.62]))

    return concat(meshes)


def make_three_strips_plate(strip: trimesh.Trimesh, spacing: float = 8.0) -> trimesh.Trimesh:
    """Duplicate one strip into three parallel strips for a single TPU print."""
    bounds = strip.bounds
    width = bounds[1, 0] - bounds[0, 0]
    meshes = []
    for idx in range(3):
        m = strip.copy()
        m.apply_translation([(idx - 1) * (width + spacing), 0, 0])
        meshes.append(m)
    return concat(meshes)


def make_slider(
    strip_width: float = 16.0,
    channel_clearance: float = 1.0,
    arm_len: float = 48.0,
    plate_t: float = 2.2,
    wall_t: float = 2.0,
    wall_h: float = 6.5,
    ring_side: float | None = None,
) -> trimesh.Trimesh:
    """
    Simplified printable Y-guide/slider.

    It is a flat jig with three radial U-channels and a central triangular frame.
    The channel geometry is intentionally open, so it prints without trapped support.
    """
    meshes: List[trimesh.Trimesh] = []
    ch_w = strip_width + channel_clearance
    ring_side = ring_side if ring_side is not None else strip_width + 2.0 * channel_clearance
    ring_wall = wall_t * 1.25
    ring_h = wall_h

    # Central equilateral triangular ring, built from three bars.
    # Triangle in XY, height in Z. Radius from center to vertices:
    R = ring_side / math.sqrt(3.0)
    verts = []
    for k in range(3):
        a = math.radians(90 + k * 120)
        verts.append(np.array([R * math.cos(a), R * math.sin(a)]))
    for k in range(3):
        p0 = verts[k]
        p1 = verts[(k + 1) % 3]
        mid = (p0 + p1) / 2.0
        v = p1 - p0
        angle = math.atan2(v[1], v[0])
        meshes.append(oriented_box(float(np.linalg.norm(v)) + ring_wall, ring_wall, ring_h, tuple(mid), angle, plate_t + ring_h / 2.0))

    # Three open U channels. Local X points outward; local Y is channel width.
    inner_offset = R * 0.55
    for k in range(3):
        angle = math.radians(90 + k * 120)
        d = np.array([math.cos(angle), math.sin(angle)])
        # Start just outside central ring, extend outward.
        start = d * inner_offset
        center = start + d * (arm_len / 2.0)
        # Base tray
        meshes.append(oriented_box(arm_len, ch_w + 2 * wall_t, plate_t, tuple(center), angle, plate_t / 2.0))
        # Side walls, offset perpendicular to direction.
        perp = np.array([-d[1], d[0]])
        for s in [-1, 1]:
            c = center + perp * s * (ch_w / 2.0 + wall_t / 2.0)
            meshes.append(oriented_box(arm_len, wall_t, wall_h, tuple(c), angle, plate_t + wall_h / 2.0))
        # Rounded lead-in at outer end.
        end = start + d * arm_len
        meshes.append(oriented_box(wall_t * 2.2, ch_w + 2 * wall_t, wall_h * 0.65, tuple(end), angle, plate_t + wall_h * 0.325))

    # Optional corner pads around the frame for clamping/screws; left solid on purpose.
    for k in range(3):
        p = verts[k] * 1.45
        meshes.append(cylinder_along("z", radius=4.0, length=plate_t, center=[float(p[0]), float(p[1]), plate_t / 2.0], sections=24))

    return concat(meshes)


def transform_flat_panel_to_triangle(mesh: trimesh.Trimesh, side_index: int, side_len: float) -> trimesh.Trimesh:
    """
    Map a flat strip into one side of a triangular tube preview.
    Local flat coordinates: X=side direction, Y=beam length, Z=outward thickness.
    Global: X/Z are cross-section, Y remains length.
    """
    # Equilateral triangle vertices in XZ plane, centered around origin.
    h = math.sqrt(3.0) / 2.0 * side_len
    pts = [np.array([-side_len / 2, -h / 3]), np.array([side_len / 2, -h / 3]), np.array([0.0, 2 * h / 3])]
    p0 = pts[side_index]
    p1 = pts[(side_index + 1) % 3]
    center = (p0 + p1) / 2.0
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    # Outward normal: away from triangle centroid (0,0)
    n = center / (np.linalg.norm(center) + 1e-9)
    # Force n perpendicular-ish to side, normalized.
    n = np.array([u[1], -u[0]])
    # Choose the normal pointing outward.
    if np.dot(n, center) < 0:
        n = -n

    m = mesh.copy()
    v = m.vertices.copy()
    x_local = v[:, 0]
    y_local = v[:, 1]
    z_local = v[:, 2]
    cross = center[None, :] + x_local[:, None] * u[None, :] + z_local[:, None] * n[None, :]
    # New global: X=cross.x, Y=original length, Z=cross.z
    m.vertices = np.column_stack([cross[:, 0], y_local, cross[:, 1]])
    return m


def make_zipped_preview(
    teeth: int = 18,
    pitch: float = 5.0,
    strip_width: float = 16.0,
    margin: float = 5.0,
    base_t: float = 0.70,
    rib_radius: float = 0.75,
    sections: int = 18,
) -> trimesh.Trimesh:
    """Three ribbed panels arranged as a triangular tube. Preview/fit reference only."""
    panel = make_flat_strip(
        teeth=teeth,
        pitch=pitch,
        strip_width=strip_width,
        margin=margin,
        base_t=base_t,
        rib_radius=rib_radius,
        sections=sections,
        include_edges=False,
    )
    return concat([transform_flat_panel_to_triangle(panel, i, strip_width) for i in range(3)])


def export(mesh: trimesh.Trimesh, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    m = mesh.copy()
    # Put the lowest point on the bed for slicers.
    if len(m.vertices):
        min_z = float(m.bounds[0, 2])
        if min_z != 0.0:
            m.apply_translation([0, 0, -min_z])
    m.export(path)


def build_all(args: argparse.Namespace) -> None:
    out = Path(args.out)
    strip = make_flat_strip(
        teeth=args.teeth,
        pitch=args.pitch,
        strip_width=args.strip_width,
        margin=args.margin,
        base_t=args.base_t,
        rib_radius=args.rib_radius,
        rib_y=args.rib_y,
        bead_r=args.bead_r,
        bead_segment=args.bead_segment,
        clip_clearance=args.clip_clearance,
        clip_wall=args.clip_wall,
        snap_lip=not args.no_snap_lip,
        sections=args.sections,
        include_edges=True,
    )
    strip3 = make_three_strips_plate(strip, spacing=args.plate_spacing)
    slider = make_slider(
        strip_width=args.strip_width,
        channel_clearance=args.slider_clearance,
        arm_len=args.slider_arm_len,
        plate_t=args.slider_plate_t,
        wall_t=args.slider_wall_t,
        wall_h=args.slider_wall_h,
    )
    preview = make_zipped_preview(
        teeth=args.teeth,
        pitch=args.pitch,
        strip_width=args.strip_width,
        margin=args.margin,
        base_t=args.base_t,
        rib_radius=args.rib_radius,
        sections=args.sections,
    )

    if args.part in ("all", "strip"):
        export(strip, out / "strip_single_TPU.stl")
        export(strip3, out / "strip_3x_TPU.stl")
    if args.part in ("all", "slider"):
        export(slider, out / "slider_PLA.stl")
    if args.part in ("all", "preview"):
        export(preview, out / "zipped_preview_not_for_printing.stl")

    params = vars(args).copy()
    params["note"] = "Experimental Y-zipper-inspired generator, not the official MIT/CSAIL geometry. Tune clearances for your printer/material."
    with open(out / "params.json", "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2)

    print(f"Wrote files to {out.resolve()}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate experimental Y-zipper-inspired STL files.")
    p.add_argument("--out", default="yz_out", help="Output directory")
    p.add_argument("--part", choices=["all", "strip", "slider", "preview"], default="all")
    p.add_argument("--teeth", type=int, default=18, help="Number of repeated rib/tooth modules")
    p.add_argument("--pitch", type=float, default=5.0, help="Distance between tooth centers, mm")
    p.add_argument("--strip-width", type=float, default=16.0, help="Width of the flexible panel, mm")
    p.add_argument("--margin", type=float, default=5.0, help="Plain length at strip ends, mm")
    p.add_argument("--base-t", type=float, default=0.70, help="Flexible base membrane thickness, mm")
    p.add_argument("--rib-radius", type=float, default=0.75, help="Rib/corrugation radius, mm")
    p.add_argument("--rib-y", type=float, default=1.25, help="Flat pad width under each rib along length, mm")
    p.add_argument("--bead-r", type=float, default=1.05, help="Male bead radius, mm")
    p.add_argument("--bead-segment", type=float, default=None, help="Length of each bead/clip segment, mm; default = 0.62*pitch")
    p.add_argument("--clip-clearance", type=float, default=0.35, help="Extra room in female clip slot, mm")
    p.add_argument("--clip-wall", type=float, default=0.85, help="Female clip wall/lip thickness, mm")
    p.add_argument("--no-snap-lip", action="store_true", help="Disable little retaining bumps in the female clip")
    p.add_argument("--sections", type=int, default=18, help="Cylinder resolution")
    p.add_argument("--plate-spacing", type=float, default=8.0, help="Spacing between strips in strip_3x_TPU.stl, mm")
    p.add_argument("--slider-clearance", type=float, default=1.2, help="Channel clearance around strip width, mm")
    p.add_argument("--slider-arm-len", type=float, default=48.0, help="Slider guide arm length, mm")
    p.add_argument("--slider-plate-t", type=float, default=2.2, help="Slider base plate thickness, mm")
    p.add_argument("--slider-wall-t", type=float, default=2.0, help="Slider channel wall thickness, mm")
    p.add_argument("--slider-wall-h", type=float, default=6.5, help="Slider channel wall height, mm")
    return p.parse_args()


if __name__ == "__main__":
    build_all(parse_args())
