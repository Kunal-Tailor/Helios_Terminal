from fastapi import FastAPI

app = FastAPI(
    title="Helios Terminal API",
    description="Multi-agent decision intelligence platform for AI sourcing strategy and dependency risk analysis.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Basic liveness check — confirms the API is up."""
    return {"status": "ok"}
