import numpy as np
import cv2
from ..laser_extraction import LaserExtractor


def test_laser_extraction_synthetic():
    # create synthetic image with a bright line
    h, w = 480, 640
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for x in range(50, 590, 5):
        y = 200 + int(20.0*np.sin(x/50.0))
        img[y-1:y+2, x] = (0, 0, 255)
    le = LaserExtractor(blur_ksize=(5,5), threshold=50)
    pts = le.extract(img)
    assert pts.shape[0] > 50
    # x coordinates increasing
    assert np.all(np.diff(pts[:,0]) > 0)
