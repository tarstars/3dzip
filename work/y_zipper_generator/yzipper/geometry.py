from __future__ import annotations

import math

import numpy as np
import trimesh


def equilateral_vertices(side_len: float) -> list[np.ndarray]:
    height = math.sqrt(3.0) / 2.0 * side_len
    return [
        np.array([-side_len / 2.0, -height / 3.0]),
        np.array([side_len / 2.0, -height / 3.0]),
        np.array([0.0, 2.0 * height / 3.0]),
    ]


def transform_flat_panel_to_triangle(mesh: trimesh.Trimesh, side_index: int, side_len: float) -> trimesh.Trimesh:
    """Map one flat strip panel onto one side of an equilateral triangular beam preview."""
    pts = equilateral_vertices(side_len)
    p0 = pts[side_index]
    p1 = pts[(side_index + 1) % 3]
    center = (p0 + p1) / 2.0
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    normal = np.array([u[1], -u[0]])
    if np.dot(normal, center) < 0:
        normal = -normal

    out = mesh.copy()
    vertices = out.vertices.copy()
    x_local = vertices[:, 0]
    y_local = vertices[:, 1]
    z_local = vertices[:, 2]
    cross_section = center[None, :] + x_local[:, None] * u[None, :] + z_local[:, None] * normal[None, :]
    out.vertices = np.column_stack([cross_section[:, 0], y_local, cross_section[:, 1]])
    return out

