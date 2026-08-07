from fastapi import FastAPI

from app.api.routes.decisions import router as decisions_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="Helios Terminal API",
    description="Multi-agent decision intelligence platform for AI sourcing strategy and dependency risk analysis.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(decisions_router)
