# Use official python slim image for a smaller footprint
FROM python:3.10-slim

# Set environment variables for non-interactive installations and python optimizations
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- OPTIMIZATION STEP ---
# Pre-download the HuggingFace model directly into the Docker image layer.
# This prevents the application from re-downloading the large model weights upon every container start.
RUN python -c "\
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM; \
model_name='sshleifer/distilbart-cnn-12-6'; \
AutoTokenizer.from_pretrained(model_name); \
AutoModelForSeq2SeqLM.from_pretrained(model_name) \
"

# Copy the rest of the application code
COPY main.py .

# Expose the API port
EXPOSE 8000

# Specify the command to run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
