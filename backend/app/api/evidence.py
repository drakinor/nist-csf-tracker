from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.models import Evidence, Control, ArtifactChunk
from app.services.scoring_service import ScoringService

router = APIRouter()


class EvidenceValidation(BaseModel):
    """Request model for validating evidence."""
    status: str  # accepted, rejected
    notes: Optional[str] = None
    evidence_type: Optional[str] = None  # policy, procedure, technical, operational
    confidence: Optional[float] = None


class EvidenceCreate(BaseModel):
    """Request model for creating evidence."""
    control_id: int
    artifact_id: int
    chunk_id: int
    snippet_text: str
    locator_json: dict
    evidence_type: Optional[str] = None
    notes: Optional[str] = None


@router.get("/", response_model=List[Evidence])
async def list_evidence(
    control_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List evidence with optional filtering."""
    statement = select(Evidence).offset(skip).limit(limit)
    
    if control_id:
        statement = statement.where(Evidence.control_id == control_id)
    if status:
        statement = statement.where(Evidence.status == status)
    
    evidence = session.exec(statement).all()
    return evidence


@router.get("/{evidence_id}", response_model=Evidence)
async def get_evidence(
    evidence_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific evidence record."""
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.post("/", response_model=Evidence)
async def create_evidence(
    evidence_data: EvidenceCreate,
    session: Session = Depends(get_session)
):
    """Create a new evidence record."""
    # Verify control exists
    control = session.get(Control, evidence_data.control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Verify chunk exists
    chunk = session.get(ArtifactChunk, evidence_data.chunk_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="Chunk not found")
    
    evidence = Evidence(
        control_id=evidence_data.control_id,
        artifact_id=evidence_data.artifact_id,
        chunk_id=evidence_data.chunk_id,
        snippet_text=evidence_data.snippet_text,
        locator_json=evidence_data.locator_json,
        evidence_type=evidence_data.evidence_type,
        notes=evidence_data.notes,
        status="pending"
    )
    
    session.add(evidence)
    session.commit()
    session.refresh(evidence)
    
    return evidence


@router.patch("/{evidence_id}/validate")
async def validate_evidence(
    evidence_id: int,
    validation: EvidenceValidation,
    session: Session = Depends(get_session)
):
    """Validate (accept or reject) evidence."""
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    # Update evidence
    evidence.status = validation.status
    evidence.notes = validation.notes
    evidence.evidence_type = validation.evidence_type
    evidence.confidence = validation.confidence
    evidence.validated_at = datetime.utcnow()
    
    session.add(evidence)
    session.commit()
    
    # Recalculate control score if accepted
    if validation.status == "accepted":
        scoring_service = ScoringService(session)
        scoring_service.calculate_control_score(evidence.control_id)
    
    session.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: int,
    session: Session = Depends(get_session)
):
    """Delete an evidence record."""
    evidence = session.get(Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    control_id = evidence.control_id
    session.delete(evidence)
    session.commit()
    
    # Recalculate control score
    scoring_service = ScoringService(session)
    scoring_service.calculate_control_score(control_id)
    
    return {"message": "Evidence deleted successfully"}
