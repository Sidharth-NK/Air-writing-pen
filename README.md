# Air Writing Pen (V2 – Modular Architecture)

A modular implementation of an air-writing pen system using IMU sensor data.  
The system captures 3D motion through inertial sensors and converts it into meaningful strokes, gestures, and visualisations.

---

## Current Version – **V2 (Modular Architecture)**

This repository contains the refactored V2 release, featuring a clean, modular structure for improved maintainability and extensibility.

### Key Features
- Modular folder structure for calibration, firmware, and visualisation  
- Reusable Python modules  
- Improved clarity and maintainability  
- Better separation of concerns  
- Supports **BMI270** (accelerometer + gyroscope) and **BMM150** (magnetometer)

---

## Folder Structure

--

## Hardware Used
- **Arduino Nano BLE Sense Rev2**
- **BMI270** (accelerometer + gyroscope)
- **BMM150** (magnetometer)

Current implementation uses **6 DOF** (accelerometer + gyroscope).  
Magnetometer-based fusion (9-DOF) can be added easily due to the modular design.

---

## Legacy Version – **V1 (Single Script)**

The earlier single-file prototype is preserved for reference.

### V1 Highlights
- Basic IMU → stroke mapping  
- Minimal visualisation  
- Useful for understanding the first working version  

Check out the V1 tag:
```bash
git checkout v1.0.0
```

How to Run the Visualisation (V2)
1. Install dependencies:
```
pip install -r requirements.txt
```
2. Connect your IMU device

Arduino Nano BLE Sense Rev2 must be connected.

3. Run the visualisation script:
```
python visualisation/visual.py
```
