# DIY PS5 Camera + Line Laser 3D Scanner (Overview)

This project provides a modular Python stack and ESP32 firmware for a hybrid 3D scanner using laser triangulation and photogrammetry.

Quick start

1. Install Python deps:
   pip install -r requirements.txt

2. Edit `config/scan_settings.json` to set your turntable IP, camera index, poses, and step degrees.

3. Calibrate camera and laser per pose:
   - Use `python -c "from calibration import calibrate_camera_from_images; calibrate_camera_from_images([...])"`
   - Use `estimate_laser_plane_from_points` with sample slices.

4. Run a scan session:
   python -c "from scan_session import ScanSession; ScanSession('config/scan_settings.json').run()"

5. Merge slices:
   python -c "from pointcloud_merge import merge_pointclouds; merge_pointclouds(['output/slices/low','output/slices/mid','output/slices/high'],'output/merged_pointcloud.ply')"

Notes
- Move the camera/laser manually to each pose when prompted.
- For photogrammetry, use `output/rgb/<pose>` as input to Meshroom/COLMAP.
