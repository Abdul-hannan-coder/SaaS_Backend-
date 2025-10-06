FROM python:3.11-slim

WORKDIR /app

# System deps - Enhanced video processing dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    yt-dlp \
    curl \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN pip install uv && uv sync

COPY . .

CMD ["uv", "run", "run.py"] 