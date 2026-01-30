FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY automatic_manager/ ./automatic_manager/
COPY environment/ ./environment/
COPY knowledge/ ./knowledge/
COPY utils/ ./utils/
COPY config.py .
COPY main.py .



CMD ["python", "main.py"]
