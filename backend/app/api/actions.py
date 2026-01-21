from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlmodel import Session, select
from app.database import get_session
from app.models import Action

router = APIRouter()


class ActionCreate(BaseModel):
    """Request model for creating an action."""
    gap_id: Optional[int] = None
    control_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    acceptance_criteria: Optional[str] = None


class ActionUpdate(BaseModel):
    """Request model for updating an action."""
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    acceptance_criteria: Optional[str] = None


@router.get("/", response_model=List[Action])
async def list_actions(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List action items with optional filtering."""
    statement = select(Action).offset(skip).limit(limit).order_by(Action.created_at.desc())
    
    if status:
        statement = statement.where(Action.status == status)
    
    actions = session.exec(statement).all()
    return actions


@router.post("/", response_model=Action)
async def create_action(
    action_data: ActionCreate,
    session: Session = Depends(get_session)
):
    """Create a new action item."""
    action = Action(**action_data.dict())
    session.add(action)
    session.commit()
    session.refresh(action)
    return action


@router.get("/{action_id}", response_model=Action)
async def get_action(
    action_id: int,
    session: Session = Depends(get_session)
):
    """Get a specific action by ID."""
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.patch("/{action_id}", response_model=Action)
async def update_action(
    action_id: int,
    action_data: ActionUpdate,
    session: Session = Depends(get_session)
):
    """Update an action item."""
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    update_dict = action_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(action, key, value)
    
    # ACCEPTANCE-CRITERIA-DRIVEN CLOSURE
    if action_data.status == "complete":
        if not action.completed_at:
            action.completed_at = datetime.utcnow()
        
        # Verify acceptance criteria
        if action.acceptance_criteria:
            print(f"ACTION COMPLETED: {action.title}")
            print(f"  Acceptance Criteria: {action.acceptance_criteria}")
            print(f"  Status: Meeting criteria - marking complete")
        
        # If linked to gap, check if gap can be resolved
        if action.gap_id:
            from app.models import Gap
            gap = session.get(Gap, action.gap_id)
            if gap and gap.status == "open":
                # Check if all actions for this gap are complete
                from sqlmodel import select
                gap_actions = session.exec(
                    select(Action).where(
                        Action.gap_id == action.gap_id,
                        Action.status != "complete"
                    )
                ).all()
                
                if len(gap_actions) == 0:  # All actions complete
                    gap.status = "resolved"
                    gap.resolved_at = datetime.utcnow()
                    print(f"GAP AUTO-RESOLVED: Gap {gap.id} - all linked actions complete")
    
    session.add(action)
    session.commit()
    session.refresh(action)
    return action


@router.delete("/{action_id}")
async def delete_action(
    action_id: int,
    session: Session = Depends(get_session)
):
    """Delete an action item."""
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    session.delete(action)
    session.commit()
    return {"message": "Action deleted successfully"}


@router.get("/summary/stats")
async def get_actions_summary(
    session: Session = Depends(get_session)
):
    """Get summary statistics for actions."""
    statement = select(Action)
    all_actions = session.exec(statement).all()
    
    by_status = {
        "open": len([a for a in all_actions if a.status == "open"]),
        "in_progress": len([a for a in all_actions if a.status == "in_progress"]),
        "blocked": len([a for a in all_actions if a.status == "blocked"]),
        "complete": len([a for a in all_actions if a.status == "complete"])
    }
    
    # Check for overdue actions
    now = datetime.utcnow()
    overdue = [
        a for a in all_actions 
        if a.due_date and a.due_date < now and a.status != "complete"
    ]
    
    # Group by owner
    by_owner = {}
    for action in all_actions:
        if action.owner and action.status != "complete":
            by_owner[action.owner] = by_owner.get(action.owner, 0) + 1
    
    return {
        "total_actions": len(all_actions),
        "by_status": by_status,
        "overdue_count": len(overdue),
        "by_owner": by_owner,
        "completion_rate": round(by_status["complete"] / len(all_actions) * 100, 1) if all_actions else 0
    }


@router.get("/kanban/board")
async def get_kanban_board(
    session: Session = Depends(get_session)
):
    """Get actions organized by status for Kanban view."""
    statement = select(Action).order_by(Action.created_at.desc())
    all_actions = session.exec(statement).all()
    
    kanban = {
        "open": [a for a in all_actions if a.status == "open"],
        "in_progress": [a for a in all_actions if a.status == "in_progress"],
        "blocked": [a for a in all_actions if a.status == "blocked"],
        "complete": [a for a in all_actions if a.status == "complete"]
    }
    
    return kanban


@router.post("/{action_id}/check-criteria")
async def check_acceptance_criteria(
    action_id: int,
    session: Session = Depends(get_session)
):
    """
    Check if acceptance criteria for an action are met.
    This is a helper endpoint to verify criteria before marking complete.
    """
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if not action.acceptance_criteria:
        return {
            "has_criteria": False,
            "message": "No acceptance criteria defined for this action",
            "can_close": True  # Can close without criteria (manual decision)
        }
    
    # If linked to gap, check gap status
    gap_resolved = False
    if action.gap_id:
        from app.models import Gap
        gap = session.get(Gap, action.gap_id)
        if gap:
            gap_resolved = gap.status == "resolved"
    
    # If linked to control, check if evidence exists
    evidence_exists = False
    if action.control_id:
        from app.models import Evidence
        from sqlmodel import select
        evidence = session.exec(
            select(Evidence).where(
                Evidence.control_id == action.control_id,
                Evidence.status == "accepted"
            ).limit(1)
        ).first()
        evidence_exists = evidence is not None
    
    return {
        "has_criteria": True,
        "acceptance_criteria": action.acceptance_criteria,
        "gap_resolved": gap_resolved,
        "evidence_exists": evidence_exists,
        "can_close": gap_resolved or evidence_exists,  # Automatic check
        "recommendation": (
            "✅ Acceptance criteria appear to be met - ready to close"
            if gap_resolved or evidence_exists
            else "⚠️ Acceptance criteria not yet met - additional work needed"
        )
    }
