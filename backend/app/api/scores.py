from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.models import Score, ScoreEvent, ScoreSnapshot
from app.services.scoring_service import ScoringService

router = APIRouter()


class ManualScoreOverride(BaseModel):
    """Request model for manual score override."""
    score_value: float
    score_label: str
    notes: str
    user: str = "admin"


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


@router.post("/{control_id}/override")
async def override_score(
    control_id: int,
    override: ManualScoreOverride,
    session: Session = Depends(get_session)
):
    """Manually override a control's score."""
    # Validate score values
    valid_scores = {0.0: "none", 0.33: "partial", 0.66: "mostly", 1.0: "full"}
    if override.score_value not in valid_scores:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid score value. Must be one of: {list(valid_scores.keys())}"
        )
    
    if override.score_label not in valid_scores.values():
        raise HTTPException(
            status_code=400,
            detail=f"Invalid score label. Must be one of: {list(valid_scores.values())}"
        )
    
    # Validate consistency
    if valid_scores[override.score_value] != override.score_label:
        raise HTTPException(
            status_code=400,
            detail=f"Score value {override.score_value} does not match label '{override.score_label}'"
        )
    
    # Get existing score
    statement = select(Score).where(Score.control_id == control_id)
    existing_score = session.exec(statement).first()
    
    if not existing_score:
        raise HTTPException(status_code=404, detail="Score not found for this control")
    
    # Create score event for audit trail
    score_event = ScoreEvent(
        control_id=control_id,
        old_score=existing_score.score_value,
        new_score=override.score_value,
        old_label=existing_score.score_label,
        new_label=override.score_label,
        user=override.user,
        reason=f"Manual override: {override.notes}"
    )
    session.add(score_event)
    
    # Update score
    existing_score.score_value = override.score_value
    existing_score.score_label = override.score_label
    existing_score.method = "manual"
    existing_score.notes = override.notes
    existing_score.score_rationale = f"Manual override by {override.user}"
    
    session.add(existing_score)
    session.commit()
    session.refresh(existing_score)
    
    return {
        "message": "Score updated successfully",
        "score": existing_score,
        "event_id": score_event.id
    }


@router.get("/dashboard")
async def get_dashboard_summary(
    session: Session = Depends(get_session)
):
    """Get dashboard summary with overall statistics."""
    scoring_service = ScoringService(session)
    
    overall_data = scoring_service.get_overall_score()
    function_rollups = scoring_service.get_function_rollups()
    category_rollups = scoring_service.get_category_rollups()
    
    # Format for frontend expectations
    overall = {
        "percentage": round(overall_data["average_score"] * 100),
        "scored_controls": overall_data["controls_with_evidence"],
        "total_controls": overall_data["total_controls"]
    }
    
    # Format function rollups for frontend
    by_function = []
    for func in function_rollups:
        by_function.append({
            "function": func["function"],
            "percentage": round(func["average_score"] * 100),
            "scored_controls": func["controls_with_evidence"],
            "total_controls": func["total_controls"]
        })
    
    # Format category rollups for frontend
    by_category = []
    for cat in category_rollups:
        by_category.append({
            "category": cat["category"],
            "percentage": round(cat["average_score"] * 100),
            "scored_controls": cat["controls_with_evidence"],
            "total_controls": cat["total_controls"]
        })

    return {
        "overall": overall,
        "by_function": by_function,
        "by_category": by_category,
        "score_distribution": scoring_service.get_score_distribution(),
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


@router.get("/lowest")
async def get_lowest_scoring_controls(
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """Get the lowest scoring controls to prioritize improvement efforts."""
    from app.models import Control
    
    # Get all scores with their control information
    statement = select(Score, Control).join(Control).order_by(Score.score_value.asc()).limit(limit)
    results = session.exec(statement).all()
    
    lowest_controls = []
    for score, control in results:
        lowest_controls.append({
            "control_id": control.id,
            "csf_id": control.csf_id,
            "name": control.name,
            "function": control.function,
            "category": control.category,
            "score_value": score.score_value,
            "score_label": score.score_label,
            "method": score.method
        })
    
    return lowest_controls

@router.post("/snapshot")
async def create_score_snapshot(
    session: Session = Depends(get_session)
):
    """Create a snapshot of current scores for historical tracking."""
    from datetime import datetime
    
    scoring_service = ScoringService(session)
    
    # Get current dashboard data
    overall_data = scoring_service.get_overall_score()
    function_rollups = scoring_service.get_function_rollups()
    category_rollups = scoring_service.get_category_rollups()
    score_distribution = scoring_service.get_score_distribution()
    
    # Create function scores dict
    function_scores_dict = {}
    for func in function_rollups:
        function_scores_dict[func["function"]] = round(func["average_score"] * 100)
    
    # Create category scores dict
    category_scores_dict = {}
    for cat in category_rollups:
        category_scores_dict[cat["category"]] = round(cat["average_score"] * 100)
    
    # Create snapshot
    snapshot = ScoreSnapshot(
        snapshot_date=datetime.utcnow(),
        overall_percentage=round(overall_data["average_score"] * 100),
        total_controls=overall_data["total_controls"],
        scored_controls=overall_data["controls_with_evidence"],
        function_scores=function_scores_dict,
        category_scores=category_scores_dict,
        score_distribution=score_distribution
    )
    
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    
    return {
        "message": "Snapshot created successfully",
        "snapshot_id": snapshot.id,
        "snapshot_date": snapshot.snapshot_date.isoformat()
    }




@router.post("/recalculate-weighted")
async def recalculate_weighted_scores(
    session: Session = Depends(get_session)
):
    """Recalculate scores using weighted evidence approach."""
    scoring_service = ScoringService(session)
    result = scoring_service.recalculate_all_scores_advanced(use_weighted=True)

    return {
        "message": "Scores recalculated using weighted method",
        "controls_updated": result["updated"],
        "total_controls": result["total"],
        "method": result["method"]
    }

@router.get("/trends")
async def get_score_trends(
    days: int = 30,
    session: Session = Depends(get_session)
):
    """Get historical score trends for the last N days."""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    statement = select(ScoreSnapshot).where(
        ScoreSnapshot.snapshot_date >= cutoff_date
    ).order_by(ScoreSnapshot.snapshot_date.asc())
    
    snapshots = session.exec(statement).all()
    
    # Format for frontend chart consumption
    overall_trend = []
    function_trends = {}
    
    for snapshot in snapshots:
        date_str = snapshot.snapshot_date.strftime("%Y-%m-%d")
        
        overall_trend.append({
            "date": date_str,
            "percentage": snapshot.overall_percentage,
            "scored_controls": snapshot.scored_controls,
            "total_controls": snapshot.total_controls
        })
        
        # Build function trends
        if snapshot.function_scores:
            for func_name, percentage in snapshot.function_scores.items():
                if func_name not in function_trends:
                    function_trends[func_name] = []
                function_trends[func_name].append({
                    "date": date_str,
                    "percentage": percentage
                })
    
    return {
        "overall": overall_trend,
        "by_function": function_trends,
        "period_days": days,
        "snapshots_count": len(snapshots)
    }
