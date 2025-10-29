FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/dev/shm/mplcache

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py /app/main.py
COPY handlers/ /app/handlers/
COPY lib/ /app/lib/         

RUN mkdir -p /dev/shm/mplcache /app/data

CMD ["python", "main.py"]
