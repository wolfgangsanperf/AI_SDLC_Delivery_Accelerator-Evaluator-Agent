from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from src.api.backlog_evaluator_api import router as evaluator_router

app = FastAPI(
    title="SDLC Accelerator AI Core",
    description="AI-powered core service for software development lifecycle acceleration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
app.include_router(evaluator_router)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8040)),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "debug")
    )
