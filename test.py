from modal import Stub, Image, gpu, method

image = (
    Image.debian_slim()
    .pip_install(
        "Pillow",
        "torch",
        "transformers",
        "timm",
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

        image = Image.open(BytesIO(image_bytes)).resize((350, 350))

        prompts = ["cup"]
        inputs = self.processor(text=prompts, images=[
                                image] * len(prompts), padding="max_length", return_tensors="pt")
        # Model prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
        preds = torch.sigmoid(outputs.logits).numpy()
        return preds


@stub.local_entrypoint()
def main():
    with open("IMG_8538.jpg", "rb") as f:
        image_bytes = f.read()
        preds = Model().segment.remote(image_bytes)
    print(preds)
