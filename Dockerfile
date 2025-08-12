FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Tesseract OCR for OCR features
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bbs_tool ./bbs_tool
COPY README.md pyproject.toml ./
COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "bbs_tool.main:app", "--host", "0.0.0.0", "--port", "8000"]