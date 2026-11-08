FROM python:3.12-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt
COPY common.py .
COPY storage storage
CMD ["uvicorn", "storage.app:app", "--host", "0.0.0.0", "--port", "8000"]
