from __future__ import annotations

from pathlib import Path

from yzipper.config import YZipperConfig, validate_config
from yzipper.mesh import export_stl
from yzipper.presets import apply_preset
from yzipper.slider import make_slider
from yzipper.strip import make_strip


def main() -> None:
    config = apply_preset(YZipperConfig(), "fdm-loose").with_updates(teeth=8)
    validate_config(config)
    out = Path("output/example_coupon")
    export_stl(make_strip(config), out / "strip_teeth8_pitch5_clearance055.stl")
    export_stl(make_slider(config), out / "slider_clearance060_len42.stl")
    print(f"Wrote example coupon files to {out.resolve()}")


if __name__ == "__main__":
    main()

