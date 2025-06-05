# health_only_app.py
"""
Minimal health-only FastAPI app for reliable health checks
This module provides a simple health endpoint that the launcher can use
without dependencies on the full backend functionality.
"""
from fastapi import FastAPI

# Create a minimal app with just health endpoints
health_app = FastAPI(
    title="Darbot Agent Engine Health Check",
    description="Minimal health check endpoints for monitoring",
    version="1.0.0"
)

@health_app.get("/health")
async def get_basic_health():
    """
    Basic health check endpoint for simple monitoring and launcher scripts.
    
    Returns 200 if the service is running. This is the primary health endpoint
    used by the Launcher.ps1 script and other monitoring tools.
    
    This endpoint is designed to be fast and dependency-free to ensure
    it always responds even if other parts of the system have issues.
    """
    return {"status": "ok", "service": "Darbot Agent Engine"}

@health_app.get("/healthz")
async def healthz_endpoint():
    """
    Healthz endpoint for middleware compatibility.
    Returns 200 if the service is running.
    """
    return {"status": "ok", "service": "Darbot Agent Engine"}

@health_app.get("/")
async def root():
    """Root endpoint to show the service is running"""
    return {"message": "Darbot Agent Engine Health Service", "status": "running"}