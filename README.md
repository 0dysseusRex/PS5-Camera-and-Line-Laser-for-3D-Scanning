🌀 DIY Hybrid 3D Scanner
Open hardware. Open software. Open exploration.
This project is an open‑source, hybrid laser‑triangulation + photogrammetry 3D scanner built from affordable, widely available components. It’s designed to be easy to build, easy to modify, and powerful enough to scan small to medium‑sized objects with surprising accuracy.
The entire system — hardware, firmware, and software — is built around openness, remixability, and community contribution.
If you’d like to support development, you can find me here:
👉 https://ko-fi.com/0dysseusrex

🌟 Project Goals
- Create a fully open 3D scanning platform
- Use low‑cost, accessible hardware
- Combine laser triangulation (for geometry accuracy) with photogrammetry (for texture + fine detail)
- Provide a clean, modular codebase that anyone can extend
- Offer printable hardware so anyone with a 3D printer can build the rig
- Make calibration, scanning, and reconstruction as simple and repeatable as possible
This project is built for makers, researchers, hobbyists, and anyone who wants to explore 3D capture without expensive commercial systems.

🧰 Hardware Overview
The scanner uses:
- PS5 HD Camera
Dual 1080p lenses, great low‑light performance, and accessible via OpenCV after loading custom firmware.
- Line Laser Module
A simple 650nm line laser provides crisp depth slices for triangulation.
- Motorized Turntable (ESP32‑controlled)
A NEMA17 stepper + A4988/DRV8825 driver, controlled over WiFi via a lightweight HTTP API.
- Half‑Circle Arc Stand
A 3D‑printed arc that holds the camera + laser at three discrete positions, each aimed at the turntable center.
This eliminates the need for refocusing or recalibration between heights.
- LED Lighting Ring
Ensures consistent illumination for photogrammetry.
All mechanical parts are provided as STL and STEP files for easy printing and modification.

🧪 Software Overview
The software stack is written in Python and organized into modular components:
- Camera Capture
OpenCV interface for grabbing frames from the PS5 camera.
- Laser Line Extraction
Image processing pipeline to isolate the laser line and compute subpixel centers.
- Triangulation Engine
Converts laser pixels into 3D points using camera intrinsics and a calibrated laser plane.
- Turntable Control
Python client for the ESP32’s HTTP API.
- Scan Session Orchestrator
Coordinates:
- turntable rotation
- laser‑on depth capture
- laser‑off photogrammetry capture
- multi‑position scanning
- Point Cloud Merging
Uses Open3D for filtering, alignment, and fusion.
- Photogrammetry Export
Saves RGB frames in a structure compatible with Meshroom or COLMAP.

🔄 Scanning Workflow
- Choose a camera position on the arc stand (low, mid, or high).
- Laser Depth Pass
- Laser ON
- Turntable rotates in fixed increments
- Each frame → laser extraction → triangulation → point slice
- Photogrammetry Pass
- Laser OFF
- Same angles
- Capture RGB frames for texture + fine detail
- Repeat for all positions
(Up to three total)
- Merge all point clouds
Clean, align, and fuse into a single model.
- Run photogrammetry
Use Meshroom/COLMAP for high‑res texture and detail.
- Final Fusion
Combine depth + photogrammetry for the best of both worlds.

🏗️ Repository Structure
3d-scanner/
├── LICENSES/
├── config/
├── hardware/
│   ├── esp32_turntable/
│   └── mechanical/
│       ├── arc_stand/
│       ├── camera_mount/
│       ├── laser_mount/
│       ├── turntable/
│       └── calibration_jigs/
├── python/
├── data/
└── output/


Each folder is documented and structured for clarity and ease of contribution.

🔓 Licensing
To keep the project maximally open:
- Software is licensed under Apache 2.0
- Hardware (STL/STEP) is licensed under CERN‑OHL‑P
This combination encourages remixing, commercial use, and community growth.
See the LICENSES/ folder for details.

💙 Support the Project
If you enjoy this work, want to help keep it going, or just want to buy me a coffee:
👉 https://ko-fi.com/0dysseusrex
Your support helps fund hardware, testing, and continued development.