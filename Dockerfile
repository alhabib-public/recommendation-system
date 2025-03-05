FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for NLP
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLP model to cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy application code
COPY . .

EXPOSE 8000




# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="${PYTHONPATH}:."


CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "debug"]
