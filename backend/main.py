"""
Lotus Backend - FastAPI Application Entry Point
Vaginal health RAG application using Supabase and LLM
Production-ready with Sentry monitoring and request tracking
"""

import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from config import settings
from utils.supabase_client import initialize_supabase
from routers import scan, profiles, ingredients

# Initialize Sentry for error tracking in production
if settings.SENTRY_DSN and settings.ENVIRONMENT == 'production':
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT or settings.ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                StarletteIntegration(),
            ]
        )
        logger_initialized = logging.getLogger(__name__)
        logger_initialized.info("✓ Sentry error tracking initialized")
    except Exception as e:
        logging.error(f"Failed to initialize Sentry: {e}")

# Configure logging with production-safe defaults
log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
)
logger = logging.getLogger(__name__)


class RequestIDMiddleware:
    """
    Middleware to add request ID tracking for distributed tracing
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Generate or retrieve request ID
            headers = dict(scope.get("headers", []))
            request_id = headers.get(b"x-request-id", b"").decode() or str(uuid.uuid4())
            scope["request_id"] = request_id
            
            # Add to logs
            logging.LogRecord.request_id = request_id
        
        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifecycle
    Startup: Initialize connections and services
    Shutdown: Graceful cleanup and connection closure
    """
    # Startup
    logger.info("🚀 Starting Lotus backend application")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    try:
        initialize_supabase()
        logger.info("✓ Supabase client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        raise
    
    logger.info("✓ Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Lotus backend application")
    logger.info("✓ Graceful shutdown completed")


# Initialize FastAPI app with lifespan and production settings
app = FastAPI(
    title="Lotus Backend",
    description="Vaginal health RAG application API - Production Ready",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,  # Hide docs in production
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# Configure CORS middleware FIRST - must be before other middleware to handle OPTIONS requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add trusted host middleware for production security
if settings.ENVIRONMENT == 'production':
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.vercel.app", "localhost", "127.0.0.1"]
    )

# Add request ID middleware for tracing (after CORS)
app.add_middleware(RequestIDMiddleware)


# Custom request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests with timing information
    Skip logging for OPTIONS (CORS preflight) requests to avoid interference
    """
    # Skip detailed logging for OPTIONS requests - let CORS handle them
    if request.method == "OPTIONS":
        return await call_next(request)
    
    start_time = datetime.utcnow()
    request_id = getattr(request.scope, "request_id", str(uuid.uuid4()))
    
    if settings.ENABLE_REQUEST_LOGGING:
        logger.info(
            f"→ {request.method} {request.url.path}",
            extra={"request_id": request_id}
        )
    
    try:
        response = await call_next(request)
    except Exception as e:
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.error(
            f"✗ {request.method} {request.url.path} - Error after {duration:.2f}s: {str(e)}",
            extra={"request_id": request_id},
            exc_info=True
        )
        raise
    
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    if settings.ENABLE_REQUEST_LOGGING:
        logger.info(
            f"← {request.method} {request.url.path} - {response.status_code} ({duration:.2f}s)",
            extra={"request_id": request_id}
        )
    
    # Add request ID to response headers for tracing
    response.headers["X-Request-ID"] = request_id
    
    # Check timeout
    if duration > settings.REQUEST_TIMEOUT_SECONDS:
        logger.warning(
            f"⏱️ Request exceeded timeout threshold ({duration:.2f}s > {settings.REQUEST_TIMEOUT_SECONDS}s)",
            extra={"request_id": request_id}
        )
    
    return response


# Include routers with API prefix
app.include_router(scan.router, prefix="/api")
app.include_router(profiles.router, prefix="/api")
app.include_router(ingredients.router, prefix="/api")


# Global OPTIONS handler for CORS preflight
@app.options("/{full_path:path}", include_in_schema=False)
async def options_handler(full_path: str):
    """
    Handle OPTIONS preflight requests for CORS
    Returns 200 OK with appropriate CORS headers (set by CORSMiddleware)
    """
    return {"status": "ok"}


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify API is running
    Used by load balancers and monitoring systems
    """
    return {
        "status": "healthy",
        "service": "Lotus Backend",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint
    Verifies all critical services are initialized
    """
    try:
        # Test Supabase connection
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Simple health check query
        health_response = supabase.table('ingredients_library').select('id').limit(1).execute()
        
        return {
            "ready": True,
            "service": "Lotus Backend",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "ready": False,
            "service": "Lotus Backend",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Lotus Backend API",
        "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production",
        "health": "/health",
        "ready": "/ready",
        "version": "0.1.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors
    Logs to Sentry if configured
    """
    request_id = getattr(request.scope, "request_id", str(uuid.uuid4()))
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    if settings.ENVIRONMENT == 'production':
        return {
            "error": "Internal Server Error",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, 500
    else:
        return {
            "error": str(exc),
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, 500


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
