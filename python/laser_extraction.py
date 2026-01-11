"""laser_extraction.py

Extracts a laser line from frames.
"""
from __future__ import annotations

import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class LaserExtractor:
    def __init__(self, blur_ksize: Tuple[int, int] = (7, 7), threshold: int = 200):
        self.blur_ksize = blur_ksize
        self.threshold = threshold

    def extract(self, frame: "numpy.ndarray") -> "numpy.ndarray":
        """Return Nx2 array of pixel coordinates (x, y) for the detected laser line.

        Strategy:
        - Convert to grayscale
        - Gaussian blur
        - Threshold (bright laser)
        - For each column, compute intensity-weighted centroid of bright pixels (subpixel)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, self.blur_ksize, 0)
        _, thresh = cv2.threshold(blurred, self.threshold, 255, cv2.THRESH_BINARY)

        h, w = thresh.shape
        points = []
        for x in range(w):
            col = thresh[:, x]
            ys = np.nonzero(col)[0]
            if ys.size == 0:
                continue
            intensities = blurred[ys, x].astype(float)
            # weighted centroid in pixel coordinates
            y_centroid = (ys * intensities).sum() / (intensities.sum() + 1e-12)
            points.append((x, y_centroid))

        if len(points) == 0:
            logger.debug("No laser points extracted")
            return np.zeros((0, 2), dtype=float)

        return np.array(points, dtype=float)


if __name__ == "__main__":
    # simple test snippet
    import sys
    from pathlib import Path
    le = LaserExtractor()
    img_path = sys.argv[1] if len(sys.argv) > 1 else None
    if img_path:
        img = cv2.imread(img_path)
        pts = le.extract(img)
        print(f"Extracted {len(pts)} points")
