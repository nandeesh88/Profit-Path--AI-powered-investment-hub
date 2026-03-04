"""
Profit-Path API — Production Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import logging
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from core.config import settings
from core.database import connect_db, close_db, create_indexes
from core.logging_config import setup_logging
from core.middleware import SecurityHeadersMiddleware, RequestLoggingMiddleware
from core.rate_limit import RateLimitMiddleware
from routers import auth, users, expenses, goals, investments, income

# ── Bootstrap logging first ──────────────────────────────────────────────
setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} ({settings.APP_ENV})")

    # Database
    await connect_db()
    await create_indexes()

    # Pre-load ML models
    try:
        from ai_engine.train_models import load_models
        load_models()
        logger.info("✅ AI models ready")
    except Exception as e:
        logger.warning(f"⚠️  AI model loading: {e}")

    yield

    await close_db()
    logger.info("Shutdown complete")


# ── App ──────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# ── Middleware (order matters: last added = first executed) ───────────────
# 1. Rate limiting (innermost – runs last)
app.add_middleware(RateLimitMiddleware)
# 2. Request logging + timing
app.add_middleware(RequestLoggingMiddleware)
# 3. Security headers
app.add_middleware(SecurityHeadersMiddleware)
# 4. CORS (outermost – runs first, so every response gets CORS headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(investments.router, prefix="/api/v1")
app.include_router(income.router, prefix="/api/v1")


# ── Health endpoints ─────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "env": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "database": "connected"}


# ── Dev server ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
