FROM python:3.11.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    curl \
    gcc g++ python3-dev musl-dev libffi-dev \
    ffmpeg libsm6 libxext6 zbar-tools libzbar-dev \
    libpq-dev postgresql-client \
    cmake \
    netcat-traditional \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /backend/backend

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8008
