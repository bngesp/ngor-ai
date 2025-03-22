import logging
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.controllers.webhook_controller import router as webhook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ngor-AI",
    description="An AI-powered code review system for GitLab merge requests",
    version="1.0.0"
)

# Add exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )

# Add routes
app.include_router(webhook_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Ngor-AI - AI-powered code reviews for GitLab"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Version endpoint
@app.get("/version")
async def version():
    return {"version": "1.0.0"}

# Start the application
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting Ngor-AI on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)