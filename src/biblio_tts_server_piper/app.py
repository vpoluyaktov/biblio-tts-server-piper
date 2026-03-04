"""FastAPI application for Biblio TTS Server (Piper)."""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import __version__
from .config import settings
from .models import HealthResponse
from .routers import tts_router, voices_router
from .services import PiperTTSService

STATIC_DIR = Path(__file__).parent / "static"

def setup_logging():
    """Configure logging with clean, structured output."""
    log_level = getattr(logging, settings.log_level.upper())
    
    class CleanFormatter(logging.Formatter):
        FORMATS = {
            logging.DEBUG: "\033[90m[DEBUG]\033[0m %(message)s",
            logging.INFO: "\033[32m[INFO]\033[0m  %(message)s",
            logging.WARNING: "\033[33m[WARN]\033[0m  %(message)s",
            logging.ERROR: "\033[31m[ERROR]\033[0m %(message)s",
            logging.CRITICAL: "\033[31;1m[CRIT]\033[0m  %(message)s",
        }
        
        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno, "[%(levelname)s] %(message)s")
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(CleanFormatter())
    root_logger.addHandler(console_handler)
    
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info(f"Starting Biblio TTS Server (Piper) v{__version__}")
    logger.info(f"Cache directory: {settings.cache_dir}")

    if settings.served_models:
        served_model_ids = [m.strip() for m in settings.served_models.split(",")]
        logger.info(f"Served models: {served_model_ids}")
    else:
        served_model_ids = None
    
    tts_service = PiperTTSService(served_models=served_model_ids)
    
    if served_model_ids:
        tts_service.preload_models(served_model_ids)

    logger.info(f"Biblio TTS Server (Piper) ready at http://{settings.host}:{settings.port}")

    yield

    logger.info("Shutting down Biblio TTS Server (Piper)")


app = FastAPI(
    title="Biblio TTS Server (Piper)",
    description="Part of BiblioHub - REST API for Piper TTS models",
    version=__version__,
    lifespan=lifespan,
    root_path=settings.base_path,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts_router)
app.include_router(voices_router)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root():
    """Serve the web UI."""
    html_path = STATIC_DIR / "index.html"
    html_content = html_path.read_text()
    
    base_path = settings.base_path.rstrip('/')
    html_content = html_content.replace(
        "const BASE_PATH = '';",
        f"const BASE_PATH = '{base_path}';"
    )
    
    return HTMLResponse(content=html_content)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=__version__)
