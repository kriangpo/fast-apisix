FROM python:3.13-slim

WORKDIR /app

ENV TZ=Asia/Bangkok

# ติดตั้ง system dependencies ที่จำเป็น
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8200

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8200"]
