FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

RUN wget -O /tmp/piper.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    && tar -xzf /tmp/piper.tar.gz -C /usr/local/bin \
    && rm /tmp/piper.tar.gz \
    && chmod +x /usr/local/bin/piper \
    && ls -la /usr/local/bin/piper

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY setup.py pyproject.toml ./

RUN pip install --no-cache-dir -e .

EXPOSE 5556

ENV PIPER_HOST=0.0.0.0
ENV PIPER_PORT=5556
ENV PIPER_CACHE_DIR=/data/piper

VOLUME ["/data/piper"]

CMD ["python", "-m", "biblio_tts_server_piper"]
