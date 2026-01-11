"""pointcloud_merge.py

Merge point slices into a single point cloud using Open3D.
"""
from __future__ import annotations

import open3d as o3d
import numpy as np
from pathlib import Path
from typing import List
import json
import logging

logger = logging.getLogger(__name__)


def load_slices(slice_dir: str) -> List[np.ndarray]:
    p = Path(slice_dir)
    pts = []
    for f in sorted(p.glob('*.npz')):
        data = np.load(f)
        arr = data['points']
        if arr.size:
            pts.append(arr)
    return pts


def merge_pointclouds(slice_dirs: List[str], out_file: str, voxel_size: float = 0.002) -> None:
    all_points = []
    for sd in slice_dirs:
        pts = load_slices(sd)
        for a in pts:
            if a.size:
                all_points.append(a)
    if len(all_points) == 0:
        logger.warning("No points found to merge")
        return
    pts = np.vstack(all_points)
    pcd = o3d.geometry.PointCloud(o3d.utility.Vector3dVector(pts))
    pcd_down = pcd.voxel_down_sample(voxel_size)
    pcd_clean, ind = pcd_down.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
    o3d.io.write_point_cloud(out_file, pcd_clean)
    logger.info("Wrote merged pointcloud to %s (original pts=%d, final=%d)", out_file, len(pts), len(pcd_clean.points))
