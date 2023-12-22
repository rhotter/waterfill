from PIL import Image
from fastapi import FastAPI, File, UploadFile, Query
from typing import List
from ultralytics import YOLO
import io
import pandas as pd

app = FastAPI()
model = YOLO()


@app.get("/")
def hi():
    return "hi!"


@app.post("/segment")
async def segment(image: UploadFile = File(...),
                  queries: List[str] = Query(["mug", "cup"]),
                  threshold: float = Query(0.4)):
    if not image:
        return {'error': 'No image provided'}, 400

    image_bytes = await image.read()
    img = Image.open(io.BytesIO(image_bytes))

    results = model.predict(source=img)[0]

    detected_objects = []
    for idx, cls_idx in enumerate(results.boxes.cls):
        object_name = results.names[int(cls_idx)]
        confidence = results.boxes.conf[idx].item()  # Convert to Python float

        if object_name in queries and confidence > threshold:
            bbox = results.boxes.xyxy[idx].tolist()  # Convert to Python list
            detected_object = {
                'name': object_name,
                'confidence': confidence,
                'coordinates': {
                    'xmin': bbox[0],
                    'ymin': bbox[1],
                    'xmax': bbox[2],
                    'ymax': bbox[3]
                }
            }
            detected_objects.append(detected_object)

    return detected_objects
