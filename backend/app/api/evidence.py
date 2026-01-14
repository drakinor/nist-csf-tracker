from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select, or_
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


class BulkEvidenceValidation(BaseModel):
    """Request model for bulk validating evidence."""
    evidence_ids: List[int]
    status: str  # accepted, rejected
    notes: Optional[str] = None
    evidence_type: Optional[str] = None
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
    evidence_type: Optional[str] = None,
    artifact_id: Optional[int] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List evidence with filtering and sorting."""
    statement = select(Evidence)
    
    # Apply filters
    if control_id:
        statement = statement.where(Evidence.control_id == control_id)
    if status:
        statement = statement.where(Evidence.status == status)
    if evidence_type:
        statement = statement.where(Evidence.evidence_type == evidence_type)
    if artifact_id:
        statement = statement.where(Evidence.artifact_id == artifact_id)
    if search:
        statement = statement.where(
            or_(
                Evidence.snippet_text.contains(search),
                Evidence.notes.contains(search)
            )
        )
    
    # Apply sorting
    if sort_by == "created_at":
        statement = statement.order_by(Evidence.created_at.desc() if sort_order == "desc" else Evidence.created_at.asc())
    elif sort_by == "validated_at":
        statement = statement.order_by(Evidence.validated_at.desc() if sort_order == "desc" else Evidence.validated_at.asc())
    elif sort_by == "confidence":
        statement = statement.order_by(Evidence.confidence.desc() if sort_order == "desc" else Evidence.confidence.asc())
    elif sort_by == "status":
        statement = statement.order_by(Evidence.status.desc() if sort_order == "desc" else Evidence.status.asc())
    
    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    
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


@router.post("/bulk-validate")
async def bulk_validate_evidence(
    validation: BulkEvidenceValidation,
    session: Session = Depends(get_session)
):
    """Bulk validate (accept or reject) multiple evidence items."""
    updated_count = 0
    affected_controls = set()
    
    for evidence_id in validation.evidence_ids:
        evidence = session.get(Evidence, evidence_id)
        if evidence:
            evidence.status = validation.status
            if validation.notes:
                evidence.notes = validation.notes
            if validation.evidence_type:
                evidence.evidence_type = validation.evidence_type
            if validation.confidence is not None:
                evidence.confidence = validation.confidence
            evidence.validated_at = datetime.utcnow()
            
            session.add(evidence)
            affected_controls.add(evidence.control_id)
            updated_count += 1
    
    session.commit()
    
    # Recalculate scores for affected controls if accepted
    if validation.status == "accepted":
        scoring_service = ScoringService(session)
        for control_id in affected_controls:
            scoring_service.calculate_control_score(control_id)
    
    return {
        "message": f"Bulk validation complete",
        "updated": updated_count,
        "total_requested": len(validation.evidence_ids),
        "affected_controls": len(affected_controls)
    }


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


@router.post("/bulk-delete")
async def bulk_delete_evidence(
    evidence_ids: List[int],
    session: Session = Depends(get_session)
):
    """Bulk delete multiple evidence items."""
    deleted_count = 0
    affected_controls = set()
    
    for evidence_id in evidence_ids:
        evidence = session.get(Evidence, evidence_id)
        if evidence:
            affected_controls.add(evidence.control_id)
            session.delete(evidence)
            deleted_count += 1
    
    session.commit()
    
    # Recalculate scores for affected controls
    scoring_service = ScoringService(session)
    for control_id in affected_controls:
        scoring_service.calculate_control_score(control_id)
    
    return {
        "message": f"Bulk delete complete",
        "deleted": deleted_count,
        "total_requested": len(evidence_ids),
        "affected_controls": len(affected_controls)
    }