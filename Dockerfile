# Compatible con Raspberry Pi 4 (arm64)
FROM python:3.11-slim

# Evita preguntas interactivas y reduce tamaño
ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app

# No se expone puerto: usamos long polling
CMD ["python", "main.py"]
