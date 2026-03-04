# Biblio TTS Server (Piper)

> Part of the [BiblioHub](https://github.com/vpoluyaktov/biblio-hub) application suite

A REST API server for Piper TTS models, providing text-to-speech synthesis for multiple languages.

## Features

- **Multiple Languages**: Support for 40+ languages including English, Spanish, French, German, Russian, Chinese, and more
- **High-Quality Voices**: Access to hundreds of Piper TTS voices with varying quality levels
- **Multi-Speaker Models**: Support for models with multiple speakers
- **Speed Control**: Adjust speech speed from 0.5x to 2.0x
- **REST API**: Simple HTTP API compatible with OpenTTS clients
- **Model Filtering**: Configure which models to serve; only those models will be available
- **Model Preloading**: Served models are preloaded at startup for faster first requests

## Quick Start (Docker)

The recommended way to run TTS Server Piper is as part of the [BiblioHub](https://github.com/vpoluyaktov/biblio-hub) Docker Swarm stack:

```bash
# Clone BiblioHub and service repositories
git clone https://github.com/vpoluyaktov/biblio-hub.git
git clone https://github.com/vpoluyaktov/biblio-tts-server-piper.git

# Start the stack
cd biblio-hub
cp .env.example .env
./scripts/start_stack.sh
```

Access at: `http://localhost:9900/tts-piper/`

### Standalone Docker

```bash
docker build -t biblio-tts-server-piper -f docker/Dockerfile .
docker run -p 5556:5556 -v $(pwd)/models:/data/piper biblio-tts-server-piper
```

### Installation from Source

**Prerequisites**: Piper TTS must be installed and available in PATH. Download from [Piper Releases](https://github.com/rhasspy/piper/releases).

```bash
# Clone the repository
git clone https://github.com/vpoluyaktov/biblio-tts-server-piper.git
cd biblio-tts-server-piper

# Install dependencies
pip install -r requirements.txt

# Run the server
python -m biblio_tts_server_piper
```

### Command Line Options

```bash
python -m biblio_tts_server_piper --help

Options:
  --host HOST           Host to bind to (default: 0.0.0.0)
  --port PORT           Port to bind to (default: 5556)
  --cache-dir DIR       Cache directory for models (default: ~/.cache/piper)
  --served-models IDS   Comma-separated list of models to serve (only these will be available)
```

Example:
```bash
python -m biblio_tts_server_piper --cache-dir ./models --served-models en_US-lessac-medium,en_GB-alan-medium
```

## API Usage

### List Available Voices

```bash
curl http://localhost:5556/api/voices
```

### Synthesize Speech

```bash
# Simple text (English)
curl "http://localhost:5556/api/tts?voice=piper:en_US-lessac-medium&text=Hello%20world" -o output.wav

# With speed control
curl "http://localhost:5556/api/tts?voice=piper:en_US-lessac-medium&text=Hello%20world&speed=1.2" -o output.wav

# Multi-speaker model
curl "http://localhost:5556/api/tts?voice=piper:en_US-libritts_r-medium%230&text=Hello%20world" -o output.wav
```

### List Languages

```bash
curl http://localhost:5556/api/languages
```

### List Models

```bash
# All models
curl http://localhost:5556/api/models

# Models for a specific language
curl "http://localhost:5556/api/models?language=en"
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PIPER_HOST` | `0.0.0.0` | Server bind address |
| `PIPER_PORT` | `5556` | Server port |
| `PIPER_BASE_PATH` | `/` | URL base path for reverse proxy |
| `PIPER_CACHE_DIR` | `~/.cache/piper` | Cache directory for models and config |
| `PIPER_SERVED_MODELS` | - | Comma-separated list of models to serve (e.g., `en_US-lessac-medium,en_GB-alan-medium`). Only these models and their languages/voices will be available via the API. Models are preloaded at startup. |
| `PIPER_LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Available Models

Piper provides hundreds of voices across 40+ languages. Common model examples:

- **English (US)**: `en_US-lessac-medium`, `en_US-amy-medium`, `en_US-libritts_r-medium`
- **English (GB)**: `en_GB-alan-medium`, `en_GB-alba-medium`
- **Spanish**: `es_ES-mls_10246-low`, `es_MX-ald-medium`
- **French**: `fr_FR-siwis-medium`, `fr_FR-mls_1840-low`
- **German**: `de_DE-thorsten-medium`, `de_DE-eva_k-x_low`
- **Russian**: `ru_RU-ruslan-medium`, `ru_RU-dmitri-medium`

For a complete list, see the [Piper Voices](https://huggingface.co/rhasspy/piper-voices) repository.

## Voice Quality Levels

- **x-low**: Fastest, smallest models, lower quality
- **low**: Fast, small models, decent quality
- **medium**: Balanced speed and quality (recommended)
- **high**: Slower, larger models, better quality

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:5556/docs
- ReDoc: http://localhost:5556/redoc

## License

MIT License
