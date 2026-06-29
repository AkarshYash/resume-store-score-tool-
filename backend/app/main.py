"""
Main FastAPI application for Resume Intelligence Platform
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the application
    Runs on startup and shutdown
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")
    
    # Download AI models if needed
    try:
        from app.services.ai_matcher import initialize_models
        logger.info("Initializing AI models...")
        await initialize_models()
        logger.info("AI models loaded successfully")
    except Exception as e:
        logger.warning(f"Could not initialize AI models: {e}")
        logger.warning("Models will be downloaded on first use")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered Resume Intelligence Platform for finding the best resume match",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Add processing time to response headers
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Import and include routers
from app.api import candidates, resumes, matching, search, analytics, jd_analytics

app.include_router(
    candidates.router,
    prefix=f"{settings.API_V1_PREFIX}/candidates",
    tags=["Candidates"]
)

app.include_router(
    resumes.router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["Resumes"]
)

app.include_router(
    matching.router,
    prefix=f"{settings.API_V1_PREFIX}/matching",
    tags=["Matching"]
)

app.include_router(
    search.router,
    prefix=f"{settings.API_V1_PREFIX}/search",
    tags=["Search"]
)

app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["Analytics"]
)

app.include_router(
    jd_analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/jd",
    tags=["jd_analytics"]
)

logger.info("All API routers loaded successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
