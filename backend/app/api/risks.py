from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlmodel import Session, select
from app.database import get_session
from app.models import RiskAcceptance

router = APIRouter()


class RiskAcceptanceCreate(BaseModel):
    """Request model for creating a risk acceptance."""
    control_id: int
    risk_statement: str
    likelihood: str = "medium"
    impact: str = "medium"
    compensating_controls: Optional[str] = None
    approver: Optional[str] = None
    review_date: Optional[datetime] = None


@router.get("/", response_model=List[RiskAcceptance])
async def list_risk_acceptances(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List risk acceptance records with optional filtering."""
    statement = select(RiskAcceptance).offset(skip).limit(limit).order_by(
        RiskAcceptance.created_at.desc()
    )
    
    if status:
        statement = statement.where(RiskAcceptance.status == status)
    
    risks = session.exec(statement).all()
    return risks


@router.post("/", response_model=RiskAcceptance)
async def create_risk_acceptance(
    risk_data: RiskAcceptanceCreate,
    session: Session = Depends(get_session)
):
    """Create a new risk acceptance record."""
    risk = RiskAcceptance(**risk_data.dict())
    session.add(risk)
    session.commit()
    session.refresh(risk)
    return risk


@router.patch("/{risk_id}/approve")
async def approve_risk_acceptance(
    risk_id: int,
    approver: str,
    expiry_date: Optional[datetime] = None,
    session: Session = Depends(get_session)
):
    """Approve a risk acceptance."""
    risk = session.get(RiskAcceptance, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk acceptance not found")
    
    risk.status = "approved"
    risk.approver = approver
    risk.approved_at = datetime.utcnow()
    risk.expiry_date = expiry_date
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    return risk
