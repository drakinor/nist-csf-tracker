from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from datetime import datetime
from app.database import get_session
from app.models import Gap, Control

router = APIRouter()


class GapCreate(BaseModel):
    """Request model for creating a gap."""
    control_id: int
    gap_type: str
    description: str
    severity: str = "medium"


class GapUpdate(BaseModel):
    """Request model for updating a gap."""
    status: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None


@router.get("/", response_model=List[Gap])
async def list_gaps(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    gap_type: Optional[str] = None,
    control_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List gaps with optional filtering."""
    statement = select(Gap).offset(skip).limit(limit).order_by(Gap.severity.desc(), Gap.created_at.desc())

    if status:
        statement = statement.where(Gap.status == status)
    if severity:
        statement = statement.where(Gap.severity == severity)
    if gap_type:
        statement = statement.where(Gap.gap_type == gap_type)
    if control_id:
        statement = statement.where(Gap.control_id == control_id)

    gaps = session.exec(statement).all()
    return gaps


@router.get("/summary")
async def get_gaps_summary(
    session: Session = Depends(get_session)
):
    """Get summary statistics for gaps."""
    statement = select(Gap)
    all_gaps = session.exec(statement).all()
    
    open_gaps = [g for g in all_gaps if g.status == "open"]
    
    by_severity = {
        "critical": len([g for g in open_gaps if g.severity == "critical"]),
        "high": len([g for g in open_gaps if g.severity == "high"]),
        "medium": len([g for g in open_gaps if g.severity == "medium"]),
        "low": len([g for g in open_gaps if g.severity == "low"])
    }
    
    by_type = {}
    for gap in open_gaps:
        by_type[gap.gap_type] = by_type.get(gap.gap_type, 0) + 1
    
    return {
        "total_gaps": len(all_gaps),
        "open_gaps": len(open_gaps),
        "by_severity": by_severity,
        "by_type": by_type,
        "resolved_gaps": len([g for g in all_gaps if g.status == "resolved"])
    }


@router.post("/", response_model=Gap)
async def create_gap(
    gap_data: GapCreate,
    session: Session = Depends(get_session)
):
    """Create a new gap record."""
    gap = Gap(**gap_data.dict())
    session.add(gap)
    session.commit()
    session.refresh(gap)
    return gap


@router.get("/{gap_id}", response_model=Gap)
async def get_gap(
    gap_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific gap by ID."""
    gap = session.get(Gap, gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    return gap


@router.patch("/{gap_id}", response_model=Gap)
async def update_gap(
    gap_id: int,
    gap_data: GapUpdate,
    session: Session = Depends(get_session)
):
    """Update a gap."""
    gap = session.get(Gap, gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail="Gap not found")
    
    update_dict = gap_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(gap, key, value)
    
    if gap_data.status == "resolved" and not gap.resolved_at:
        gap.resolved_at = datetime.utcnow()
    
    session.add(gap)
    session.commit()
    session.refresh(gap)
    return gap


@router.post("/regenerate")
async def regenerate_gaps(
    session: Session = Depends(get_session)
):
    """Regenerate gaps for all controls based on current scores."""
    from app.services.scoring_service import ScoringService
    
    scoring_service = ScoringService(session)
    result = scoring_service.recalculate_all_scores()
    
    # Count gaps created
    statement = select(Gap).where(Gap.status == "open")
    open_gaps = session.exec(statement).all()
    
    return {
        "message": "Gaps regenerated from current scores",
        "controls_scored": result["updated"],
        "open_gaps": len(open_gaps)
    }