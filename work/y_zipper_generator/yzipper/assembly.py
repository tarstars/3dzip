from __future__ import annotations

from dataclasses import replace

import trimesh

from .config import YZipperConfig
from .geometry import transform_flat_panel_to_triangle
from .mesh import concat
from .slider import make_slider
from .strip import make_strip, make_three_strips_plate


def make_zipped_preview(config: YZipperConfig) -> trimesh.Trimesh:
    """Visual reference only: three ribbed panels arranged as a triangular beam/tube."""
    panel = make_strip(config, include_edges=False)
    return concat([transform_flat_panel_to_triangle(panel, idx, config.tube_side) for idx in range(3)])


def standard_part_meshes(config: YZipperConfig) -> dict[str, trimesh.Trimesh]:
    strip = make_strip(config, include_edges=True)
    return {
        "strip": strip,
        "strips3": make_three_strips_plate(strip, spacing=config.plate_spacing),
        "slider": make_slider(config),
        "preview": make_zipped_preview(config),
    }


def coupon_meshes(config: YZipperConfig) -> dict[str, trimesh.Trimesh]:
    coupon_config = replace(config, teeth=min(config.teeth, 8))
    meshes = standard_part_meshes(coupon_config)
    return {
        "coupon_strip": meshes["strip"],
        "coupon_slider": meshes["slider"],
        "coupon_preview_not_for_printing": meshes["preview"],
    }


def sweep_configs(config: YZipperConfig) -> list[YZipperConfig]:
    clip_values = [0.25, 0.40, 0.55, 0.70]
    slider_values = [0.30, 0.45, 0.60, 0.75]
    base = replace(config, teeth=min(config.teeth, 6), snap_lip=False)
    return [replace(base, clip_clearance=clip, slider_clearance=slider) for clip, slider in zip(clip_values, slider_values)]

