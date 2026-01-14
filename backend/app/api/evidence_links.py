"""
Evidence linking API endpoints for managing many-to-many relationships
between evidence and controls.
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import engine
from app.models import EvidenceControlLink, Evidence, Control

router = APIRouter()


class LinkEvidenceRequest(BaseModel):
    control_id: int
    relevance_notes: Optional[str] = None
    linked_by: Optional[str] = None


class LinkResponse(BaseModel):
    id: int
    evidence_id: int
    control_id: int
    relevance_notes: Optional[str]
    linked_at: datetime
    linked_by: Optional[str]


@router.post("/evidence/{evidence_id}/link", response_model=LinkResponse)
def link_evidence_to_control(evidence_id: int, request: LinkEvidenceRequest):
    """Link an evidence item to an additional control."""
    with Session(engine) as session:
        # Verify evidence exists
        evidence = session.get(Evidence, evidence_id)
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        # Verify control exists
        control = session.get(Control, request.control_id)
        if not control:
            raise HTTPException(status_code=404, detail="Control not found")
        
        # Check if link already exists
        existing = session.exec(
            select(EvidenceControlLink)
            .where(EvidenceControlLink.evidence_id == evidence_id)
            .where(EvidenceControlLink.control_id == request.control_id)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Evidence is already linked to this control"
            )
        
        # Create link
        link = EvidenceControlLink(
            evidence_id=evidence_id,
            control_id=request.control_id,
            relevance_notes=request.relevance_notes,
            linked_by=request.linked_by,
            linked_at=datetime.utcnow()
        )
        session.add(link)
        session.commit()
        session.refresh(link)
        
        return link


@router.delete("/evidence/{evidence_id}/link/{control_id}")
def unlink_evidence_from_control(evidence_id: int, control_id: int):
    """Remove the link between an evidence item and a control."""
    with Session(engine) as session:
        link = session.exec(
            select(EvidenceControlLink)
            .where(EvidenceControlLink.evidence_id == evidence_id)
            .where(EvidenceControlLink.control_id == control_id)
        ).first()
        
        if not link:
            raise HTTPException(
                status_code=404,
                detail="Link not found between this evidence and control"
            )
        
        session.delete(link)
        session.commit()
        
        return {"message": "Link removed successfully"}


@router.get("/evidence/{evidence_id}/links", response_model=List[LinkResponse])
def get_evidence_links(evidence_id: int):
    """Get all control links for a specific evidence item."""
    with Session(engine) as session:
        # Verify evidence exists
        evidence = session.get(Evidence, evidence_id)
        if not evidence:
            raise HTTPException(status_code=404, detail="Evidence not found")
        
        links = session.exec(
            select(EvidenceControlLink)
            .where(EvidenceControlLink.evidence_id == evidence_id)
        ).all()
        
        return links


@router.get("/controls/{control_id}/linked-evidence")
def get_control_linked_evidence(control_id: int):
    """
    Get all evidence for a control, including both primary and linked evidence.
    Returns:
        {
            "primary": [...],  # Evidence where control_id matches
            "linked": [...]    # Evidence linked via EvidenceControlLink
        }
    """
    with Session(engine) as session:
        # Verify control exists
        control = session.get(Control, control_id)
        if not control:
            raise HTTPException(status_code=404, detail="Control not found")
        
        # Get primary evidence (direct control_id relationship)
        primary_evidence = session.exec(
            select(Evidence)
            .where(Evidence.control_id == control_id)
        ).all()
        
        # Get linked evidence (via junction table)
        links = session.exec(
            select(EvidenceControlLink)
            .where(EvidenceControlLink.control_id == control_id)
        ).all()
        
        linked_evidence = []
        for link in links:
            evidence = session.get(Evidence, link.evidence_id)
            if evidence:
                linked_evidence.append({
                    "evidence": evidence,
                    "link": link
                })
        
        return {
            "primary": primary_evidence,
            "linked": linked_evidence
        }