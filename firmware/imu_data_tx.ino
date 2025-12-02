/*
 * Main Orientation Sketch
 * This code reads IMU data, applies calibration, runs a 6-DOF Sensor Fusion algorithm,
 * and sends the resulting orientation (Quaternion) to the PC.
 */


#include <Arduino_BMI270_BMM150.h> 
#include "MadgwickAHRS.h"          

Madgwick myFilter;

// --- Gyroscope Offsets 
// float gyro_offset_x = -0.228068;
// float gyro_offset_y = -0.070373;
// float gyro_offset_z = -0.061361;

float gyro_offset_x = -0.199573;
float gyro_offset_y = -0.056409;
float gyro_offset_z = -0.037195;


void setup() {
  Serial.begin(115200); // 
  while (!Serial);

  if (!IMU.begin()) {
    while (1); 
  }
  float gyroRate = IMU.gyroscopeSampleRate();
  myFilter.begin(gyroRate);  // Gyroscope works at 104 Hz
}

void loop() {
  float ax, ay, az; 
  float gx, gy, gz; 

  if (IMU.accelerationAvailable() && 
      IMU.gyroscopeAvailable()) {

    // Read sensor data
    IMU.readAcceleration(ax, ay, az);
    IMU.readGyroscope(gx, gy, gz);
    
    // Apply gyro calibration
    gx -= gyro_offset_x;
    gy -= gyro_offset_y;
    gz -= gyro_offset_z;

    // Note: We pass 'gy' as the first argument and 'gx' as the second.
    // This fixes the hardware axis mismtch on the Nano 33 BLE Sense Rev2.
    myFilter.updateIMU(gy, gx, gz, ax, ay, az);

  // We get the 4D quaternion values (q0, q1,q2,q3).
  // Quaternions are beter than Roll/Pitch/Yaw because they don't suffer from Gimbal Lock.
  float q0 = myFilter.getQ0();
  float q1 = myFilter.getQ1();
  float q2 = myFilter.getQ2();
  float q3 = myFilter.getQ3();

  Serial.print(q0, 4);
  Serial.print(",");
  Serial.print(q1, 4);
  Serial.print(",");
  Serial.print(q2, 4);
  Serial.print(",");
  Serial.println(q3, 4);
  }
}
