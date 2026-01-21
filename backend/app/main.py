from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import artifacts, controls, evidence, scores, gaps, actions, risks, evidence_links, candidates, reports


app = FastAPI(
    title="NIST CSF Tracker API",
    description="Local-first NIST Cybersecurity Framework compliance tracking",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "app": "NIST CSF Tracker",
        "version": "1.0.0",
        "features": {
            "llm_enabled": settings.feature_llm
        }
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "artifacts_path": str(settings.artifacts_path_absolute)
    }


# Include routers
app.include_router(artifacts.router, prefix="/api/artifacts", tags=["Artifacts"])
app.include_router(controls.router, prefix="/api/controls", tags=["Controls"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(evidence_links.router, prefix="/api", tags=["Evidence Links"])
app.include_router(candidates.router, prefix="/api", tags=["Candidates"])
app.include_router(scores.router, prefix="/api/scores", tags=["Scores"])
app.include_router(gaps.router, prefix="/api/gaps", tags=["Gaps"])
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])
app.include_router(risks.router, tags=["Risks"])  # Prefix defined in router
app.include_router(reports.router, prefix="/api", tags=["Reports"])