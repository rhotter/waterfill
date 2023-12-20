from gpiozero import AngularServo, OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# Setup for pigpio factory
factory = PiGPIOFactory()

# Servo setup
SERVO_X_PIN = 27
SERVO_Y_PIN = 22

TRIGGER_PIN = 17
INCREMENT = 5     # Adjust this for finer control of servo movement

# Initialize servos with pigpio factory and trigger pin
servoX = AngularServo(SERVO_X_PIN, pin_factory=factory, initial_angle=-90)
servoY = AngularServo(SERVO_Y_PIN, pin_factory=factory, initial_angle=-90)
trigger = OutputDevice(TRIGGER_PIN, pin_factory=factory)

print("s3")


def clamp(value, min_value=-90, max_value=90):
    return max(min_value, min(max_value, value))


def main():
    posX = servoX.angle or 0
    posY = servoY.angle or 0

    while True:
        command = input("Enter command (UP/DOWN/LEFT/RIGHT/SHOOT): ")

        if command == "UP":
            posY = clamp(posY - INCREMENT)
            servoY.angle = posY
        elif command == "DOWN":
            posY = clamp(posY + INCREMENT)
            servoY.angle = posY
        elif command == "LEFT":
            posX = clamp(posX + INCREMENT)
            servoX.angle = posX
        elif command == "RIGHT":
            posX = clamp(posX - INCREMENT)
            servoX.angle = posX
        elif command.startswith("SHOOT"):
            duration = int(command[6:])
            trigger.on()
            sleep(duration)
            trigger.off()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
