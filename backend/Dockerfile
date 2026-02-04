# 1. BASE IMAGE: NVIDIA CUDA 12.8 Devel on Red Hat UBI 9
FROM nvcr.io/nvidia/cuda:12.8.0-devel-ubi9

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TORCH_CUDA_ARCH_LIST="12.0"

# 2. SYSTEM DEPENDENCIES
RUN dnf -y update && \
    dnf -y install \
    git \
    gcc-c++ \
    python3.11 \
    python3.11-devel \
    python3.11-pip \
    && dnf clean all

# 3. SET PYTHON 3.11 DEFAULT
RUN alternatives --set python3 /usr/bin/python3.11 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

WORKDIR /app

# 4. UPGRADE PIP
RUN python3 -m pip install --upgrade pip setuptools wheel packaging ninja

# 5. INSTALL PYTORCH NIGHTLY (CUDA 12.8)
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# 6. INSTALL FLASH ATTENTION (THE FIX IS HERE)
# MAX_JOBS=1: Prevents memory spikes/thrashing
# -v: Streams output so you know it hasn't hung
RUN MAX_JOBS=1 pip install -v "flash-attn>=2.6.3" --no-build-isolation

# 7. INSTALL DIFFUSERS
RUN pip install git+https://github.com/huggingface/diffusers.git

# 8. REST OF DEPENDENCIES
# Remember to remove 'torch' from requirements.txt!
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# OpenShift Permissions Fix
RUN chgrp -R 0 /app && \
    chmod -R g=u /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
