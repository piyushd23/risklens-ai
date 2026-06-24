from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.database import engine, Base
from app.routers import auth, users, targets, assets, assessments, findings, reports, analytics, dashboard

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RiskLensAI")

# Database tables init (ensures created if not using seed)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RiskLens AI – API Documentation",
    description="Defensive Web Security Risk Analytics Platform REST APIs. Supports discovery crawling, CVSS calculations, OWASP classification, and ML risk priorities.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this down to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose global error handling to prevent internal trace leakages
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A secure system error occurred. Please contact the security administrator."}
    )

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(targets.router, prefix="/api/v1")
app.include_router(assets.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")
app.include_router(findings.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "app": "RiskLens AI",
        "tagline": "Intelligent Security Assessment. Actionable Risk Insights.",
        "version": "1.0.0",
        "status": "online",
        "api_docs": "/docs"
    }
