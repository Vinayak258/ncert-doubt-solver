FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
# libgl1-mesa-glx is often needed for opencv if it's installed (even indirectly)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Copy source code (Unpack src into root /app)
COPY src/ .

# Copy application entry point
COPY app.py .

# Create directory for vector store (to be mounted)
# This path must match where RAGPipeline expects to find the vector store
# The 'config.py' or 'vector_store' logic usually defines this.
# By default, config.py points to "data/raw_books" etc. 
# We need to ensure the vector store path aligns.
RUN mkdir -p data/vector_store

# Expose port
EXPOSE 8001

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
