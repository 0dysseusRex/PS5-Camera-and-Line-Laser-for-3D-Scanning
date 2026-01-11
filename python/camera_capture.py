"""camera_capture.py

Provides CameraCapture class to interface with a PS5 camera via OpenCV.
"""
from __future__ import annotations

import cv2
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict
import time

logger = logging.getLogger(__name__)


class CameraCapture:
    """Simple wrapper around OpenCV VideoCapture.

    - capture_frame() -> (frame, metadata)
    - save_frame(path)
    - set_resolution(width, height)

    Tag frames with an optional pose_id to keep per-pose images organized.
    """

    def __init__(self, device_index: int = 0, width: int = 1920, height: int = 1080):
        self.device_index = device_index
        self.cap = cv2.VideoCapture(device_index, cv2.CAP_ANY)
        self.width = width
        self.height = height
        self.set_resolution(width, height)

        if not self.cap.isOpened():
            logger.warning("Camera device %s not opened", device_index)

    def set_resolution(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        logger.debug("Resolution set to %dx%d", width, height)

    def capture_frame(self, pose_id: Optional[str] = None) -> Tuple[Optional["numpy.ndarray"], Dict]:
        """Capture a single frame and return (frame, metadata).

        metadata includes: timestamp, pose_id, resolution
        """
        ts = time.time()
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to read frame from camera")
            return None, {"timestamp": ts, "pose_id": pose_id}
        metadata = {"timestamp": ts, "pose_id": pose_id, "width": self.width, "height": self.height}
        return frame, metadata

    def save_frame(self, frame, path: str, pose_id: Optional[str] = None) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(p), frame)
        logger.info("Saved frame %s (pose=%s)", p, pose_id)
        return p

    def release(self) -> None:
        self.cap.release()
        logger.debug("Camera released")
