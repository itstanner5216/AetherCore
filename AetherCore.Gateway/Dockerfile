# AetherCore Gateway + Search Helper (FastAPI + Node) - Koyeb compatible
# Build from repo root: docker build -f Aethercore.Gateway/Dockerfile .

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# System deps: build tooling + Node + PM2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nodejs \
    npm \
    curl \
    && npm install -g pm2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps (cache-friendly)
COPY Aethercore.Gateway/requirements.txt ./Aethercore.Gateway/requirements.txt
RUN pip install --no-cache-dir -r Aethercore.Gateway/requirements.txt

# Install Node deps (cache-friendly)
COPY Aethercore.Gateway/package*.json ./Aethercore.Gateway/
RUN cd Aethercore.Gateway && npm ci --omit=dev

# Copy source
COPY Aethercore.Gateway/ ./Aethercore.Gateway/
COPY AetherCore.System/ ./AetherCore.System/
COPY skills/ ./skills/

# Run everything from the gateway directory so PM2 paths stay stable
WORKDIR ${APP_HOME}/Aethercore.Gateway
ENV PYTHONPATH=${APP_HOME}/Aethercore.Gateway

# Expose both processes
EXPOSE 8000 3000

# Healthcheck hits FastAPI
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Run both FastAPI (8000) + Node helper (3000)
CMD ["pm2-runtime", "ecosystem.config.js"]
