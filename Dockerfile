FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root to /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything into /app
COPY . .

# Move into the src directory for the runtime
WORKDIR /app/src

EXPOSE 8000

# Run uvicorn from within the src directory
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
