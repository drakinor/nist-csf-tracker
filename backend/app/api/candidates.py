from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.models import Control
from app.services.candidate_service import CandidateService

router = APIRouter()


@router.get("/controls/{control_id}/candidates")
async def find_candidates(
    control_id: int,
    limit: int = 20,
    session: Session = Depends(get_session)
):
    """Find evidence candidates for a control."""
    control = session.get(Control, control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    candidate_service = CandidateService(session)
    candidates = candidate_service.find_candidates(control, limit=limit)
    
    return {
        "control_id": control_id,
        "control_name": control.name,
        "csf_id": control.csf_id,
        "candidates": candidates,
        "count": len(candidates)
    }


@router.get("/artifacts/{artifact_id}/candidates")
async def find_artifact_candidates(
    artifact_id: int,
    session: Session = Depends(get_session)
):
    """Find all control candidates that match chunks in an artifact."""
    # This would scan all controls and find matches for the artifact's chunks
    # Not implemented in this version
    raise HTTPException(status_code=501, detail="Not implemented yet")
