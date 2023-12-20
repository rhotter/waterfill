from modal import Stub, Image, method, wsgi_app

image = (
    Image.debian_slim()
    .pip_install(
        "Pillow",
        "torch",
        "transformers",
        "timm",
        "flask"
    ))

stub = Stub("waternug", image=image)


@stub.cls(gpu="A10G")
class Model:
    def __enter__(self):
        from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
        # Load the model and processor
        self.processor = CLIPSegProcessor.from_pretrained(
            "CIDAS/clipseg-rd64-refined")
        self.model = CLIPSegForImageSegmentation.from_pretrained(
            "CIDAS/clipseg-rd64-refined")

    @method()
    def segment(self, image_bytes):
        from io import BytesIO
        from PIL import Image
        import torch

        if torch.cuda.is_available():
            device = torch.device("cuda")

        image = Image.open(BytesIO(image_bytes)).resize((350, 350))

        prompts = ["cup"]
        inputs = self.processor(text=prompts, images=[
                                image] * len(prompts), padding="max_length", return_tensors="pt").to(device)
        # Model prediction
        model = self.model.to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        preds = torch.sigmoid(outputs.logits).cpu().numpy()
        return preds


@stub.function(image=image)
@wsgi_app()
def flask_app():
    from flask import Flask, request, jsonify

    web_app = Flask(__name__)

    @web_app.get("/")
    def hi():
        return "hi!"

    @web_app.post("/segment")
    def segment():
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        image_file = request.files['image']
        image_bytes = image_file.read()
        preds = Model().segment.remote(image_bytes)

        # turn to list
        return jsonify("works")
        preds_list = preds.tolist()

        return jsonify(preds_list)

    return web_app
