"""calibration.py

Camera intrinsics and laser plane calibration helpers (basic implementations).
"""
from __future__ import annotations

import cv2
import numpy as np
import json
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def calibrate_camera_from_images(image_files: List[str], pattern_size=(9,6), square_size=0.025, out_file: str = 'camera_intrinsics.json') -> dict:
    """Calibrate camera using chessboard images and save intrinsics.

    Returns dict with camera_matrix and dist_coeffs.
    """
    objp = np.zeros((pattern_size[0]*pattern_size[1], 3), np.float32)
    objp[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    objp *= square_size

    objpoints = []
    imgpoints = []
    for f in image_files:
        img = cv2.imread(f)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, pattern_size)
        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), (cv2.TermCriteria_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

    if len(objpoints) < 3:
        raise RuntimeError('Not enough calibration images with detected pattern')

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    data = {'camera_matrix': mtx.tolist(), 'dist_coeffs': dist.tolist()}
    Path(out_file).write_text(json.dumps(data))
    logger.info("Saved intrinsics to %s", out_file)
    return data


def estimate_laser_plane_from_points(points: List['numpy.ndarray'], out_file: str = 'laser_plane.json') -> dict:
    """Estimate a plane from stacked 3D points (simple SVD-based fit).

    plane: n.x + d = 0
    """
    pts = np.vstack([p.reshape(-1, 3) for p in points if p.size])
    centroid = pts.mean(axis=0)
    uu, dd, vv = np.linalg.svd(pts - centroid)
    normal = vv[-1]
    d = -normal.dot(centroid)
    data = {'normal': normal.tolist(), 'd': float(d)}
    Path(out_file).write_text(json.dumps(data))
    logger.info("Saved laser plane to %s", out_file)
    return data
