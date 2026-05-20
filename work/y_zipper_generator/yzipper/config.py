from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


class ConfigError(ValueError):
    """Raised when parameters cannot produce a sensible printable model."""


@dataclass(frozen=True)
class YZipperConfig:
    """All dimensions are millimeters.

    Coordinate convention:
    - Flat strip: X is strip width, Y is strip length, Z is height above bed.
    - Zipped preview: Y remains beam length; X/Z form the triangular tube cross-section.
    - Slider: three U-channels lie in XY and are arranged 120 degrees apart.
    """

    teeth: int = 8
    pitch: float = 5.0
    strip_width: float = 16.0
    margin: float = 5.0
    strip_thickness: float = 0.70
    rib_radius: float = 0.75
    rib_y: float = 1.25
    strip_style: str = "membrane"
    latch_style: str = "bead-clip"
    rail_width: float = 1.20
    bead_radius: float = 1.05
    bead_segment: float | None = None
    clip_clearance: float = 0.55
    clip_wall: float = 0.85
    snap_lip: bool = False
    sections: int = 18
    plate_spacing: float = 8.0
    slider_clearance: float = 0.60
    slider_length: float = 42.0
    slider_plate_thickness: float = 2.2
    slider_wall_thickness: float = 2.0
    slider_wall_height: float = 6.5
    screw_boss_radius: float = 4.0
    screw_hole_radius: float = 1.65
    triangular_tube_size: float | None = None

    @property
    def strip_length(self) -> float:
        return 2.0 * self.margin + self.teeth * self.pitch

    @property
    def tooth_height(self) -> float:
        return 2.0 * self.rib_radius

    @property
    def tube_side(self) -> float:
        return self.triangular_tube_size if self.triangular_tube_size is not None else self.strip_width

    @property
    def bead_segment_length(self) -> float:
        return self.bead_segment if self.bead_segment is not None else self.pitch * 0.62

    @property
    def clip_depth(self) -> float:
        return self.bead_radius * 2.2 + self.clip_clearance

    @property
    def clip_slot_height(self) -> float:
        return self.bead_radius * 2.0 + self.clip_clearance

    @property
    def clip_height(self) -> float:
        return self.clip_slot_height + 2.0 * self.clip_wall

    def with_updates(self, **updates: Any) -> "YZipperConfig":
        return replace(self, **{k: v for k, v in updates.items() if v is not None})

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["strip_length"] = self.strip_length
        data["tooth_height"] = self.tooth_height
        data["tube_side"] = self.tube_side
        data["note"] = (
            "Experimental Y-zipper-inspired generator, not the official "
            "MIT/CSAIL geometry. Tune clearances for your printer/material."
        )
        return data


def validate_config(config: YZipperConfig) -> None:
    errors: list[str] = []

    def positive(name: str, value: float) -> None:
        if value <= 0:
            errors.append(f"{name} must be > 0 (got {value!r})")

    if config.teeth < 1:
        errors.append("teeth must be at least 1")
    if config.teeth > 80:
        errors.append("teeth must be 80 or less for this generator")

    for name in (
        "pitch",
        "strip_width",
        "margin",
        "strip_thickness",
        "rib_radius",
        "rib_y",
        "bead_radius",
        "rail_width",
        "clip_wall",
        "sections",
        "plate_spacing",
        "slider_clearance",
        "slider_length",
        "slider_plate_thickness",
        "slider_wall_thickness",
        "slider_wall_height",
        "screw_boss_radius",
        "screw_hole_radius",
        "tube_side",
    ):
        positive(name, float(getattr(config, name)))

    if config.strip_style not in {"membrane", "ladder"}:
        errors.append("strip_style must be 'membrane' or 'ladder'")
    if config.latch_style not in {"bead-clip", "none"}:
        errors.append("latch_style must be 'bead-clip' or 'none'")
    if config.strip_style == "ladder" and config.latch_style == "bead-clip":
        errors.append("ladder strip currently supports latch_style='none' only")
    if config.sections < 8:
        errors.append("sections must be at least 8")
    if config.pitch < max(2.0, config.rib_y * 1.8):
        errors.append("pitch is too small for the requested rib width")
    if config.bead_segment is not None and config.bead_segment > config.pitch * 0.95:
        errors.append("bead_segment must be shorter than one pitch")
    if config.strip_width < 6.0:
        errors.append("strip_width must be at least 6 mm")
    if config.strip_thickness < 0.35:
        errors.append("strip_thickness below 0.35 mm is not practical for first FDM tests")
    if config.rib_radius > config.strip_width / 3.0:
        errors.append("rib_radius is too large relative to strip_width")
    if config.rail_width * 2.5 >= config.strip_width:
        errors.append("rail_width leaves too little open span in the strip")
    if not (0.15 <= config.clip_clearance <= 1.5):
        errors.append("clip_clearance should be between 0.15 and 1.5 mm")
    if not (0.20 <= config.slider_clearance <= 2.0):
        errors.append("slider_clearance should be between 0.20 and 2.0 mm")
    if config.slider_length < config.tube_side * 1.5:
        errors.append("slider_length should be at least 1.5x triangular_tube_size/strip_width")
    if config.screw_hole_radius >= config.screw_boss_radius:
        errors.append("screw_hole_radius must be smaller than screw_boss_radius")
    if config.strip_length > 500:
        errors.append("strip length exceeds 500 mm; generate a shorter coupon first")

    if errors:
        raise ConfigError("; ".join(errors))
