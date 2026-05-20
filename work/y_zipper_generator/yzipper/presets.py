from __future__ import annotations

from .config import YZipperConfig


PRESETS: dict[str, dict[str, object]] = {
    "fdm-loose": {
        "teeth": 8,
        "clip_clearance": 0.55,
        "slider_clearance": 0.60,
        "snap_lip": False,
        "strip_thickness": 0.70,
        "rib_radius": 0.75,
    },
    "fdm-medium": {
        "clip_clearance": 0.42,
        "slider_clearance": 0.45,
        "snap_lip": True,
    },
    "fdm-tight": {
        "clip_clearance": 0.28,
        "slider_clearance": 0.30,
        "snap_lip": True,
    },
    "tpu-strip": {
        "strip_thickness": 0.65,
        "rib_radius": 0.70,
        "clip_wall": 0.85,
        "snap_lip": False,
    },
    "pla-slider": {
        "slider_plate_thickness": 2.2,
        "slider_wall_thickness": 2.0,
        "slider_wall_height": 6.5,
        "slider_clearance": 0.60,
    },
    "reference-like": {
        "teeth": 10,
        "pitch": 4.6,
        "strip_width": 17.0,
        "strip_thickness": 0.75,
        "rib_radius": 0.85,
        "rib_y": 1.35,
        "strip_style": "ladder",
        "latch_style": "none",
        "rail_width": 1.25,
        "clip_clearance": 0.60,
        "slider_clearance": 0.80,
        "slider_length": 45.0,
        "slider_wall_height": 7.0,
        "screw_boss_radius": 4.2,
        "screw_hole_radius": 1.7,
        "snap_lip": False,
    },
}


def preset_names() -> list[str]:
    return sorted(PRESETS)


def apply_preset(config: YZipperConfig, name: str | None) -> YZipperConfig:
    if not name:
        return config
    try:
        updates = PRESETS[name]
    except KeyError as exc:
        raise ValueError(f"unknown preset {name!r}; choose from {', '.join(preset_names())}") from exc
    return config.with_updates(**updates)
