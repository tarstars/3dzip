from __future__ import annotations

import math
from typing import List

import numpy as np
import trimesh

from .config import YZipperConfig
from .mesh import annular_cylinder_z, concat, oriented_box


def make_slider(config: YZipperConfig) -> trimesh.Trimesh:
    """Build a printable three-way guide with radial U-channels and lead-in mouths."""
    meshes: List[trimesh.Trimesh] = []
    channel_width = config.strip_width + config.slider_clearance
    ring_side = config.tube_side + 2.0 * config.slider_clearance
    ring_wall = config.slider_wall_thickness * 1.25
    ring_radius = ring_side / math.sqrt(3.0)
    plate_t = config.slider_plate_thickness
    wall_h = config.slider_wall_height
    wall_t = config.slider_wall_thickness

    verts = []
    for idx in range(3):
        angle = math.radians(90 + idx * 120)
        verts.append(np.array([ring_radius * math.cos(angle), ring_radius * math.sin(angle)]))

    for idx in range(3):
        p0 = verts[idx]
        p1 = verts[(idx + 1) % 3]
        mid = (p0 + p1) / 2.0
        vector = p1 - p0
        angle = math.atan2(vector[1], vector[0])
        meshes.append(oriented_box(float(np.linalg.norm(vector)) + ring_wall, ring_wall, wall_h, tuple(mid), angle, plate_t + wall_h / 2.0))

    inner_offset = ring_radius * 0.55
    for idx in range(3):
        angle = math.radians(90 + idx * 120)
        direction = np.array([math.cos(angle), math.sin(angle)])
        start = direction * inner_offset
        center = start + direction * (config.slider_length / 2.0)
        perpendicular = np.array([-direction[1], direction[0]])

        meshes.append(oriented_box(config.slider_length, channel_width + 2.0 * wall_t, plate_t, tuple(center), angle, plate_t / 2.0))

        for side in (-1, 1):
            wall_center = center + perpendicular * side * (channel_width / 2.0 + wall_t / 2.0)
            meshes.append(oriented_box(config.slider_length, wall_t, wall_h, tuple(wall_center), angle, plate_t + wall_h / 2.0))

            # A short outward splay at the mouth gives TPU strips a lead-in instead of a square edge.
            mouth_center = start + direction * config.slider_length + perpendicular * side * (
                channel_width / 2.0 + wall_t * 0.9
            )
            meshes.append(
                oriented_box(
                    wall_t * 4.0,
                    wall_t,
                    wall_h * 0.65,
                    tuple(mouth_center),
                    angle + side * math.radians(10),
                    plate_t + wall_h * 0.325,
                )
            )

        end = start + direction * config.slider_length
        meshes.append(oriented_box(wall_t * 2.2, channel_width + 2.0 * wall_t, wall_h * 0.65, tuple(end), angle, plate_t + wall_h * 0.325))

    for vertex in verts:
        pad = vertex * 1.45
        meshes.append(
            annular_cylinder_z(
                outer_radius=config.screw_boss_radius,
                inner_radius=config.screw_hole_radius,
                height=plate_t,
                center=[float(pad[0]), float(pad[1]), plate_t / 2.0],
                sections=32,
            )
        )

    return concat(meshes)
