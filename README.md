# Z-Image-Turbo UI & Docker Environment

This project consists of a React Frontend and a CUDA-accelerated Python Backend for the Z-Image-Turbo model.

## Prerequisites
- **Docker** & **NVIDIA Container Toolkit** (Required for GPU support)
- **NVIDIA GPU** (Ampere or newer recommended for bfloat16 and Flash Attention)
- Node.js 18+

## Architecture
- **Frontend**: React + Tailwind + Lucide (Port 3000/8080)
- **Backend**: FastAPI + PyTorch + Diffusers (Port 8000)

## Quick Start

### 1. Start the Backend (Docker)
This builds a container with CUDA 12.4, Flash Attention 3 (support), and the latest Diffusers library.

```bash
cd backend

# Build the image (this may take 5-10 minutes to compile Flash Attention)
docker build -t z-image-turbo-backend .

# Run the container with GPU access
# IMPORTANT: --gpus all is required for the container to see your NVIDIA card
docker run --gpus all -p 8000:8000 z-image-turbo-backend
```

**Note on Flash Attention 3**: 
The Dockerfile installs the `flash-attn` package. The code attempts to use the `_flash_3` backend if toggled in the UI. This requires specific hardware support (e.g., NVIDIA H100 Hopper architecture). If you are running on Ampere (A100, RTX 3090) or Ada (RTX 4090), Flash Attention 2 is typically the standard. The backend handles fallback gracefully.

### 2. Start the Frontend
Open a new terminal in the project root:

```bash
npm install
npm start
```

## Usage
1. Open the frontend URL.
2. Ensure the backend is running (Check logs for "Model loaded successfully").
3. Enter a prompt and click "Generate".
