"""
Risk management API endpoints.

Provides CRUD operations for risk register, risk scoring,
heat map data, and risk analytics.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..database import get_session
from ..models import Risk, Control, Gap, Score
from ..services.risk_service import RiskService

router = APIRouter(prefix="/api/risks", tags=["risks"])


# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/", response_model=Risk)
def create_risk(risk: Risk, session: Session = Depends(get_session)):
    """
    Create a new risk entry.
    
    Automatically calculates inherent risk score based on likelihood and impact.
    """
    service = RiskService(session)
    
    # Calculate inherent risk score
    risk.inherent_risk_score = service.calculate_risk_score(risk.likelihood, risk.impact)
    
    # Set next review date if not provided
    if not risk.next_review_date:
        risk.next_review_date = service.calculate_next_review_date(
            risk.review_frequency, 
            risk.created_at
        )
    
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    return risk


@router.get("/", response_model=List[Risk])
def list_risks(
    status: Optional[str] = None,
    treatment: Optional[str] = None,
    risk_category: Optional[str] = None,
    control_id: Optional[int] = None,
    min_risk_score: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """
    List all risks with optional filtering.
    
    Query parameters:
    - status: Filter by risk status (open, under_review, accepted, mitigated, etc.)
    - treatment: Filter by treatment type (accept, mitigate, transfer, avoid)
    - risk_category: Filter by risk category (operational, technical, compliance, strategic)
    - control_id: Filter by specific control
    - min_risk_score: Filter risks with score >= this value
    """
    query = select(Risk)
    
    if status:
        query = query.where(Risk.status == status)
    if treatment:
        query = query.where(Risk.treatment == treatment)
    if risk_category:
        query = query.where(Risk.risk_category == risk_category)
    if control_id:
        query = query.where(Risk.control_id == control_id)
    if min_risk_score:
        query = query.where(Risk.inherent_risk_score >= min_risk_score)
    
    # Order by risk score (highest first), then by creation date
    query = query.order_by(Risk.inherent_risk_score.desc(), Risk.created_at.desc())
    
    risks = session.exec(query).all()
    return risks


@router.get("/{risk_id}", response_model=Risk)
def get_risk(risk_id: int, session: Session = Depends(get_session)):
    """Get a specific risk by ID."""
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.patch("/{risk_id}", response_model=Risk)
def update_risk(
    risk_id: int,
    risk_update: dict,
    session: Session = Depends(get_session)
):
    """
    Update a risk entry (partial update).
    
    Recalculates inherent risk score if likelihood or impact change.
    """
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    service = RiskService(session)
    
    # Update fields
    for key, value in risk_update.items():
        if hasattr(risk, key):
            setattr(risk, key, value)
    
    # Recalculate risk score if likelihood or impact changed
    if "likelihood" in risk_update or "impact" in risk_update:
        risk.inherent_risk_score = service.calculate_risk_score(
            risk.likelihood,
            risk.impact
        )
    
    # Update next review date if review frequency changed
    if "review_frequency" in risk_update:
        risk.next_review_date = service.calculate_next_review_date(
            risk.review_frequency,
            risk.last_reviewed_at or risk.created_at
        )
    
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    return risk


@router.delete("/{risk_id}")
def delete_risk(risk_id: int, session: Session = Depends(get_session)):
    """Delete a risk entry."""
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    session.delete(risk)
    session.commit()
    return {"message": "Risk deleted successfully"}


# ============================================================================
# Risk Analytics
# ============================================================================

@router.get("/summary/stats")
def get_risk_summary(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Get risk register summary statistics.
    
    Returns:
    - Total risk count
    - By status breakdown
    - By treatment breakdown
    - By risk level (critical/high/medium/low)
    - Average risk score
    - Due for review count
    """
    service = RiskService(session)
    
    # Total count
    total_query = select(func.count(Risk.id))
    total = session.exec(total_query).one()
    
    # By status
    status_query = select(Risk.status, func.count(Risk.id)).group_by(Risk.status)
    by_status = {row[0]: row[1] for row in session.exec(status_query).all()}
    
    # By treatment
    treatment_query = select(Risk.treatment, func.count(Risk.id)).group_by(Risk.treatment)
    by_treatment = {row[0]: row[1] for row in session.exec(treatment_query).all()}
    
    # By risk level (based on inherent risk score)
    risks = session.exec(select(Risk)).all()
    by_risk_level = {
        "critical": sum(1 for r in risks if r.inherent_risk_score >= 20),  # 20-25
        "high": sum(1 for r in risks if 15 <= r.inherent_risk_score < 20),  # 15-19
        "medium": sum(1 for r in risks if 9 <= r.inherent_risk_score < 15),  # 9-14
        "low": sum(1 for r in risks if r.inherent_risk_score < 9),  # 1-8
    }
    
    # Average risk score
    avg_score_query = select(func.avg(Risk.inherent_risk_score))
    avg_score = session.exec(avg_score_query).one() or 0.0
    
    # Due for review (next_review_date < today)
    today = datetime.utcnow()
    due_query = select(func.count(Risk.id)).where(
        Risk.next_review_date < today,
        Risk.status.in_(["open", "under_review", "accepted"])
    )
    due_for_review = session.exec(due_query).one()
    
    return {
        "total": total,
        "by_status": by_status,
        "by_treatment": by_treatment,
        "by_risk_level": by_risk_level,
        "average_risk_score": round(avg_score, 2),
        "due_for_review": due_for_review,
    }


@router.get("/heatmap/data")
def get_risk_heatmap(session: Session = Depends(get_session)) -> Dict[str, Any]:
    """
    Get risk heat map data.
    
    Returns a 5x4 matrix of risk counts by likelihood (rows) and impact (columns).
    Format: { "low_low": 2, "low_medium": 5, "medium_high": 8, ... }
    """
    service = RiskService(session)
    risks = session.exec(select(Risk)).all()
    
    heatmap_data = service.generate_heatmap_data(risks)
    
    return {
        "heatmap": heatmap_data,
        "total_risks": len(risks),
    }


@router.get("/top/highest")
def get_highest_risks(
    limit: int = 10,
    session: Session = Depends(get_session)
) -> List[Dict[str, Any]]:
    """
    Get top highest-risk entries (by inherent risk score).
    
    Returns risk details with associated control information.
    """
    query = select(Risk).order_by(Risk.inherent_risk_score.desc()).limit(limit)
    risks = session.exec(query).all()
    
    # Enrich with control details
    result = []
    for risk in risks:
        control = session.get(Control, risk.control_id)
        result.append({
            "risk_id": risk.id,
            "risk_title": risk.risk_title,
            "risk_score": risk.inherent_risk_score,
            "likelihood": risk.likelihood,
            "impact": risk.impact,
            "status": risk.status,
            "treatment": risk.treatment,
            "control_csf_id": control.csf_id if control else None,
            "control_name": control.name if control else None,
            "created_at": risk.created_at,
        })
    
    return result


@router.get("/due/reviews")
def get_risks_due_for_review(session: Session = Depends(get_session)) -> List[Risk]:
    """
    Get risks that are due for review (next_review_date has passed).
    
    Only includes open, under_review, and accepted risks.
    """
    today = datetime.utcnow()
    query = select(Risk).where(
        Risk.next_review_date < today,
        Risk.status.in_(["open", "under_review", "accepted"])
    ).order_by(Risk.next_review_date)
    
    risks = session.exec(query).all()
    return risks


# ============================================================================
# Risk Treatment Actions
# ============================================================================

@router.post("/{risk_id}/accept")
def accept_risk(
    risk_id: int,
    acceptance_data: dict,
    session: Session = Depends(get_session)
):
    """
    Accept a risk (change treatment to 'accept' and record approval).
    
    Required fields in acceptance_data:
    - acceptance_approver: Who approved
    - compensating_controls: Description of compensating controls (if any)
    - acceptance_expiry_date: When acceptance expires
    """
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    # Update risk with acceptance details
    risk.treatment = "accept"
    risk.status = "accepted"
    risk.acceptance_approver = acceptance_data.get("acceptance_approver")
    risk.compensating_controls = acceptance_data.get("compensating_controls")
    risk.acceptance_approved_at = datetime.utcnow()
    risk.acceptance_expiry_date = acceptance_data.get("acceptance_expiry_date")
    risk.treatment_rationale = acceptance_data.get("treatment_rationale")
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    
    return risk


@router.post("/{risk_id}/mitigate")
def mitigate_risk(
    risk_id: int,
    mitigation_data: dict,
    session: Session = Depends(get_session)
):
    """
    Set risk treatment to 'mitigate' and record mitigation plan.
    
    Required fields in mitigation_data:
    - mitigation_plan: Description of mitigation steps
    - mitigation_owner: Who owns the mitigation
    - mitigation_target_date: When mitigation should be complete
    - residual_risk_score: Expected risk score after mitigation
    """
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    # Update risk with mitigation details
    risk.treatment = "mitigate"
    risk.status = "under_review"
    risk.mitigation_plan = mitigation_data.get("mitigation_plan")
    risk.mitigation_owner = mitigation_data.get("mitigation_owner")
    risk.mitigation_target_date = mitigation_data.get("mitigation_target_date")
    risk.residual_risk_score = mitigation_data.get("residual_risk_score")
    risk.treatment_rationale = mitigation_data.get("treatment_rationale")
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    
    return risk


@router.post("/{risk_id}/close")
def close_risk(
    risk_id: int,
    closure_notes: str = "",
    session: Session = Depends(get_session)
):
    """
    Close a risk (mark as mitigated/resolved).
    """
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    risk.status = "closed"
    if closure_notes:
        risk.treatment_rationale = (risk.treatment_rationale or "") + f"\n\nClosure notes: {closure_notes}"
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    
    return risk


@router.post("/{risk_id}/review")
def mark_risk_reviewed(
    risk_id: int,
    review_notes: str = "",
    session: Session = Depends(get_session)
):
    """
    Mark a risk as reviewed and set next review date.
    """
    risk = session.get(Risk, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    service = RiskService(session)
    
    risk.last_reviewed_at = datetime.utcnow()
    risk.next_review_date = service.calculate_next_review_date(
        risk.review_frequency,
        risk.last_reviewed_at
    )
    
    if review_notes:
        risk.treatment_rationale = (risk.treatment_rationale or "") + f"\n\nReview ({risk.last_reviewed_at}): {review_notes}"
    
    risk.updated_at = datetime.utcnow()
    
    session.add(risk)
    session.commit()
    session.refresh(risk)
    
    return risk


# ============================================================================
# Risk Generation from Gaps
# ============================================================================

@router.post("/generate/from-gaps")
def generate_risks_from_gaps(session: Session = Depends(get_session)):
    """
    Auto-generate risk entries from open gaps with critical or high severity.
    
    Creates risks for gaps that don't already have associated risks.
    """
    service = RiskService(session)
    
    # Find critical/high gaps without associated risks
    gaps_query = select(Gap).where(
        Gap.status.in_(["open", "in_progress"]),
        Gap.severity.in_(["critical", "high"])
    )
    gaps = session.exec(gaps_query).all()
    
    # Check which gaps already have risks
    existing_risk_gap_ids = set(
        row[0] for row in session.exec(
            select(Risk.gap_id).where(Risk.gap_id.isnot(None))
        ).all()
    )
    
    new_risks = []
    for gap in gaps:
        if gap.id in existing_risk_gap_ids:
            continue  # Skip gaps that already have risks
        
        # Get control details
        control = session.get(Control, gap.control_id)
        if not control:
            continue
        
        # Create risk from gap
        risk = service.create_risk_from_gap(gap, control)
        session.add(risk)
        new_risks.append(risk)
    
    session.commit()
    
    return {
        "message": f"Generated {len(new_risks)} risks from gaps",
        "risks_created": len(new_risks),
    }
