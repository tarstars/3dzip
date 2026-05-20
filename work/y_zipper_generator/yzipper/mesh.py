from __future__ import annotations

import math
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np
import trimesh


Vec3 = Tuple[float, float, float]


def box_mesh(size: Vec3, center: Vec3) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=size)
    mesh.apply_translation(center)
    return mesh


def cylinder_along(axis: str, radius: float, length: float, center: Vec3, sections: int = 18) -> trimesh.Trimesh:
    mesh = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    if axis.lower() == "x":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2.0, [0, 1, 0]))
    elif axis.lower() == "y":
        mesh.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2.0, [1, 0, 0]))
    elif axis.lower() != "z":
        raise ValueError("axis must be 'x', 'y', or 'z'")
    mesh.apply_translation(center)
    return mesh


def annular_cylinder_z(
    outer_radius: float,
    inner_radius: float,
    height: float,
    center: Vec3,
    sections: int = 32,
) -> trimesh.Trimesh:
    """Create a printable washer/ring mesh without boolean subtraction."""
    if inner_radius <= 0 or outer_radius <= inner_radius:
        raise ValueError("annular cylinder requires 0 < inner_radius < outer_radius")

    angles = np.linspace(0.0, math.tau, sections, endpoint=False)
    bottom_outer = np.column_stack([outer_radius * np.cos(angles), outer_radius * np.sin(angles), np.full(sections, -height / 2.0)])
    top_outer = np.column_stack([outer_radius * np.cos(angles), outer_radius * np.sin(angles), np.full(sections, height / 2.0)])
    bottom_inner = np.column_stack([inner_radius * np.cos(angles), inner_radius * np.sin(angles), np.full(sections, -height / 2.0)])
    top_inner = np.column_stack([inner_radius * np.cos(angles), inner_radius * np.sin(angles), np.full(sections, height / 2.0)])
    vertices = np.vstack([bottom_outer, top_outer, bottom_inner, top_inner])

    faces: list[list[int]] = []
    bo = 0
    to = sections
    bi = sections * 2
    ti = sections * 3
    for idx in range(sections):
        nxt = (idx + 1) % sections
        faces.append([bo + idx, bo + nxt, to + nxt])
        faces.append([bo + idx, to + nxt, to + idx])
        faces.append([bi + idx, ti + idx, ti + nxt])
        faces.append([bi + idx, ti + nxt, bi + nxt])
        faces.append([to + idx, to + nxt, ti + nxt])
        faces.append([to + idx, ti + nxt, ti + idx])
        faces.append([bo + idx, bi + nxt, bo + nxt])
        faces.append([bo + idx, bi + idx, bi + nxt])

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(faces), process=False)
    mesh.apply_translation(center)
    return mesh


def oriented_box(
    length: float,
    width: float,
    height: float,
    center_xy: tuple[float, float],
    angle_rad: float,
    z_center: float,
) -> trimesh.Trimesh:
    mesh = trimesh.creation.box(extents=[length, width, height])
    mesh.apply_transform(trimesh.transformations.rotation_matrix(angle_rad, [0, 0, 1]))
    mesh.apply_translation([center_xy[0], center_xy[1], z_center])
    return mesh


def concat(meshes: Iterable[trimesh.Trimesh]) -> trimesh.Trimesh:
    parts = [m for m in meshes if m is not None and len(m.vertices) > 0]
    if not parts:
        return trimesh.Trimesh(vertices=[], faces=[])
    out = trimesh.util.concatenate(parts)
    out.remove_unreferenced_vertices()
    return out


def move_to_bed(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    out = mesh.copy()
    if len(out.vertices):
        out.apply_translation([0.0, 0.0, -float(out.bounds[0, 2])])
    return out


def export_stl(mesh: trimesh.Trimesh, path: Path) -> None:
    if not np.isfinite(mesh.vertices).all():
        raise ValueError(f"mesh for {path} has non-finite vertices")
    path.parent.mkdir(parents=True, exist_ok=True)
    move_to_bed(mesh).export(path)


def mesh_stats(mesh: trimesh.Trimesh) -> dict[str, object]:
    if len(mesh.vertices) == 0:
        return {
            "vertices": 0,
            "faces": 0,
            "finite": True,
            "watertight": False,
            "volume": 0.0,
            "bounds_min": [0.0, 0.0, 0.0],
            "bounds_max": [0.0, 0.0, 0.0],
            "extents": [0.0, 0.0, 0.0],
        }
    bounds = mesh.bounds
    return {
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "finite": bool(np.isfinite(mesh.vertices).all()),
        "watertight": bool(mesh.is_watertight),
        "volume": float(mesh.volume),
        "bounds_min": [round(float(v), 3) for v in bounds[0]],
        "bounds_max": [round(float(v), 3) for v in bounds[1]],
        "extents": [round(float(v), 3) for v in bounds[1] - bounds[0]],
    }
