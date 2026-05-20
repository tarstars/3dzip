from __future__ import annotations

import pytest

from yzipper.config import ConfigError, YZipperConfig, validate_config
from yzipper.presets import apply_preset


def test_default_config_is_valid() -> None:
    validate_config(YZipperConfig())


def test_fdm_loose_preset_is_first_print_friendly() -> None:
    config = apply_preset(YZipperConfig(), "fdm-loose")
    assert config.teeth == 8
    assert config.clip_clearance == pytest.approx(0.55)
    assert config.slider_clearance == pytest.approx(0.60)
    assert config.snap_lip is False


def test_reference_like_preset_uses_ladder_strip() -> None:
    config = apply_preset(YZipperConfig(), "reference-like")
    validate_config(config)
    assert config.strip_style == "ladder"
    assert config.latch_style == "none"
    assert config.slider_clearance >= 0.6


def test_invalid_parameters_fail_clearly() -> None:
    with pytest.raises(ConfigError, match="teeth"):
        validate_config(YZipperConfig(teeth=0))


def test_ladder_bead_clip_combination_is_rejected() -> None:
    with pytest.raises(ConfigError, match="ladder"):
        validate_config(YZipperConfig(strip_style="ladder", latch_style="bead-clip"))
