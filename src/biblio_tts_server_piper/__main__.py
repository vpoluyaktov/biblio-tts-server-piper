"""Entry point for running the server."""

import argparse
import os

import uvicorn

from .config import settings


def main():
    """Run the Biblio TTS Server (Piper)."""
    parser = argparse.ArgumentParser(description="Biblio TTS Server (Piper)")
    parser.add_argument(
        "--host",
        default=None,
        help=f"Host to bind to (default: {settings.host})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help=f"Port to bind to (default: {settings.port})",
    )
    parser.add_argument(
        "--cache-dir",
        default=None,
        help=f"Cache directory for models (default: {settings.cache_dir})",
    )
    parser.add_argument(
        "--served-models",
        default=None,
        help="Comma-separated list of models to serve (only these will be available)",
    )

    args = parser.parse_args()

    if args.host:
        os.environ["PIPER_HOST"] = args.host
    if args.port:
        os.environ["PIPER_PORT"] = str(args.port)
    if args.cache_dir:
        os.environ["PIPER_CACHE_DIR"] = args.cache_dir
    if args.served_models:
        os.environ["PIPER_SERVED_MODELS"] = args.served_models

    from .config import Settings
    updated_settings = Settings()

    uvicorn.run(
        "biblio_tts_server_piper.app:app",
        host=updated_settings.host,
        port=updated_settings.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
