"""triangulation.py

Triangulation utilities: undistort pixels, cast rays, intersect with laser plane.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple, List

import numpy as np
import cv2
from .utils.geometry import ray_plane_intersection, normalize
import logging

logger = logging.getLogger(__name__)


class Triangulator:
    def __init__(self, intrinsics_file: str, laser_plane_file: str):
        self.intrinsics_file = Path(intrinsics_file)
        self.laser_plane_file = Path(laser_plane_file)
        self._load_intrinsics()
        self._load_laser_plane()

    def _load_intrinsics(self) -> None:
        data = json.loads(self.intrinsics_file.read_text())
        self.camera_matrix = np.array(data["camera_matrix"])
        self.dist_coeffs = np.array(data.get("dist_coeffs", [0, 0, 0, 0, 0]))
        logger.debug("Loaded intrinsics from %s", self.intrinsics_file)

    def _load_laser_plane(self) -> None:
        data = json.loads(self.laser_plane_file.read_text())
        # plane stored as {"normal": [nx,ny,nz], "d": d}
        self.plane_normal = np.array(data["normal"], dtype=float)
        self.plane_d = float(data["d"])
        logger.debug("Loaded laser plane from %s", self.laser_plane_file)

    def undistort_point(self, x: float, y: float) -> np.ndarray:
        # return normalized camera ray direction
        pts = np.array([[[x, y]]], dtype=float)
        und = cv2.undistortPoints(pts, self.camera_matrix, self.dist_coeffs, P=self.camera_matrix)
        px = und[0, 0, 0]
        py = und[0, 0, 1]
        # backproject to camera coordinates (z = 1)
        cam_pt = np.array([px, py, 1.0], dtype=float)
        ray = normalize(cam_pt)
        return ray

    def pixel_line_to_points(self, pixel_coords: "numpy.ndarray") -> "numpy.ndarray":
        """Given Nx2 pixel coords (x,y) return Nx3 world points from ray-plane intersection (camera at origin).

        Note: We assume camera at origin and laser plane is in same camera-centric coordinates. If extrinsics are present, they should be applied by caller.
        """
        pts3 = []
        for x, y in pixel_coords:
            ray = self.undistort_point(float(x), float(y))
            origin = np.array([0.0, 0.0, 0.0])
            hit, p = ray_plane_intersection(origin, ray, self.plane_normal, self.plane_d)
            if hit:
                pts3.append(p)
        if len(pts3) == 0:
            return np.zeros((0, 3), dtype=float)
        return np.vstack(pts3)
