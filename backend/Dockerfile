FROM python:3.11.10-slim

# ===== ENV =====
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ===== System deps =====
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc g++ python3-dev \
    libffi-dev \
    ffmpeg libsm6 libxext6 \
    zbar-tools libzbar-dev \
    libpq-dev postgresql-client \
    cmake \
    netcat-traditional \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# ===== Workdir =====
WORKDIR /backend/backend

# ===== Install Python deps (cache-friendly) =====
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# ===== Copy source code =====
COPY . .

# ===== Expose port =====
EXPOSE 8008