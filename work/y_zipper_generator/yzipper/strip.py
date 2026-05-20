from __future__ import annotations

from typing import List

import trimesh

from .config import YZipperConfig
from .mesh import box_mesh, concat, cylinder_along


def make_strip(config: YZipperConfig, include_edges: bool = True) -> trimesh.Trimesh:
    """Build one flat strip with repeated ribs and a simplified bead/C-clip latch."""
    if config.strip_style == "ladder":
        return make_ladder_strip(config, include_edges=include_edges)
    return make_membrane_strip(config, include_edges=include_edges)


def make_membrane_strip(config: YZipperConfig, include_edges: bool = True) -> trimesh.Trimesh:
    """Build the original membrane-backed strip."""
    meshes: List[trimesh.Trimesh] = []
    length = config.strip_length
    strip_width = config.strip_width
    base_t = config.strip_thickness

    meshes.append(box_mesh([strip_width, length, base_t], [0, length / 2.0, base_t / 2.0]))

    rib_len = max(2.0, strip_width - 2.2)
    for idx in range(config.teeth):
        y = config.margin + (idx + 0.5) * config.pitch
        meshes.append(
            box_mesh([rib_len, config.rib_y, config.rib_radius * 0.55], [0, y, base_t + config.rib_radius * 0.15])
        )
        meshes.append(
            cylinder_along("x", config.rib_radius, rib_len, [0, y, base_t + config.rib_radius * 0.75], config.sections)
        )

    if not include_edges or config.latch_style == "none":
        return concat(meshes)

    bead_segment = min(config.bead_segment_length, config.pitch * 0.82)
    bead_x = -strip_width / 2.0 - config.bead_radius * 1.15
    neck_w = config.bead_radius * 0.55
    neck_x = -strip_width / 2.0 - neck_w / 2.0
    bead_z = base_t + config.bead_radius

    for idx in range(config.teeth):
        y = config.margin + (idx + 0.5) * config.pitch
        meshes.append(box_mesh([neck_w, bead_segment, config.bead_radius * 0.80], [neck_x, y, bead_z]))
        meshes.append(cylinder_along("y", config.bead_radius, bead_segment, [bead_x, y, bead_z], config.sections))

    back_x = strip_width / 2.0 + config.clip_wall / 2.0
    depth_center_x = strip_width / 2.0 + config.clip_wall + config.clip_depth / 2.0
    lip_z_bottom = base_t + config.clip_wall / 2.0
    lip_z_top = base_t + config.clip_wall + config.clip_slot_height + config.clip_wall / 2.0
    back_z = base_t + config.clip_height / 2.0

    for idx in range(config.teeth):
        y = config.margin + (idx + 0.5) * config.pitch
        meshes.append(box_mesh([config.clip_wall, bead_segment, config.clip_height], [back_x, y, back_z]))
        meshes.append(box_mesh([config.clip_depth, bead_segment, config.clip_wall], [depth_center_x, y, lip_z_bottom]))
        meshes.append(box_mesh([config.clip_depth, bead_segment, config.clip_wall], [depth_center_x, y, lip_z_top]))
        if config.snap_lip:
            catch_t = max(0.35, config.bead_radius * 0.35)
            catch_h = max(0.25, config.bead_radius * 0.28)
            catch_x = strip_width / 2.0 + config.clip_wall + config.clip_depth - catch_t / 2.0
            lower_z = base_t + config.clip_wall + catch_h / 2.0
            upper_z = base_t + config.clip_wall + config.clip_slot_height - catch_h / 2.0
            meshes.append(box_mesh([catch_t, bead_segment, catch_h], [catch_x, y, lower_z]))
            meshes.append(box_mesh([catch_t, bead_segment, catch_h], [catch_x, y, upper_z]))

    tab_y = config.margin * 0.45
    meshes.append(box_mesh([strip_width * 0.70, config.margin * 0.55, base_t * 1.25], [0, tab_y, base_t * 0.62]))
    return concat(meshes)


def make_ladder_strip(config: YZipperConfig, include_edges: bool = True) -> trimesh.Trimesh:
    """Build a screenshot-inspired open ladder strip.

    This is a visual/mechanical approximation of the reference images: rounded
    transverse bars connected by two flexible side rails, with open slots between
    bars instead of a continuous membrane.
    """
    meshes: List[trimesh.Trimesh] = []
    length = config.strip_length
    base_t = config.strip_thickness
    half_width = config.strip_width / 2.0
    rail_x = half_width - config.rail_width / 2.0

    for side in (-1, 1):
        x = side * rail_x
        meshes.append(box_mesh([config.rail_width, length, base_t], [x, length / 2.0, base_t / 2.0]))
        meshes.append(cylinder_along("y", config.rail_width / 2.0, length, [x, length / 2.0, base_t], config.sections))

    rib_len = max(2.0, config.strip_width)
    rib_z = base_t + config.rib_radius * 0.75
    pad_h = max(0.35, base_t * 0.65)
    for idx in range(config.teeth):
        y = config.margin + (idx + 0.5) * config.pitch
        meshes.append(box_mesh([rib_len, config.rib_y, pad_h], [0, y, pad_h / 2.0]))
        meshes.append(cylinder_along("x", config.rib_radius, rib_len, [0, y, rib_z], config.sections))

    # Short rounded tabs help start the flexible strip through the guide.
    for y in (config.margin * 0.35, length - config.margin * 0.35):
        meshes.append(box_mesh([config.strip_width * 0.85, config.margin * 0.45, base_t], [0, y, base_t / 2.0]))

    return concat(meshes)


def make_three_strips_plate(strip: trimesh.Trimesh, spacing: float = 8.0) -> trimesh.Trimesh:
    bounds = strip.bounds
    width = float(bounds[1, 0] - bounds[0, 0])
    meshes = []
    for idx in range(3):
        copy = strip.copy()
        copy.apply_translation([(idx - 1) * (width + spacing), 0, 0])
        meshes.append(copy)
    return concat(meshes)
