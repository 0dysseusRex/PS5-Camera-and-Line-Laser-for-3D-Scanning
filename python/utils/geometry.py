"""geometry.py

Geometry helpers: ray-plane intersection, plane representation helpers.
"""
from __future__ import annotations

import numpy as np
from typing import Tuple


def ray_plane_intersection(ray_origin: np.ndarray, ray_dir: np.ndarray, plane_normal: np.ndarray, plane_d: float) -> Tuple[bool, np.ndarray]:
    """Intersect ray with plane (plane: n.x + d = 0).

    ray_origin: (3,)
    ray_dir: (3,) (should be normalized or not; t computed accordingly)
    plane_normal: (3,)
    plane_d: float

    Returns (hit, point)
    """
    denom = plane_normal.dot(ray_dir)
    if abs(denom) < 1e-9:
        return False, np.zeros(3)
    t = -(plane_normal.dot(ray_origin) + plane_d) / denom
    if t < 0:
        # intersection behind camera
        return False, np.zeros(3)
    pt = ray_origin + t * ray_dir
    return True, pt


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        return v
    return v / n
