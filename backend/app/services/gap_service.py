from typing import Dict, Any
from sqlmodel import Session, select
from app.models import Control, Score, Gap, Evidence


class GapService:
    """Service for identifying and generating gaps."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def generate_gaps(self) -> Dict[str, int]:
        """Generate gaps from control scores and evidence patterns."""
        statement = select(Control)
        controls = self.session.exec(statement).all()
        
        created = 0
        analyzed = 0
        
        for control in controls:
            analyzed += 1
            
            # Get control score
            score_statement = select(Score).where(Score.control_id == control.id)
            score = self.session.exec(score_statement).first()
            
            # Get evidence
            evidence_statement = select(Evidence).where(
                Evidence.control_id == control.id,
                Evidence.status == "accepted"
            )
            evidence_list = self.session.exec(evidence_statement).all()
            
            # Check if gap already exists
            existing_gap_statement = select(Gap).where(
                Gap.control_id == control.id,
                Gap.status == "open"
            )
            existing_gap = self.session.exec(existing_gap_statement).first()
            
            # Determine if gap should be created
            gap_type = None
            severity = "medium"
            description = ""
            
            if not score or score.score_value == 0.0:
                gap_type = "missing"
                severity = "high"
                description = f"No evidence found for {control.csf_id}: {control.name}"
            
            elif score.score_value < 0.5:
                # Check evidence types
                evidence_types = set(e.evidence_type for e in evidence_list if e.evidence_type)
                
                if evidence_types == {"policy"}:
                    gap_type = "policy_only"
                    severity = "medium"
                    description = f"Only policy evidence for {control.csf_id}. Missing procedures and technical controls."
                else:
                    gap_type = "incomplete"
                    severity = "medium"
                    description = f"Partial implementation of {control.csf_id}: {control.name}"
            
            # Create gap if needed and doesn't exist
            if gap_type and not existing_gap:
                gap = Gap(
                    control_id=control.id,
                    gap_type=gap_type,
                    description=description,
                    severity=severity,
                    status="open"
                )
                self.session.add(gap)
                created += 1
        
        self.session.commit()
        
        return {
            "created": created,
            "analyzed": analyzed
        }
