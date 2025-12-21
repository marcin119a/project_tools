import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from models.database import engine
from routers import health, hello, location


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    from models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: Close database connections
    try:
        await engine.dispose()
    except asyncio.CancelledError:
        # Ignoruj CancelledError podczas shutdown (normalne zachowanie uvicorn)
        pass
    except Exception:
        # Ignoruj inne błędy podczas shutdown
        pass


app = FastAPI(
    title="Project Tools API",
    description="API dla zarządzania lokalizacjami i ogłoszeniami",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(hello.router, tags=["Hello"])
app.include_router(location.router)


@app.get("/", response_model=dict)
async def root() -> dict:
    """Root endpoint - podstawowe informacje o API"""
    return {
        "message": "Project Tools API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }

