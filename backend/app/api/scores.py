from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.database import get_session
from app.models import Score, ScoreEvent
from app.services.scoring_service import ScoringService

router = APIRouter()


@router.get("/", response_model=List[Score])
async def list_scores(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all control scores."""
    statement = select(Score).offset(skip).limit(limit)
    scores = session.exec(statement).all()
    return scores


@router.post("/recalculate-all")
async def recalculate_all_scores(
    session: Session = Depends(get_session)
):
    """Recalculate scores for all controls."""
    scoring_service = ScoringService(session)
    result = scoring_service.recalculate_all_scores()
    
    return {
        "message": "Scores recalculated",
        "controls_updated": result["updated"],
        "total_controls": result["total"]
    }


@router.get("/dashboard")
async def get_dashboard_summary(
    session: Session = Depends(get_session)
):
    """Get dashboard summary with overall statistics."""
    scoring_service = ScoringService(session)
    
    return {
        "overall": scoring_service.get_overall_score(),
        "by_function": scoring_service.get_function_rollups(),
        "by_category": scoring_service.get_category_rollups(),
        "needs_validation": scoring_service.get_needs_validation_count()
    }


@router.get("/history/{control_id}")
async def get_score_history(
    control_id: int,
    session: Session = Depends(get_session)
):
    """Get score change history for a control."""
    statement = select(ScoreEvent).where(
        ScoreEvent.control_id == control_id
    ).order_by(ScoreEvent.timestamp.desc())
    
    events = session.exec(statement).all()
    return events
