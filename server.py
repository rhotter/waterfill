from modal import Stub, Image, method, asgi_app

image = (
    Image.debian_slim()
    .pip_install(
        "Pillow",
        "torch",
        "transformers",
        "timm",
        "scipy",
        "fastapi",
    ))

stub = Stub("waternug", image=image)


@stub.cls(gpu="A10G")
class Model:
    def __enter__(self):
        from transformers import Owlv2Processor, Owlv2ForObjectDetection
        # Load the model and processor

        self.processor = Owlv2Processor.from_pretrained(
            "google/owlv2-base-patch16-ensemble")
        self.model = Owlv2ForObjectDetection.from_pretrained(
            "google/owlv2-base-patch16-ensemble")

    @method()
    def segment(self, image_bytes, queries, threshold=0.4):
        from io import BytesIO
        from PIL import Image
        import torch

        if torch.cuda.is_available():
            device = torch.device("cuda")

        image = Image.open(BytesIO(image_bytes))

        inputs = self.processor(
            text=queries, images=image, return_tensors="pt").to(device)

        # Model prediction
        model = self.model.to(device)
        model.eval()

        with torch.no_grad():
            outputs = model(**inputs)

        model_image_size = model.config.vision_config.image_size
        target_sizes = torch.Tensor(
            [(model_image_size, model_image_size)]).to(device)
        results = self.processor.post_process_object_detection(
            outputs, threshold=threshold, target_sizes=target_sizes)

        results = results[0]

        # turn results into a list
        results_list = []
        aspect_ratio = image.size[0]/image.size[1]
        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            x1, y1, x2, y2 = box.cpu().tolist()
            x1 *= 1/model_image_size
            x2 *= 1/model_image_size
            y1 *= aspect_ratio/model_image_size
            y2 *= aspect_ratio/model_image_size

            results_list.append({
                "score": float(score),
                "box": [x1, y1, x2, y2],
                "label": queries[label]
            })

        return results_list


@stub.function(image=image)
@asgi_app()
def flask_app():
    from fastapi import FastAPI, File, UploadFile, Query
    from typing import List

    web_app = FastAPI()

    @web_app.get("/")
    def hi():
        return "hi!"

    @web_app.post("/segment")
    async def segment(image: UploadFile = File(...),
                      queries: List[str] = Query(["a mug", "a cup"]),
                      threshold: float = Query(0.4)):
        if not image:
            return {'error': 'No image provided'}, 400

        image_bytes = await image.read()

        # Use queries from args if provided, else default to ["a cup", "a mug"]
        results = Model().segment.remote(image_bytes, queries=queries, threshold=threshold)

        return results

    return web_app
