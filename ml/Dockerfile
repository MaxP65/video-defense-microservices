FROM python:3.12-slim
WORKDIR /app
COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt numpy==1.26.4 opencv-python-headless==4.11.0.86
RUN pip install --no-cache-dir torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
COPY common.py .
COPY ml ml
CMD ["uvicorn", "ml.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
