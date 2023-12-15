#include <Servo.h>

/*

servo x setup

*/
const int SERVO_X_PIN = 6;
const int SERVO_X_MAX = 180;
const int SERVO_X_MIN = 90;

/*

servo y setup

*/
const int SERVO_Y_PIN = 5;
const int SERVO_Y_MAX = 30;
const int SERVO_Y_MIN = 0;

const int TRIGGER_PIN = 9;

const int increment = 1;

Servo servoX; // Servo for LEFT and RIGHT
Servo servoY; // Servo for UP and DOWN

int posX = 180; // Initial position for servoY
int posY = 0;   // Initial position for servoX

void setup()
{
  servoY.attach(SERVO_Y_PIN); // Attach servoY to pin 9
  servoX.attach(SERVO_X_PIN); // Attach servoX to pin 10
  servoY.write(posY);         // Set initial position for servoY
  servoX.write(posX);         // Set initial position for servoX
  pinMode(TRIGGER_PIN, OUTPUT);
  Serial.begin(9600); // Start serial communication
}

int clamp(int v, int imin, int imax)
{
  return max(imin, min(imax, v));
}

void loop()
{
  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');

    if (command == "UP")
    {
      posY = clamp(posY - increment, SERVO_Y_MIN, SERVO_Y_MAX);
      servoY.write(posY);
    }
    else if (command == "DOWN")
    {
      posY = clamp(posY + increment, SERVO_Y_MIN, SERVO_Y_MAX);
      servoY.write(posY);
    }
    else if (command == "LEFT")
    {
      posX = clamp(posX + increment, SERVO_X_MIN, SERVO_X_MAX);
      servoX.write(posX);
    }
    else if (command == "RIGHT")
    {
      posX = clamp(posX - increment, SERVO_X_MIN, SERVO_X_MAX);
      servoX.write(posX);
    }
    else if (command.startsWith("SHOOT"))
    {
      int duration = command.substring(6).toInt();
      digitalWrite(TRIGGER_PIN, HIGH); // Assuming trigger is connected to pin TRIGGER_PIN
      delay(duration);
      digitalWrite(TRIGGER_PIN, LOW);
    }
  }
}