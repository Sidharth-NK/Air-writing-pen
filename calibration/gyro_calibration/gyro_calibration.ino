/*
 * Gyroscope Calibration Sketch
 * For Nano 33 BLE Sense Rev2 (using Arduino_BMI270_BMM150 library)
 * * Place your board on a flat, motionless surface and run this.
 * It will take 1000 readings and average them to find the
 * gyroscope's zero-offset (bias).
 */

#include <Arduino_BMI270_BMM150.h> 

const int numSamples = 1000;
float gx_offset = 0.0;
float gy_offset = 0.0;
float gz_offset = 0.0;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1); // Halt
  }

  Serial.println("Starting Gyroscope Calibration...");
  Serial.println("Keep the board perfectly still for a few seconds.");
  delay(1000);

  float sum_gx = 0;
  float sum_gy = 0;
  float sum_gz = 0;

  for (int i = 0; i < numSamples; i++) {
    float gx, gy, gz;
    
    // Wait for a new sample
    while(!IMU.gyroscopeAvailable()) { }
    
    IMU.readGyroscope(gx, gy, gz);
    sum_gx += gx;
    sum_gy += gy;
    sum_gz += gz;
    
    if(i % 100 == 0) {
      Serial.print(".");
    }
  }

  // Calculate the average (the bias)
  gx_offset = sum_gx / numSamples;
  gy_offset = sum_gy / numSamples;
  gz_offset = sum_gz / numSamples;

  Serial.println("\nCalibration Complete!");
  Serial.println("Copy these offset values into your main sketch:");
  Serial.print("float gyro_offset_x = "); Serial.print(gx_offset, 6); Serial.println(";");
  Serial.print("float gyro_offset_y = "); Serial.print(gy_offset, 6); Serial.println(";");
  Serial.print("float gyro_offset_z = "); Serial.print(gz_offset, 6); Serial.println(";");
}

void loop() {
  // Do nothing
}
