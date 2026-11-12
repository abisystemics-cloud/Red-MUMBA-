# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CONFIG_PATH=/app/config/config.yaml

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends tini ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY core/ core/
COPY agents/ agents/
COPY ml_engine/ ml_engine/
COPY scripts/ scripts/
COPY main.py docker-entrypoint.sh ./
COPY config.yaml /app/config.default.yaml

RUN useradd --uid 10001 --create-home trader \
    && mkdir -p /app/data /app/config \
    && chown -R trader:trader /app \
    && chmod +x /app/docker-entrypoint.sh
USER trader

VOLUME ["/app/data", "/app/config"]
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD python -c "import os,urllib.request,sys; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"8080\")}/health', timeout=4); sys.exit(0)" || exit 1

# tini relaie SIGTERM → arrêt propre (annulation des ordres / flatten)
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
CMD ["python", "main.py"]
