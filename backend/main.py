import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from diffusers import ZImagePipeline
from io import BytesIO
from fastapi.responses import Response
import os

app = FastAPI(title="Z-Image Generation API")

# --- ADD THIS BLOCK IMMEDIATELY AFTER CREATING 'app' ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL domains (easiest for testing)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# -------------------------------------------------------

# Global variable for the pipeline
pipe = None

@app.on_event("startup")
async def startup_event():
    global pipe
    print("Initializing Z-Image Pipeline...")
    try:
        # Load the pipeline
        pipe = ZImagePipeline.from_pretrained(
            "Tongyi-MAI/Z-Image-Turbo",
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=False,
        )

        # 1. CPU Offloading (Critical for 16GB VRAM)
        # Keeps weights in system RAM, moves to GPU only when needed.
        # If this method also fails, replace it with: pipe.to("cuda") and reduce image size.
        if hasattr(pipe, "enable_model_cpu_offload"):
            pipe.enable_model_cpu_offload()
        else:
            print("Warning: Pipeline does not support CPU offloading. VRAM usage may be high.")
            pipe.to("cuda")

        # 2. VAE Slicing (The Fix)
        # We call it on the .vae component directly
        if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_slicing"):
            pipe.vae.enable_slicing()
            print("VAE slicing enabled.")
        
        print("Pipeline loaded successfully.")
    except Exception as e:
        print(f"Error loading pipeline: {e}")
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
