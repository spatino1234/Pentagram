import modal
import io
from fastapi import Response, HTTPException, Query, Request
from datetime import datetime, timezone
import requests
import os

def download_model():
    from diffusers import AutoPipelineForText2Image
    import torch

    AutoPipelineForText2Image.from_pretrained(
        "stabilityai/sdxl-turbo",
        torch_dtype=torch.float16,
        variant="fp16"
    )


image = (
    modal.Image.debian_slim()
    .pip_install(
        "fastapi[standard]", 
        "transformers", 
        "accelerate", 
        "diffusers", 
        "requests"
    )
    .run_function(download_model)
)

app = modal.App("sdxl-turbo", image=image)

@app.cls(
    image=image,
    gpu="A10G",
    secrets=[modal.Secret.from_name("custom-secret")]
    
)
class Model:
    @modal.build()
    @modal.enter()
    def load_weights(self):
        from diffusers import AutoPipelineForText2Image
        from diffusers.utils import make_image_grid, load_image
        import torch

        self.pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16,
            variant="fp16"
        )
        self.pipe.to("cuda")
        self.API_KEY = os.environ["API_KEY"]

    @modal.web_endpoint()
    def generate(self, request: Request, prompt: str = Query(..., description="The text prompt to generate your image from")):

        api_key = request.headers.get("X-API-KEY")

        if api_key != self.API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        image = self.pipe(prompt, num_inference_steps = 8, guidance_scale = 0.0).images[0]
        
        buffer = io.BytesIO()
        image.save(buffer, format = "JPEG")
        
        return Response(content=buffer.getvalue(), media_type="image/jpeg")
    

    @modal.web_endpoint()
    def health(self):
            return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
# modal deploy main.py
    

#  @app.function(
#     schedule=modal.Cron("*/5 * * * *"),
#     secrets=[modal.Secret.from_name("custom-secret")]
# )
# def keep_warm():
#     health_url = "https://rafikasaad007--sdxl-turbo-model-generate.modal.run"
#     generate_url = "hhttps://rafikasaad007--sdxl-turbo-model-health.modal.run"

#     health_response = requests.get(health_url)
#     print('health_response', health_response.json())
#     print(f"Health check status code: {health_response.json()['status']} at: {datetime.now(timezone.utc).isoformat()}")

#     headers = {
#         "X-API-Key": os.environ["API_KEY"]
#     }

#     generate_response = requests.get(generate_url, headers=headers)
#     print(f"Generate endpoint tested successfully at: {datetime.now(timezone.utc).isoformat()}")



