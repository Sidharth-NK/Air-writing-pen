"""
IMU Visualiser Module

Real-time 3D orientation visualization from IMU sensor data via serial connection.
Uses Madgwick filter quaternion output to compute yaw/pitch/roll and visualize
cursor movement on a 2D screen with path history.

Serial format: comma-separated quaternion values (q0,q1,q2,q3)
"""

import serial
import math
import sys
import logging
from typing import Optional, Tuple
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore

logger = logging.getLogger(__name__)

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

GAIN_X = 18.0     
GAIN_Y = 18.0     
ALPHA = 0.2
DEADZONE = 0.02


class IMUVisualiser:
    """
    Real-time IMU orientation visualizer with cursor tracking.
    
    Reads quaternion data from serial port, computes yaw/pitch/roll angles,
    applies smoothing and deadzone filtering, and displays cursor path on screen.
    Supports roll-based screen rotation for immersive control.
    """
    def __init__(self) -> None:
        logger.info("Init started...")

        # Serial init
        self.ser = None
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
            self.ser.reset_input_buffer()
            logger.info("Serial port %s opened: %s", SERIAL_PORT, self.ser.is_open)
        except serial.SerialException as e:
            logger.error("Failed to open serial port %s at %d baud: %s", 
                        SERIAL_PORT, BAUD_RATE, e)
            raise

        # GUI Window
        self.win = pg.GraphicsLayoutWidget(show=True, title="IMU VISUALISER")
        self.win.resize(1000, 700)

        self.plot = self.win.addPlot(title="Drawing Canvas")
        self.plot.setXRange(-500, 500)
        self.plot.setYRange(-500, 500)
        self.plot.setLabel("bottom", "Screen X (Yaw)")
        self.plot.setLabel("left", "Screen Y (Pitch)")

        # State variables
        self.cursor_x = 0
        self.cursor_y = 0

        self.prev_yaw = None
        self.prev_pitch = None

        self.avg_delta_yaw = 0
        self.avg_delta_pitch = 0

        self.path_x = []
        self.path_y = []
        
        # Create persistent plot items for performance
        self.path_item = self.plot.plot([], [], pen='y')
        self.cursor_item = self.plot.plot([], [], symbol='o', symbolBrush='r', symbolSize=10)

        logger.info("Initialised state variables.")

        # Timer loop 100 Hz
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.start(10)
    
            

    def read_packet(self) -> Optional[Tuple[float,float, float, float]]:
        """Read and parse quaternion from serial port.
        
        Returns:
            Tuple of (q0, q1, q2, q3) if valid data received, None otherwise.
        """
        line = self.ser.readline().decode(errors="ignore").strip()
        if not line:
            return None

        parts = line.split(",")
        if len(parts) < 4:
            return None

        try:
            q0, q1, q2, q3 = map(float, parts[:4])
        except ValueError:
            logger.debug("Couldn't parse floats from serial line: %r", line)
            return None

        return q0, q1, q2, q3

    def compute_orientation(self, q: Tuple[float, float, float, float]) -> Tuple[float, float, float]:
        """
        Convert quaternion to Euler angles (yaw, pitch, roll) in degrees..
        Args:
            q: Tuple of (q0, q1, q2, q3) quaternion components.
        Returns:
            Tuple of (yaw_deg, pitch_deg, roll_deg).
        """
        q0, q1, q2, q3 = q

        calc_roll = math.atan2(q0*q1 + q2*q3, 0.5 - (q1*q1 + q2*q2))

        pitch_arg = -2 * (q1*q3 - q0*q2)
        pitch_arg = max(min(pitch_arg, 1.0), -1.0)
        calc_pitch = math.asin(pitch_arg)
        
        calc_yaw = math.atan2(q1*q2 + q0*q3, 0.5 - (q2*q2 + q3*q3))

        # AXIS SWAP
        current_roll  = math.degrees(calc_pitch)
        current_pitch = math.degrees(calc_roll)
        current_yaw   = math.degrees(calc_yaw)

        return current_yaw, current_pitch, current_roll

    def compute_motion(self, yaw: float, pitch: float) -> Tuple[float, float]:
        """Compute screen motion delta from yaw and pitch angles.
        
         Applies wrap-around correction, exponential smoothing, and deadzone filtering.
         
         Args:
            yaw: Current yaw angle in degrees.
            pitch: Current pitch angle in degrees.
            
        Returns:
            Tuple of (dx, dy) screen motion deltas.
        """
        if self.prev_yaw is None:
            self.prev_yaw = yaw
            self.prev_pitch = pitch
            return 0, 0

        raw_delta_yaw = yaw - self.prev_yaw
        raw_delta_pitch = pitch - self.prev_pitch

        # Wrap-around correction
        if raw_delta_yaw > 180: raw_delta_yaw -= 360
        if raw_delta_yaw < -180: raw_delta_yaw += 360
        if raw_delta_pitch > 180: raw_delta_pitch -= 360
        if raw_delta_pitch < -180: raw_delta_pitch += 360

        # Smoothing
        self.avg_delta_yaw = ALPHA * raw_delta_yaw + (1 - ALPHA) * self.avg_delta_yaw
        self.avg_delta_pitch = ALPHA * raw_delta_pitch + (1 - ALPHA) * self.avg_delta_pitch

        # Deadzone
        move_yaw = 0 if abs(self.avg_delta_yaw) < DEADZONE else self.avg_delta_yaw
        move_pitch = 0 if abs(self.avg_delta_pitch) < DEADZONE else self.avg_delta_pitch

        # Screen movement 
        dx = -move_yaw * GAIN_X
        dy =  move_pitch * GAIN_Y

        self.prev_yaw = yaw
        self.prev_pitch = pitch

        return dx, dy

    def update_screen(self, dx: float, dy: float, roll_deg: float) -> None:
        """Update cursor position and render path on screen.
        
        Applies roll-based rotation to motion vector, updates cursor position,
        maintains path history, and redraws plot.
        
        Args:
            dx: Unrotated X motion delta.
            dy: Unrotated Y motion delta.
            roll_deg: Roll angle in degrees for motion rotation.
        """
        roll_rad = math.radians(roll_deg)

        # Rotate motion by roll angle
        dx2 = dx * math.cos(roll_rad) - dy * math.sin(roll_rad)
        dy2 = dx * math.sin(roll_rad) + dy * math.cos(roll_rad)

        # Update cursor
        self.cursor_x += dx2
        self.cursor_y += dy2

        self.path_x.append(self.cursor_x)
        self.path_y.append(self.cursor_y)

        if len(self.path_x) > 400:
            self.path_x.pop(0)
            self.path_y.pop(0)

        # Update persistent plot items (much faster than recreating)
        self.path_item.setData(self.path_x, self.path_y)
        self.cursor_item.setData([self.cursor_x], [self.cursor_y])

    def loop(self) -> None:
        """Main event loop: read sensor, compute orientation, update display."""
        packet = self.read_packet()
        if not packet:
            return

        yaw, pitch, roll = self.compute_orientation(packet)
        dx, dy = self.compute_motion(yaw, pitch)
        self.update_screen(dx, dy, roll)
    
    
    def close(self) -> None:
        """Clean up resources: stop timer and close serial port."""
        self.timer.stop()
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
                logger.info("Closed serial port")
        except Exception:
            logger.exception("Error closing serial")

if __name__ == "__main__":
    # Configure logging once at entry point
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    
    app = QtWidgets.QApplication([])
    vis = IMUVisualiser()
    
    # Connect cleanup on app quit
    app.aboutToQuit.connect(vis.close)
    
    sys.exit(app.exec_())
