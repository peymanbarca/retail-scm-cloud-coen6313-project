FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Optional: Preload Hugging Face model
RUN python -c "from transformers import pipeline; pipeline('feature-extraction', model='sentence-transformers/all-MiniLM-L6-v2')"

EXPOSE 8004
CMD ["uvicorn", "product_catalogue_service:app", "--host", "0.0.0.0", "--port", "8004"]
