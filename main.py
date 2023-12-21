import time
from picamera import PiCamera
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from time import sleep


# this will init the gpio crap
from controller import move_rel, shoot_start, shoot_stop
sleep(0.1)

OFFSET_X = 0.47
OFFSET_Y = 0.5
offsets = np.array([OFFSET_X, OFFSET_Y])
TOLERANCE = 0.02

IMG_GAIN_X = -100
IMG_GAIN_Y = 100
img_gains = np.array([IMG_GAIN_X, IMG_GAIN_Y])

# Replace 'COM_PORT' with the appropriate port
# arduino = serial.Serial('COM_PORT', 9600)
camera = PiCamera()
camera.rotation = 180

image_path = 'scene.jpg'


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
    print("got response!")
    res = response.json()
    return res


def do_feedback():
    snap()
    try:
        x1, y1, x2, y2 = find_mug()[0]["box"]
        cx = (x1 + x2) / 2
        # cy = (y1 + y2) / 2
        bottom_y = max(y1, y2)
        top_y = min(y1, y2)
        cy = 0.75 * top_y + 0.25 * bottom_y

        print(f"found cup at {cx}, {cy}")
    except:
        print("Didnt find the cup")
        shoot_stop()
        return
    com = np.array([cx, cy])
    move_rel(*((com - offsets) * img_gains))
    time.sleep(0.1)

    # shoot if within tolerance
    if np.linalg.norm(com - offsets) < TOLERANCE:
        print("shooting")
        shoot_start()
    else:
        shoot_stop()

# try:
# while True:
#     do_feedback()


if __name__ == "__main__":
    try:
        while True:
            do_feedback()
    except KeyboardInterrupt:
        pass
    finally:
        shoot_stop()


# snap()
# find_mug()

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
