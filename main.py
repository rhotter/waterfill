import serial
import time

arduino = serial.Serial('COM_PORT', 9600)  # Replace 'COM_PORT' with the appropriate port

def send_command(command):
    arduino.write((command + '\n').encode())

def up():
    send_command("UP")

def down():
    send_command("DOWN")

def left():
    send_command("LEFT")

def right():
    send_command("RIGHT")

def shoot(duration):
    send_command(f"SHOOT {duration}")

# Example usage
up()
time.sleep(1)
down()
time.sleep(1)
left()
time.sleep(1)
right()
time.sleep(1)
shoot(5000)
