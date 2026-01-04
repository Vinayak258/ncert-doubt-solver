FROM python:3.10-slim

WORKDIR /app

# Copy ONLY requirements
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt

# Copy ONLY service code
COPY src/ ./src
COPY app.py .

# ✅ COPY PROMPT FILES (THIS FIXES THE ERROR)
COPY prompts/ ./prompts/

# Copy vector store data (CRITICAL - contains FAISS index)
COPY data/vector_store/ ./data/vector_store/

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
