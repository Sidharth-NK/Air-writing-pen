# Air Writing System

The **Air Writing System** captures 3D hand motion using inertial sensors and converts it into meaningful strokes, gestures, and visualisations in real time.  
The goal is to enable *natural, device-free writing and drawing in air* using orientation and motion sensing.

The final form factor is flexible. It can be implemented as a **ring, pen, or wearable controller**.  
The current prototype is designed around a **ring-based form factor** for intuitive finger-level motion capture.

---

## Concept Overview

At a high level, the system works as a **motion-to-stroke pipeline**:

**IMU Motion → Orientation Estimation → Motion Mapping → Stroke Visualisation**

1. **Motion Capture**  
   Inertial sensors measure angular velocity and linear acceleration of the hand.

2. **Sensor Fusion**  
   Raw IMU data is fused into a stable 3D orientation using a quaternion-based filter.

3. **Motion Interpretation**  
   Changes in orientation are converted into 2D screen movements.

4. **Visualisation**  
   The motion is rendered as a continuous drawing path, simulating air writing.

---

## Current Version – **V2 (Modular Architecture)**

Version 2 introduces a **modular and extensible architecture**, separating sensing, calibration, motion processing, and visualisation.

### Key Improvements
- Clean separation of firmware, calibration, and visualisation  
- Quaternion-based orientation pipeline  
- Reusable Python modules  
- Easier extension to gesture recognition and 9-DOF fusion  

---

## Core Algorithmic Flow (V2)

### 1. Orientation Estimation
- The IMU outputs orientation as **quaternions** (`q0, q1, q2, q3`)
- Quaternions avoid gimbal lock and provide smooth 3D rotation tracking
- Euler angles (**yaw, pitch, roll**) are derived for intuitive control

### 2. Motion Extraction
- **Yaw** → horizontal motion  
- **Pitch** → vertical motion  
- **Roll** → rotation of the motion frame (natural wrist rotation)

Only *changes* in orientation are used, not absolute angles, enabling relative motion tracking.

### 3. Signal Conditioning
To ensure smooth and usable writing:
- **Wrap-around correction** handles ±180° discontinuities
- **Exponential smoothing** reduces sensor noise
- **Deadzone filtering** eliminates micro jitter

### 4. Stroke Generation
- Filtered motion deltas are scaled and accumulated
- The cursor position forms a continuous path
- Recent stroke history is retained for real-time drawing feedback

---

## Hardware Used
- **Arduino Nano BLE Sense Rev2**
- **BMI270** – Accelerometer + Gyroscope
- **BMM150** – Magnetometer (optional)

Current implementation operates in **6-DOF mode** (accelerometer + gyroscope).  
The architecture is designed to easily support **9-DOF fusion** using the magnetometer for drift correction.

---

## Visualisation Module

The visualisation runs on a host PC and performs:
- Real-time serial data reception
- Quaternion → Euler conversion
- Motion filtering and mapping
- Live 2D stroke rendering

The result is an interactive canvas that directly reflects hand movement in air.

---

## How to Run (V2)

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Connect the IMU device (Arduino Nano BLE Sense Rev2)
Run the visualisation:
```bash
python visualisation/visual.py
```
## Legacy Version – V1 (Single Script Prototype)

The initial proof-of-concept implementation is preserved as V1.

### V1 Characteristics

- Single monolithic script
- Minimal processing and visualisation
- Useful for understanding the evolution of the system.

Checkout V1:
```bash
git checkout v1.0.0
```

## Future updates to bring
- Gesture, charachter and handwriting recognitions using Tiny ML models.
- Wearable UI interaction
- Create PCB for the custom ring form factor
- Create CAD design for the ring form factor
- Extend to different applications, AR/VR, pathological tremor detection, robotics/drone applications etc.
