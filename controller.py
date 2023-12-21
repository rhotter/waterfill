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
servoX = AngularServo(SERVO_X_PIN, pin_factory=factory, initial_angle=0)
servoY = AngularServo(SERVO_Y_PIN, pin_factory=factory, initial_angle=-45)
trigger = OutputDevice(TRIGGER_PIN, pin_factory=factory)

posX = servoX.angle or 0
posY = servoY.angle or 0

print(posY, posX)


def clamp(value, min_value=-90, max_value=90):
    return max(min_value, min(max_value, value))


def move_rel(x_rel, y_rel):
    global posX, posY
    # test
    posY = clamp(posY + y_rel)
    posX = clamp(posX + x_rel)
    print(f"Moving rel {x_rel}, {y_rel} to new position {posX}, {posY}")
    servoX.angle = posX
    servoY.angle = posY


def shoot(duration):
    trigger.on()
    sleep(duration)
    trigger.off()


def shoot_start():
    trigger.on()


def shoot_stop():
    trigger.off()


def main():
    while True:
        command = input("Enter command (UP/DOWN/LEFT/RIGHT/SHOOT): ")
        if command == "UP":
            move_rel(0, INCREMENT)
        elif command == "DOWN":
            move_rel(0, -INCREMENT)
        elif command == "LEFT":
            move_rel(INCREMENT, 0)
        elif command == "RIGHT":
            move_rel(-INCREMENT, 0)
        elif command.startswith("SHOOT"):
            duration = int(command[6:])
            shoot(duration)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
