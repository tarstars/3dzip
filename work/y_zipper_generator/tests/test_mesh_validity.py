from __future__ import annotations

from pathlib import Path

import trimesh

from yzipper.assembly import standard_part_meshes
from yzipper.config import YZipperConfig
from yzipper.presets import apply_preset
from yzipper.validate import assert_plausible_mesh, load_stl_stats


def test_generated_meshes_have_plausible_bounds() -> None:
    config = YZipperConfig(teeth=8)
    for mesh in standard_part_meshes(config).values():
        assert_plausible_mesh(mesh, max_extent=130.0)


def test_exported_strip_bounds_are_expected(tmp_path: Path) -> None:
    from yzipper.mesh import export_stl
    from yzipper.strip import make_strip

    config = YZipperConfig(teeth=8, pitch=5.0)
    path = tmp_path / "strip.stl"
    export_stl(make_strip(config), path)
    stats = load_stl_stats(path)
    assert stats["finite"] is True
    assert stats["faces"] > 0
    assert stats["extents"][1] == 50.0
    assert 18.0 < stats["extents"][0] < 25.0
    assert 4.0 < stats["extents"][2] < 6.5


def test_meshes_have_nonzero_area_or_volume() -> None:
    config = YZipperConfig(teeth=6)
    for mesh in standard_part_meshes(config).values():
        loaded = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces, process=False)
        assert loaded.area > 0
        assert abs(float(loaded.volume)) > 0


def test_reference_like_ladder_has_open_strip_bounds() -> None:
    config = apply_preset(YZipperConfig(), "reference-like")
    meshes = standard_part_meshes(config)
    strip_extents = meshes["strip"].bounds[1] - meshes["strip"].bounds[0]
    assert strip_extents[1] == config.strip_length
    assert 16.0 <= strip_extents[0] <= 19.0
    assert 2.0 <= strip_extents[2] <= 3.5
