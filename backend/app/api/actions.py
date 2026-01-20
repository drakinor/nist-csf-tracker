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
    
    if action_data.status == "complete" and not action.completed_at:
        action.completed_at = datetime.utcnow()
    
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
