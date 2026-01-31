# Use a standard Python image (not alpine, as alpine is harder to debug)
FROM python:3.11-slim

# 1. Install System Dependencies
# We need build-essential for compiling, and zlib/jpeg for Pillow
# We need libx11 for pystray (even if we skip the tray icon later)
RUN apt-get update && apt-get install -y \
    build-essential \
    libz-dev \
    libjpeg-dev \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Upgrade pip (fixes many wheel installation issues)
RUN pip install --no-cache-dir --upgrade pip

# 3. Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the app
COPY . .

# Set environment variable to skip tray logic in build.py
ENV DOCKER_BUILD=true

EXPOSE 8000

CMD ["python", "build.py"]