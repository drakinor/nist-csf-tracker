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
    
    if action_data.status == "done" and not action.completed_at:
        action.completed_at = datetime.utcnow()
    
    session.add(action)
    session.commit()
    session.refresh(action)
    return action
