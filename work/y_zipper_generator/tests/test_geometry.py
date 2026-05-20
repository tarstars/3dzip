from __future__ import annotations

import numpy as np

from yzipper.config import YZipperConfig
from yzipper.geometry import equilateral_vertices
from yzipper.strip import make_strip


def test_equilateral_vertices_are_120_degree_compatible() -> None:
    pts = equilateral_vertices(18.0)
    lengths = [np.linalg.norm(pts[(idx + 1) % 3] - pts[idx]) for idx in range(3)]
    assert lengths == pytest_approx_list([18.0, 18.0, 18.0])


def test_strip_length_tracks_tooth_count_and_pitch() -> None:
    config = YZipperConfig(teeth=7, pitch=4.5, margin=6.0)
    mesh = make_strip(config)
    extents = mesh.bounds[1] - mesh.bounds[0]
    assert extents[1] == pytest_approx(config.strip_length)


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, abs=1e-6)


def pytest_approx_list(values: list[float]):
    import pytest

    return pytest.approx(values, abs=1e-6)

