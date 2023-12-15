#include <Servo.h>

// set pin numbers:
const int SERVO_X_PIN = 10;
const int SERVO_Y_PIN = 9;
const int TRIGGER_PIN = 11;

Servo servoX;  // Servo for LEFT and RIGHT
Servo servoY;  // Servo for UP and DOWN

int posX = 90; // Initial position for servoY
int posY = 90; // Initial position for servoX

void setup() {
  servoY.attach(SERVO_X_PIN); // Attach servoY to pin 9
  servoX.attach(SERVO_Y_PIN); // Attach servoX to pin 10
  servoY.write(posX); // Set initial position for servoY
  servoX.write(posY); // Set initial position for servoX
  Serial.begin(9600); // Start serial communication
}

void updateServo(Servo &servo, int &position, int change) {
  position += change;
  position = max(0, min(180, position)); // Constrain position between 0 and 180
  servo.write(position);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');

    if (command == "UP") {
      updateServo(servoY, posX, -10); // Decrease position by 10
    } else if (command == "DOWN") {
      updateServo(servoY, posX, 10); // Increase position by 10
    } else if (command == "LEFT") {
      updateServo(servoX, posY, -10); // Decrease position by 10
    } else if (command == "RIGHT") {
      updateServo(servoX, posY, 10); // Increase position by 10
    } else if (command.startsWith("SHOOT")) {
      int duration = command.substring(6).toInt();
      digitalWrite(TRIGGER_PIN, HIGH); // Assuming trigger is connected to pin TRIGGER_PIN
      delay(duration);
      digitalWrite(TRIGGER_PIN, LOW);
    }
  }
}
