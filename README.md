# Biblio TTS Server (Piper)

> Part of the [BiblioHub](https://github.com/vpoluyaktov/biblio-hub) application suite

<img width="995" height="654" alt="Screenshot 2026-03-22 at 23 03 34" src="https://github.com/user-attachments/assets/f75682cc-0d48-40b7-a4a8-4836c0239aaa" />


REST service for [Piper](https://github.com/rhasspy/piper) text-to-speech synthesis with support for 40+ languages and hundreds of voices. Written in Python.

**Live demo: [https://demo.bibliohub.org/tts-piper/](https://demo.bibliohub.org/tts-piper/)**

## Features

- **40+ Languages** — English, Spanish, French, German, Russian, Chinese, and more
- **High-Quality Voices** — Hundreds of Piper voices with varying quality levels
- **Multi-Speaker Models** — Support for models with multiple speakers
- **Speed Control** — Adjust speech speed from 0.5x to 2.0x
- **Model Filtering** — Configure which models to serve; preloaded at startup
- **REST API** — Compatible with OpenTTS clients

## Technology Stack

- **Language**: Python
- **Framework**: FastAPI + uvicorn
- **TTS Engine**: Piper TTS
- **Deployment**: Docker, Docker Swarm (via BiblioHub)

## Quick Start (Docker)

The recommended way to run is as part of the [BiblioHub](https://github.com/vpoluyaktov/biblio-hub) Docker Swarm stack:

```bash
git clone https://github.com/vpoluyaktov/biblio-hub.git
cd biblio-hub
cp .env.example .env
./scripts/start_stack.sh
```

Access at: `http://localhost:9900/tts-piper/`

### From Source

Requires Piper TTS installed and available in PATH ([Piper Releases](https://github.com/rhasspy/piper/releases)).

```bash
git clone https://github.com/vpoluyaktov/biblio-tts-server-piper.git
cd biblio-tts-server-piper
pip install -r requirements.txt
python -m biblio_tts_server_piper
```

## API Endpoints

- `GET /api/tts` — Synthesize speech (`voice`, `text`, `speed` params)
- `GET /api/voices` — List available voices
- `GET /api/languages` — List supported languages
- `GET /api/models` — List available models (optional `language` filter)
- `GET /health` — Health check

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `PIPER_HOST` | Server bind address | `0.0.0.0` |
| `PIPER_PORT` | Server port | `5556` |
| `PIPER_BASE_PATH` | URL base path for reverse proxy | `/` |
| `PIPER_CACHE_DIR` | Cache directory for models | `~/.cache/piper` |
| `PIPER_SERVED_MODELS` | Comma-separated models to serve (e.g., `en_US-lessac-medium,en_GB-alan-medium`) | — |
| `PIPER_LOG_LEVEL` | Logging level | `INFO` |

## Available Models

Common examples:

- **English (US)**: `en_US-lessac-medium`, `en_US-amy-medium`
- **English (GB)**: `en_GB-alan-medium`, `en_GB-alba-medium`
- **Spanish**: `es_ES-mls_10246-low`, `es_MX-ald-medium`
- **French**: `fr_FR-siwis-medium`
- **German**: `de_DE-thorsten-medium`
- **Russian**: `ru_RU-ruslan-medium`, `ru_RU-dmitri-medium`

Full list: [Piper Voices](https://huggingface.co/rhasspy/piper-voices)

## License

MIT
