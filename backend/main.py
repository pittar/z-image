import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from diffusers import ZImagePipeline
from io import BytesIO
from fastapi.responses import Response
import os

app = FastAPI(title="Z-Image Generation API")

# Global variable for the pipeline
pipe = None

@app.on_event("startup")
async def startup_event():
    global pipe
    print("Initializing Z-Image Pipeline...")
    try:
        # Load the pipeline
        # Use bfloat16 for optimal performance on Blackwell (RTX 50-series)
        pipe = ZImagePipeline.from_pretrained(
            "Tongyi-MAI/Z-Image-Turbo",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=False,
        )

        # --- CRITICAL FIX START ---
        
        # 1. CPU Offloading
        # Instead of pipe.to("cuda"), we use offloading.
        # This keeps the inactive parts of the model in your 128GB System RAM
        # and only moves the Transformer/UNet to the GPU when actively computing.
        # This reduces VRAM usage from ~15GB to ~4-6GB.
        pipe.enable_model_cpu_offload()

        # 2. VAE Slicing
        # Generating 1024x1024 images creates a massive memory spike at the end
        # when decoding latents to pixels. Slicing decodes small chunks at a time.
        pipe.enable_vae_slicing()

        # --- CRITICAL FIX END ---

        # [Optional] Attention Backend
        # Since you built without Flash Attention installed, we should skip forcing it.
        # PyTorch 2.0+ automatically uses "Scaled Dot Product Attention" (SDPA),
        # which is built-in and highly optimized for your hardware.
        print("Using default PyTorch SDPA (Scaled Dot Product Attention) backend.")

        # [Optional] Model Compilation
        # Compiling can help speed, but on 16GB cards, compiling can sometimes
        # induce extra memory overhead. We'll leave it commented out for stability.
        # pipe.transformer.compile()
        
        print("Pipeline loaded successfully.")
    except Exception as e:
        print(f"Error loading pipeline: {e}")
        # We don't raise here to allow the app to start, but requests will fail
        pass

class GenerateRequest(BaseModel):
    prompt: str
    height: int = 1024
    width: int = 1024
    num_inference_steps: int = 9
    guidance_scale: float = 0.0
    seed: int = 42

@app.post("/generate", responses={200: {"content": {"image/png": {}}}})
async def generate_image(req: GenerateRequest):
    global pipe
    if pipe is None:
        raise HTTPException(status_code=503, detail="Model is not loaded or failed to load.")

    try:
        # Note: When using cpu_offload, standard generators are often safer,
        # but creating a CUDA generator is generally supported.
        generator = torch.Generator("cuda").manual_seed(req.seed)
        
        # Generate Image
        result = pipe(
            prompt=req.prompt,
            height=req.height,
            width=req.width,
            num_inference_steps=req.num_inference_steps,
            guidance_scale=req.guidance_scale,
            generator=generator,
        )
        
        image = result.images[0]
        
        # Save to buffer
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        
        return Response(content=buffer.getvalue(), media_type="image/png")
        
    except Exception as e:
        print(f"Error during generation: {e}")
        # Check for OOM specifically to give better feedback
        if "out of memory" in str(e).lower():
            raise HTTPException(status_code=500, detail="GPU Out of Memory. Try reducing image size.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": pipe is not None}
