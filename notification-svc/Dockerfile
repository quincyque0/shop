FROM python:3.10-slim

LABEL maintainer="shop-team" \
      service="notification-svc" \
      version="1.0.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
