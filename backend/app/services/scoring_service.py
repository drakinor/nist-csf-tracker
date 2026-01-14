from datetime import datetime
from typing import Dict, Any
from sqlmodel import Session, select, func
from app.models import Control, Evidence, Score, ScoreEvent


class ScoringService:
    """Service for calculating and managing control scores."""
    
    # Score mapping
    SCORE_MAP = {
        "none": 0.0,
        "partial": 0.33,
        "mostly": 0.66,
        "full": 1.0
    }
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_control_score(self, control_id: int) -> Score:
        """Calculate score for a single control based on evidence."""
        # Get accepted evidence count by type
        statement = select(Evidence).where(
            Evidence.control_id == control_id,
            Evidence.status == "accepted"
        )
        evidence_list = self.session.exec(statement).all()
        
        # Determine score based on evidence
        new_score_value, new_score_label = self._determine_score(evidence_list)
        
        # Get or create score record
        score_statement = select(Score).where(Score.control_id == control_id)
        score = self.session.exec(score_statement).first()
        
        if score:
            # Record change if different
            if score.score_value != new_score_value:
                event = ScoreEvent(
                    control_id=control_id,
                    old_score=score.score_value,
                    new_score=new_score_value,
                    old_label=score.score_label,
                    new_label=new_score_label,
                    reason="Evidence validation update"
                )
                self.session.add(event)
            
            # Update score
            score.score_value = new_score_value
            score.score_label = new_score_label
            score.calculated_at = datetime.utcnow()
        else:
            # Create new score
            score = Score(
                control_id=control_id,
                score_value=new_score_value,
                score_label=new_score_label,
                method="auto"
            )
            self.session.add(score)
        
        self.session.commit()
        self.session.refresh(score)
        
        return score
    
    def _determine_score(self, evidence_list: list) -> tuple[float, str]:
        """Determine score based on evidence characteristics."""
        if not evidence_list:
            return self.SCORE_MAP["none"], "none"
        
        # Count evidence by type
        evidence_types = {}
        for evidence in evidence_list:
            etype = evidence.evidence_type or "untyped"
            evidence_types[etype] = evidence_types.get(etype, 0) + 1
        
        # Scoring heuristics
        has_policy = evidence_types.get("policy", 0) > 0
        has_procedure = evidence_types.get("procedure", 0) > 0
        has_technical = evidence_types.get("technical", 0) > 0
        has_operational = evidence_types.get("operational", 0) > 0
        
        total_evidence = len(evidence_list)
        
        # Full implementation: multiple evidence types
        if sum([has_policy, has_procedure, has_technical, has_operational]) >= 3:
            return self.SCORE_MAP["full"], "full"
        
        # Mostly implemented: 2 evidence types or substantial evidence
        if sum([has_policy, has_procedure, has_technical, has_operational]) >= 2:
            return self.SCORE_MAP["mostly"], "mostly"
        
        # Partial: single evidence type or minimal evidence
        if total_evidence >= 2:
            return self.SCORE_MAP["mostly"], "mostly"
        
        return self.SCORE_MAP["partial"], "partial"
    
    def recalculate_all_scores(self) -> Dict[str, int]:
        """Recalculate scores for all controls."""
        statement = select(Control)
        controls = self.session.exec(statement).all()
        
        updated = 0
        for control in controls:
            self.calculate_control_score(control.id)
            updated += 1
        
        return {"updated": updated, "total": len(controls)}
    
    def get_overall_score(self) -> Dict[str, Any]:
        """Get overall compliance score."""
        statement = select(Score)
        scores = self.session.exec(statement).all()
        
        if not scores:
            return {
                "average_score": 0.0,
                "total_controls": 0,
                "scored_controls": 0,
                "percentage": 0.0
            }
        
        total_score = sum(s.score_value for s in scores)
        avg_score = total_score / len(scores) if scores else 0.0
        
        # Get total controls
        control_count = self.session.exec(select(func.count(Control.id))).one()
        
        return {
            "average_score": round(avg_score, 2),
            "total_controls": control_count,
            "scored_controls": len(scores),
            "percentage": round(avg_score * 100, 1)
        }
    
    def get_function_rollups(self) -> list[Dict[str, Any]]:
        """Get score rollups by function."""
        statement = select(Control)
        controls = self.session.exec(statement).all()
        
        # Group by function
        functions = {}
        for control in controls:
            if control.function not in functions:
                functions[control.function] = []
            functions[control.function].append(control.id)
        
        # Calculate average score per function
        results = []
        for function, control_ids in functions.items():
            scores = []
            for cid in control_ids:
                score_statement = select(Score).where(Score.control_id == cid)
                score = self.session.exec(score_statement).first()
                if score:
                    scores.append(score.score_value)
            
            avg = sum(scores) / len(scores) if scores else 0.0
            results.append({
                "function": function,
                "average_score": round(avg, 2),
                "percentage": round(avg * 100, 1),
                "total_controls": len(control_ids),
                "scored_controls": len(scores)
            })
        
        return sorted(results, key=lambda x: x["function"])
    
    def get_category_rollups(self) -> list[Dict[str, Any]]:
        """Get score rollups by category."""
        statement = select(Control)
        controls = self.session.exec(statement).all()
        
        # Group by category
        categories = {}
        for control in controls:
            if control.category not in categories:
                categories[control.category] = []
            categories[control.category].append(control.id)
        
        # Calculate average score per category
        results = []
        for category, control_ids in categories.items():
            scores = []
            for cid in control_ids:
                score_statement = select(Score).where(Score.control_id == cid)
                score = self.session.exec(score_statement).first()
                if score:
                    scores.append(score.score_value)
            
            avg = sum(scores) / len(scores) if scores else 0.0
            results.append({
                "category": category,
                "average_score": round(avg, 2),
                "percentage": round(avg * 100, 1),
                "total_controls": len(control_ids),
                "scored_controls": len(scores)
            })
        
        return sorted(results, key=lambda x: x["category"])
    
    def get_needs_validation_count(self) -> int:
        """Get count of evidence items needing validation."""
        statement = select(func.count(Evidence.id)).where(Evidence.status == "pending")
        count = self.session.exec(statement).one()
        return count
