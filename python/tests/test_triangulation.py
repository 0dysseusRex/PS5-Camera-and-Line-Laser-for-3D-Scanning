import numpy as np
from ..triangulation import Triangulator
from pathlib import Path


def test_triangulator_synthetic(tmp_path):
    # create simple intrinsics and a horizontal plane at z=1
    intr = {'camera_matrix': [[100,0,50],[0,100,50],[0,0,1]], 'dist_coeffs': [0,0,0,0,0]}
    lp = {'normal': [0,0,1], 'd': -1.0}
    intr_f = tmp_path / 'intr.json'
    lp_f = tmp_path / 'plane.json'
    intr_f.write_text(str(intr).replace("'", '"'))
    lp_f.write_text(str(lp).replace("'", '"'))
    tri = Triangulator(str(intr_f), str(lp_f))
    # pixel at principal point should intersect plane at z=1 -> ray [0,0,1] -> pt [0,0,1]
    pts = tri.pixel_line_to_points(np.array([[50,50]]))
    assert pts.shape[0] == 1
    assert abs(pts[0,2] - 1.0) < 1e-6
