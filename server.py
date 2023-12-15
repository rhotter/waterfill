from flask import Flask, request, jsonify
from dataclasses import dataclass
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
import torch
from PIL import Image
import io
import cv2

# Initialize Flask app
app = Flask(__name__)

# Load the model and processor
processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")

# Data class for the response
@dataclass
class SegmentationResponse:
    contours: list

def detect_contours(preds):
    mask = preds > 0.1
    contours, _ = cv2.findContours(mask.astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_list = [contour.tolist() for contour in contours]
    return contours_list

@app.route('/segment', methods=['POST'])
def segment_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    # Read the image file
    image_file = request.files['image']
    image = Image.open(io.BytesIO(image_file.read()))

    # Define your prompts here
    prompts = ["cup"]

    # Process the image and prompts
    inputs = processor(text=prompts, images=[image] * len(prompts), padding="max_length", return_tensors="pt")

    # Model prediction
    with torch.no_grad():
        outputs = model(**inputs)
    preds = torch.sigmoid(outputs.logits)

    contours = detect_contours(preds.numpy())

    # Create a response object
    response = SegmentationResponse(contours=contours)

    return jsonify(response.__dict__)

if __name__ == '__main__':
    app.run(debug=True)
