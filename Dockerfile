# aiogram 2.x needs aiohttp 3.8, which ships wheels up to Python 3.11
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATA_DIR=/data

WORKDIR /app

# tzdata lets TZ from .env set the time for daily stats and backups
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 bot \
    && mkdir -p /data \
    && chown bot:bot /data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY tgbot ./tgbot

USER bot
VOLUME ["/data"]

CMD ["python", "main.py"]
