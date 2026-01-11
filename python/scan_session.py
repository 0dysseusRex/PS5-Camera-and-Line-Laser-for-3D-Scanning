"""scan_session.py

Orchestrates multi-pose scan sessions (laser depth + photogrammetry).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import List, Dict, Optional

import numpy as np
from .camera_capture import CameraCapture
from .laser_extraction import LaserExtractor
from .triangulation import Triangulator
from .turntable_client import TurntableClient

logger = logging.getLogger(__name__)


class LaserController:
    """Placeholder for laser control. Replace with GPIO or USB control as needed."""

    def __init__(self):
        self.on = False

    def turn_on(self):
        self.on = True
        logger.info("Laser turned ON")

    def turn_off(self):
        self.on = False
        logger.info("Laser turned OFF")


class ScanSession:
    def __init__(self, config_file: str, out_dir: str = 'output'):
        cfg = json.loads(Path(config_file).read_text())
        self.poses: List[str] = cfg.get('poses', ['low', 'mid', 'high'])
        self.degrees_per_step: float = cfg.get('degrees_per_step', 10.0)
        self.angles = list(np.arange(0, 360, self.degrees_per_step))
        self.intrinsics_dir = Path(cfg.get('intrinsics_dir', 'config'))
        self.laser_planes_dir = Path(cfg.get('laser_planes_dir', 'config'))
        self.out_dir = Path(out_dir)
        self.turntable = TurntableClient(cfg.get('turntable_base_url', 'http://192.168.4.1'))
        self.camera = CameraCapture(device_index=cfg.get('camera_index', 0))
        self.laser = LaserController()
        self.laser_extractor = LaserExtractor()

    def _pose_intrinsics(self, pose_id: str) -> str:
        return str(self.intrinsics_dir / f'camera_intrinsics_{pose_id}.json')

    def _pose_laser_plane(self, pose_id: str) -> str:
        return str(self.laser_planes_dir / f'laser_plane_{pose_id}.json')

    def run(self):
        for pose in self.poses:
            input(f"Move camera/laser to pose '{pose}' and press ENTER when ready...")
            logger.info("Starting pose %s", pose)
            # Stage 1: laser depth
            self.laser.turn_on()
            triang = Triangulator(self._pose_intrinsics(pose), self._pose_laser_plane(pose))
            slice_dir = self.out_dir / 'slices' / pose
            slice_dir.mkdir(parents=True, exist_ok=True)
            for angle in self.angles:
                self.turntable.rotate_to(angle)
                self.turntable.wait_until_idle()
                frame, meta = self.camera.capture_frame(pose_id=pose)
                if frame is None:
                    continue
                pixels = self.laser_extractor.extract(frame)
                points = triang.pixel_line_to_points(pixels)
                # save slice
                slice_file = slice_dir / f'slice_{int(angle):03d}.npz'
                np.savez_compressed(slice_file, points=points, pose=pose, angle=angle, timestamp=meta['timestamp'])
                logger.info("Saved slice %s with %d points", slice_file, len(points))

            self.laser.turn_off()

            # Stage 2: photogrammetry RGB
            rgb_dir = self.out_dir / 'rgb' / pose
            rgb_dir.mkdir(parents=True, exist_ok=True)
            for angle in self.angles:
                self.turntable.rotate_to(angle)
                self.turntable.wait_until_idle()
                frame, meta = self.camera.capture_frame(pose_id=pose)
                if frame is None:
                    continue
                img_path = rgb_dir / f'img_{int(angle):03d}.jpg'
                self.camera.save_frame(frame, str(img_path), pose_id=pose)
                # Write simple metadata sidecar
                meta_file = img_path.with_suffix('.json')
                meta.update({'pose': pose, 'angle': angle})
                meta_file.write_text(json.dumps(meta))
                logger.info("Saved RGB %s", img_path)

        logger.info("ScanSession run complete")
