# full res: 4 s
# 50x50: 2-3 s
# hi: 0.4 s
# read-img: 0.5 s

import requests
import time
from PIL import Image

print("pinging api...")

api_url = 'http://bore.pub:23807/segment'
image_path = 'scene-3.jpg'

# Open the image and send it in a POST request
queries = ["cup"]
with open(image_path, 'rb') as image_file:
    params = {'queries': queries, 'threshold': 0.2}
    files = {'image': (image_path, image_file, 'image/jpeg')}
    time2 = time.time()
    response = requests.post(api_url, files=files, params=params)
print("got response!")
# print(response.text)
preds = response.json()
print(preds)
end_time = time.time()
print("API time: " + str(end_time - time2))
