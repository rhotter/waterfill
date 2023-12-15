import serial
import time
from picamera import PiCamera
import requests
import numpy as np

# Replace 'COM_PORT' with the appropriate port
# arduino = serial.Serial('COM_PORT', 9600)
camera = PiCamera()
image_path = 'scene.jpg'


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


def snap():
    camera.capture('scene.jpg')
    print("snapped")


def find_mug():
    print("pinging api...")
    # URL of the Flask API
    api_url = 'https://rhotter--waternug-flask-app.modal.run/segment'

    # Open the image and send it in a POST request
    with open(image_path, 'rb') as image_file:
        files = {'image': (image_path, image_file, 'image/jpeg')}
        response = requests.post(api_url, files=files)

    preds = response.json()
    preds = np.array(preds)
    print(preds)


snap()
find_mug()

# Example usage
# up()
# time.sleep(1)
# down()
# time.sleep(1)
# left()
# time.sleep(1)
# right()
# time.sleep(1)
# shoot(5000)
