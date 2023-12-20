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
        from transformers import OwlViTProcessor, OwlViTForObjectDetection

        # Load the model and processor
        self.model = OwlViTForObjectDetection.from_pretrained(
            "google/owlvit-base-patch32")
        self.processor = OwlViTProcessor.from_pretrained(
            "google/owlvit-base-patch32")

    @method()
    def segment(self, image_bytes):
        from io import BytesIO
        from PIL import Image
        import torch

        if torch.cuda.is_available():
            device = torch.device("cuda")

        image = Image.open(BytesIO(image_bytes))

        queries = ["a cup", "a mug"]
        inputs = self.processor(
            text=queries, images=image, return_tensors="pt").to(device)

        # Model prediction
        model = self.model.to(device)
        model.eval()

        with torch.no_grad():
            outputs = model(**inputs)

        target_sizes = torch.Tensor([image.size[::-1]]).to(device)
        results = self.processor.post_process_object_detection(
            outputs, threshold=0.5, target_sizes=target_sizes)

        results = results[0]

        # turn results into a list
        results_list = [{
            "score": float(score),
            "box": (box / model.config.vision_config.image_size).cpu().tolist(),
            "label": queries[label]
        } for score, label, box in zip(results["scores"], results["labels"], results["boxes"])]

        return results_list


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
        results = Model().segment.remote(image_bytes)

        return jsonify(results)

    return web_app
