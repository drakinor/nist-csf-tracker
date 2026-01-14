from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_session
from app.models import Control, Evidence, Score
from app.services.candidate_service import CandidateService

router = APIRouter()


@router.get("/", response_model=List[Control])
async def list_controls(
    function: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all NIST CSF controls with optional filtering."""
    statement = select(Control).offset(skip).limit(limit)
    
    if function:
        statement = statement.where(Control.function == function)
    if category:
        statement = statement.where(Control.category == category)
    
    controls = session.exec(statement).all()
    return controls


@router.get("/{control_id}", response_model=Control)
async def get_control(
    control_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific control by ID."""
    control = session.get(Control, control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control


@router.get("/{control_id}/evidence")
async def get_control_evidence(
    control_id: int,
    session: Session = Depends(get_session)
):
    """Get all evidence for a specific control."""
    statement = select(Evidence).where(Evidence.control_id == control_id)
    evidence = session.exec(statement).all()
    return evidence


@router.get("/{control_id}/candidates")
async def get_evidence_candidates(
    control_id: int,
    limit: int = Query(default=20, le=100),
    session: Session = Depends(get_session)
):
    """Get evidence candidates for a control (EPIC 3)."""
    control = session.get(Control, control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    candidate_service = CandidateService(session)
    candidates = candidate_service.find_candidates(control, limit=limit)
    
    return {
        "control_id": control_id,
        "csf_id": control.csf_id,
        "candidates": candidates
    }


@router.get("/{control_id}/score")
async def get_control_score(
    control_id: int,
    session: Session = Depends(get_session)
):
    """Get the current score for a control."""
    statement = select(Score).where(Score.control_id == control_id)
    score = session.exec(statement).first()
    
    if not score:
        return {
            "control_id": control_id,
            "score_value": 0.0,
            "score_label": "none",
            "message": "No score calculated yet"
        }
    
    return score


@router.get("/functions/summary")
async def get_functions_summary(
    session: Session = Depends(get_session)
):
    """Get score summary by function."""
    from app.services.scoring_service import ScoringService
    
    scoring_service = ScoringService(session)
    return scoring_service.get_function_rollups()


@router.get("/categories/summary")
async def get_categories_summary(
    session: Session = Depends(get_session)
):
    """Get score summary by category."""
    from app.services.scoring_service import ScoringService
    
    scoring_service = ScoringService(session)
    return scoring_service.get_category_rollups()
