from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from .mesh import mesh_stats


def load_stl_stats(path: Path) -> dict[str, object]:
    mesh = trimesh.load_mesh(path, force="mesh")
    return mesh_stats(mesh)


def assert_plausible_mesh(mesh: trimesh.Trimesh, max_extent: float = 250.0) -> None:
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("mesh is empty")
    if not np.isfinite(mesh.vertices).all():
        raise ValueError("mesh has non-finite vertices")
    extents = mesh.bounds[1] - mesh.bounds[0]
    if np.any(extents <= 0):
        raise ValueError(f"mesh has non-positive extent: {extents}")
    if np.any(extents > max_extent):
        raise ValueError(f"mesh extents look too large for a coupon: {extents}")

