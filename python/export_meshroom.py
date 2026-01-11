"""export_meshroom.py

Helpers to prepare RGB images and metadata for Meshroom / COLMAP.
"""
from __future__ import annotations

import shutil
from pathlib import Path
import json
from typing import List
import logging

logger = logging.getLogger(__name__)


def prepare_meshroom_dataset(rgb_root: str, out_dir: str, poses_as_separate_folders: bool = True) -> None:
    """Organize images into a dataset directory for Meshroom/COLMAP.

    If poses_as_separate_folders is True, images from each pose are stored in separate sub-folders.
    """
    root = Path(rgb_root)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for pose_dir in sorted(root.iterdir()):
        if not pose_dir.is_dir():
            continue
        if poses_as_separate_folders:
            dest = out / pose_dir.name
            dest.mkdir(parents=True, exist_ok=True)
            for img in pose_dir.glob('*.jpg'):
                shutil.copy2(img, dest / img.name)
        else:
            for img in pose_dir.glob('*.jpg'):
                shutil.copy2(img, out / f'{pose_dir.name}_{img.name}')
    logger.info("Prepared meshroom dataset at %s", out)


def write_camera_intrinsics(camera_matrix, dist_coeffs, out_file):
    data = {'camera_matrix': camera_matrix.tolist(), 'dist_coeffs': dist_coeffs.tolist()}
    Path(out_file).write_text(json.dumps(data))
    logger.info("Saved intrinsics to %s", out_file)
