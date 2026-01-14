from datetime import datetime
from typing import Dict, Any, List
from sqlmodel import Session, select, func
from app.models import Control, Evidence, Score, ScoreEvent, Gap, EvidenceControlLink


class ScoringService:
    """
    Service for calculating and managing control scores.

    SPEC COMPLIANCE:
    - Scores are DETERMINISTIC (0.0, 0.33, 0.66, 1.0 only)
    - Evidence MUST be human-validated (status=accepted)
    - Policy-only evidence CANNOT score 1.0
    - Full score requires: policy + procedure AND (technical OR operational)
    - Scores include rationale
    - Supports linked evidence (many-to-many via EvidenceControlLink)
    """

    # Score mapping (NIST CSF spec compliant)
    SCORE_MAP = {
        "none": 0.0,
        "partial": 0.33,
        "mostly": 0.66,
        "full": 1.0
    }

    def __init__(self, session: Session):
        self.session = session

    def calculate_control_score(self, control_id: int) -> Score:
        """
        Calculate score for a single control based on ACCEPTED evidence only.
        Scoring is deterministic and follows NIST CSF spec rules.
        Includes both primary evidence (control_id) and linked evidence (via junction table).
        """
        # Get ONLY accepted primary evidence
        primary_statement = select(Evidence).where(
            Evidence.control_id == control_id,
            Evidence.status == "accepted"
        )
        primary_evidence = self.session.exec(primary_statement).all()

        # Get ONLY accepted linked evidence
        linked_statement = (
            select(Evidence)
            .join(EvidenceControlLink, Evidence.id == EvidenceControlLink.evidence_id)
            .where(
                EvidenceControlLink.control_id == control_id,
                Evidence.status == "accepted"
            )
        )
        linked_evidence = self.session.exec(linked_statement).all()

        # Combine both primary and linked evidence for scoring
        all_evidence = list(primary_evidence) + list(linked_evidence)

        # Determine score based on evidence diversity
        new_score_value, new_score_label, rationale = self._determine_score(all_evidence)

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
                    reason=f"Evidence validation update: {rationale}"
                )
                self.session.add(event)

            # Update score
            score.score_value = new_score_value
            score.score_label = new_score_label
            score.score_rationale = rationale
            score.calculated_at = datetime.utcnow()
        else:
            # Create new score
            score = Score(
                control_id=control_id,
                score_value=new_score_value,
                score_label=new_score_label,
                score_rationale=rationale,
                method="auto"
            )
            self.session.add(score)

        self.session.commit()
        self.session.refresh(score)

        # Generate gaps based on score
        self._generate_gaps(control_id, new_score_value, all_evidence)

        return score

    def _determine_score(self, evidence_list: List[Evidence]) -> tuple[float, str, str]:
        """
        Determine score based on evidence characteristics.

        SPEC RULES:
        - No evidence = 0.0 (missing_control)
        - Policy only = 0.33 (missing_procedure or missing_technical)
        - Policy + Procedure = 0.66 (missing_technical/operational)
        - Policy + Procedure + (Technical OR Operational) = 1.0
        - Assessment evidence strengthens confidence but doesn't replace implementation

        Returns: (score_value, score_label, rationale)
        """
        if not evidence_list:
            return self.SCORE_MAP["none"], "none", "No validated evidence"

        # Count evidence by type
        evidence_types = {e.evidence_type for e in evidence_list if e.evidence_type}

        has_policy = "policy" in evidence_types
        has_procedure = "procedure" in evidence_types
        has_technical = "technical" in evidence_types
        has_operational = "operational" in evidence_types
        has_assessment = "assessment" in evidence_types

        # Determine score based on NIST CSF spec logic
        if has_policy and has_procedure and (has_technical or has_operational):
            # Full implementation
            rationale = "Policy, procedure, and "
            if has_technical and has_operational:
                rationale += "both technical and operational evidence"
            elif has_technical:
                rationale += "technical enforcement evidence"
            else:
                rationale += "operational evidence"
            
            if has_assessment:
                rationale += " with assessment validation"
            
            return self.SCORE_MAP["full"], "full", rationale

        elif has_policy and has_procedure:
            # Policy and procedure but missing enforcement
            rationale = "Policy and procedure documented"
            if has_assessment:
                rationale += " with assessment, but missing technical/operational enforcement"
            else:
                rationale += ", but missing technical/operational enforcement"
            return self.SCORE_MAP["mostly"], "mostly", rationale

        elif has_policy:
            # Policy only - spec says this CANNOT score 1.0
            rationale = "Policy documented only"
            if has_procedure:
                rationale += " with procedures"
            if has_assessment:
                rationale += ", plus assessment"
            rationale += ", but missing implementation evidence"
            return self.SCORE_MAP["partial"], "partial", rationale

        else:
            # Some evidence but not comprehensive
            types_found = ", ".join(evidence_types)
            rationale = f"Partial evidence ({types_found}), but missing policy foundation"
            return self.SCORE_MAP["partial"], "partial", rationale

    def _generate_gaps(self, control_id: int, score_value: float, evidence_list: List[Evidence]):
        """
        Generate or update gaps based on current score and evidence.
        Gaps are the inverse of the score - they identify what's missing.
        """
        evidence_types = {e.evidence_type for e in evidence_list if e.evidence_type}

        # Define expected gaps based on score
        expected_gaps = []

        if score_value == 0.0:
            # No evidence at all
            expected_gaps.append({
                "gap_type": "missing_control",
                "description": "No validated evidence for this control",
                "severity": "critical"
            })
        else:
            # Check for missing evidence types
            if "policy" not in evidence_types:
                expected_gaps.append({
                    "gap_type": "missing_policy",
                    "description": "No policy documentation validated for this control",
                    "severity": "high"
                })
            
            if "procedure" not in evidence_types:
                expected_gaps.append({
                    "gap_type": "missing_procedure",
                    "description": "No procedural documentation validated for this control",
                    "severity": "high" if "policy" in evidence_types else "critical"
                })
            
            if "technical" not in evidence_types:
                expected_gaps.append({
                    "gap_type": "missing_technical_enforcement",
                    "description": "No technical enforcement mechanism validated for this control",
                    "severity": "high"
                })
            
            if "operational" not in evidence_types:
                expected_gaps.append({
                    "gap_type": "missing_operational_evidence",
                    "description": "No operational evidence (logs, reports, assessments) validated for this control",
                    "severity": "medium"
                })
            
            # If we have some evidence but not full score
            if score_value < 1.0 and len(evidence_types) > 0:
                expected_gaps.append({
                    "gap_type": "incomplete_implementation",
                    "description": f"Control partially implemented: {', '.join(evidence_types)} present, but missing complete coverage",
                    "severity": "medium" if score_value >= 0.66 else "high"
                })

        # Get existing gaps for this control
        existing_gaps = self.session.exec(
            select(Gap).where(
                Gap.control_id == control_id,
                Gap.status != "resolved"
            )
        ).all()

        # Create a set of existing gap types
        existing_gap_types = {g.gap_type for g in existing_gaps}

        # Add new gaps
        for gap_data in expected_gaps:
            if gap_data["gap_type"] not in existing_gap_types:
                new_gap = Gap(
                    control_id=control_id,
                    gap_type=gap_data["gap_type"],
                    description=gap_data["description"],
                    severity=gap_data["severity"],
                    status="open"
                )
                self.session.add(new_gap)

        # Resolve gaps that no longer apply
        expected_gap_types = {g["gap_type"] for g in expected_gaps}
        for gap in existing_gaps:
            if gap.gap_type not in expected_gap_types and gap.status == "open":
                gap.status = "resolved"
                gap.resolved_at = datetime.utcnow()

        self.session.commit()

    def calculate_function_score(self, function_name: str) -> Dict[str, Any]:
        """Calculate aggregate score for a NIST CSF function."""
        statement = (
            select(Control, Score)
            .join(Score, Control.id == Score.control_id, isouter=True)
            .where(Control.function == function_name)
        )
        results = self.session.exec(statement).all()

        total_controls = len(results)
        if total_controls == 0:
            return {
                "function": function_name,
                "total_controls": 0,
                "avg_score": 0.0,
                "score_label": "none"
            }

        scores = [r[1].score_value if r[1] else 0.0 for r in results]
        avg_score = sum(scores) / total_controls

        # Map average to label
        if avg_score >= 0.9:
            score_label = "full"
        elif avg_score >= 0.6:
            score_label = "mostly"
        elif avg_score >= 0.2:
            score_label = "partial"
        else:
            score_label = "none"

        return {
            "function": function_name,
            "total_controls": total_controls,
            "avg_score": round(avg_score, 2),
            "score_label": score_label
        }

    def calculate_category_score(self, category_name: str) -> Dict[str, Any]:
        """Calculate aggregate score for a NIST CSF category."""
        statement = (
            select(Control, Score)
            .join(Score, Control.id == Score.control_id, isouter=True)
            .where(Control.category == category_name)
        )
        results = self.session.exec(statement).all()

        total_controls = len(results)
        if total_controls == 0:
            return {
                "category": category_name,
                "total_controls": 0,
                "avg_score": 0.0,
                "score_label": "none"
            }

        scores = [r[1].score_value if r[1] else 0.0 for r in results]
        avg_score = sum(scores) / total_controls

        # Map average to label
        if avg_score >= 0.9:
            score_label = "full"
        elif avg_score >= 0.6:
            score_label = "mostly"
        elif avg_score >= 0.2:
            score_label = "partial"
        else:
            score_label = "none"

        return {
            "category": category_name,
            "total_controls": total_controls,
            "avg_score": round(avg_score, 2),
            "score_label": score_label
        }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics."""
        # Get all controls with scores
        statement = (
            select(Control, Score)
            .join(Score, Control.id == Score.control_id, isouter=True)
        )
        results = self.session.exec(statement).all()

        total_controls = len(results)
        scores = [r[1].score_value if r[1] else 0.0 for r in results]
        overall_avg = sum(scores) / total_controls if total_controls > 0 else 0.0

        # Count by score label
        score_distribution = {
            "full": sum(1 for s in scores if s >= 0.9),
            "mostly": sum(1 for s in scores if 0.6 <= s < 0.9),
            "partial": sum(1 for s in scores if 0.2 <= s < 0.6),
            "none": sum(1 for s in scores if s < 0.2)
        }

        # Calculate function scores
        functions = ["Identify", "Protect", "Detect", "Respond", "Recover"]
        function_scores = []
        for func in functions:
            func_score = self.calculate_function_score(func)
            if func_score["total_controls"] > 0:
                function_scores.append(func_score)

        return {
            "total_controls": total_controls,
            "overall_score": round(overall_avg, 2),
            "score_distribution": score_distribution,
            "function_scores": function_scores,
            "last_updated": datetime.utcnow().isoformat()
        }