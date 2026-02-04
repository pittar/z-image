# 1. UPDATE BASE IMAGE: Must use CUDA 12.8 Devel for RTX 50-series (Blackwell) compilation
FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV TORCH_CUDA_ARCH_LIST="12.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    git \
    ninja-build \
    curl \
    ca-certificates \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    && rm -rf /var/lib/apt/lists/*

# Install pip for Python 3.11
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Set python3.11 as default python
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3

WORKDIR /app

# 2. INSTALL PYTORCH NIGHTLY: Explicitly target CUDA 12.8 (cu128)
# We install this BEFORE requirements.txt to ensure the GPU version is prioritized
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# 3. INSTALL FLASH ATTENTION
# Because the base image is now CUDA 12.8, this will compile correctly for sm_120
RUN MAX_JOBS=1 pip install "flash-attn>=2.6.3" --no-build-isolation

# Install Diffusers from source
RUN pip install git+https://github.com/huggingface/diffusers.git

# 4. INSTALL REMAINING DEPENDENCIES
# Important: Remove 'torch', 'torchvision', 'torchaudio' from your requirements.txt
# so this step doesn't downgrade what we just installed.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
