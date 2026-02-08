"""
FastAPI application initialization with middleware, CORS, and route registration.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.config import settings
from app.database import close_db, init_db
from app.routers import auth


# Initialize Sentry for error tracking (if configured)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0 if settings.DEBUG else 0.1,
        environment="development" if settings.DEBUG else "production",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown events.

    Startup:
        - Initialize database (development only)

    Shutdown:
        - Close database connections
    """
    # Startup
    # Disabled auto table creation - use Alembic migrations instead
    # This makes startup much faster
    # if settings.DEBUG:
    #     await init_db()

    yield

    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered SEO analysis platform for developers and agencies",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    if settings.DEBUG:
        # In debug mode, show full error details
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__,
            },
        )
    else:
        # In production, hide error details
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }


# Register routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Import additional routers
from app.routers import websites, crawls, dashboard

app.include_router(websites.router, prefix=settings.API_V1_PREFIX)
app.include_router(crawls.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)

# Additional routers will be added here as we build them:
# app.include_router(reports.router, prefix=settings.API_V1_PREFIX)
# app.include_router(keywords.router, prefix=settings.API_V1_PREFIX)
# app.include_router(ai.router, prefix=settings.API_V1_PREFIX)
# app.include_router(billing.router, prefix=settings.API_V1_PREFIX)
# app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
# trigger reload
