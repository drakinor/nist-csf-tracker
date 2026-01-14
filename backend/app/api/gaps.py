from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.database import get_session
from app.models import Gap

router = APIRouter()


class GapCreate(BaseModel):
    """Request model for creating a gap."""
    control_id: int
    gap_type: str
    description: str
    severity: str = "medium"


@router.get("/", response_model=List[Gap])
async def list_gaps(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List gaps with optional filtering."""
    statement = select(Gap).offset(skip).limit(limit)
    
    if status:
        statement = statement.where(Gap.status == status)
    if severity:
        statement = statement.where(Gap.severity == severity)
    
    gaps = session.exec(statement).all()
    return gaps


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


@router.post("/generate")
async def generate_gaps(
    session: Session = Depends(get_session)
):
    """Generate gaps from missing/partial controls."""
    from app.services.gap_service import GapService
    
    gap_service = GapService(session)
    result = gap_service.generate_gaps()
    
    return {
        "message": "Gaps generated",
        "gaps_created": result["created"],
        "controls_analyzed": result["analyzed"]
    }
