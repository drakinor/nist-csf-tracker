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

    # Score mapping (NIST Implementation Levels)
    SCORE_MAP = {
        "not-implemented": 0.0,
        "partially-implemented": 0.33,
        "largely-implemented": 0.66,
        "fully-implemented": 1.0
    }

    # Evidence type weights for advanced scoring
    EVIDENCE_WEIGHTS = {
        "policy": 0.25,        # Foundation - establishes rules
        "procedure": 0.25,     # Process - defines how to implement
        "technical": 0.30,     # Enforcement - technical controls
        "operational": 0.20,   # Proof - operational evidence of execution
        "assessment": 0.15     # Validation - independent verification
    }
    
    # Quality multipliers based on confidence level
    CONFIDENCE_MULTIPLIERS = {
        "high": 1.0,
        "medium": 0.85,
        "low": 0.70,
        None: 0.85  # Default for unspecified
    }

    def __init__(self, session: Session):
        self.session = session

    def calculate_control_score(self, control_id: int, trigger_rollup: bool = True) -> Score:
        """
        Calculate score for a single control based on ACCEPTED evidence only.
        Scoring is deterministic and follows NIST CSF spec rules.
        Includes both primary evidence (control_id) and linked evidence (via junction table).
        
        Args:
            control_id: The control to score
            trigger_rollup: If True, triggers category/function rollup recalculation (default: True)
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

        # STRICT ENFORCEMENT: Ensure score is exactly 0.0, 0.33, 0.66, or 1.0
        assert new_score_value in [0.0, 0.33, 0.66, 1.0], f"Invalid score: {new_score_value}"

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

        # GUARANTEE: Trigger rollup recalculation for affected function/category
        if trigger_rollup:
            self._ensure_rollups_updated(control_id)

        return score

    def _determine_score(self, evidence_list: List[Evidence]) -> tuple[float, str, str]:
        """
        Determine score based on evidence characteristics with STRICT enforcement.

        SPEC RULES (ENFORCED):
        - Scores MUST be exactly: 0.0, 0.33, 0.66, or 1.0 (no other values)
        - No evidence = 0.0 (missing_control)
        - Policy only = 0.33 (missing_procedure or missing_technical)
        - Policy + Procedure = 0.66 (missing_technical/operational)
        - Policy + Procedure + (Technical OR Operational) = 1.0
        - Assessment evidence strengthens confidence but doesn't replace implementation

        Returns: (score_value, score_label, rationale)
        """
        if not evidence_list:
            return 0.0, "not-implemented", "NONE: No validated evidence provided"

        # Count evidence by type (evidence-type composition rules)
        evidence_types = {e.evidence_type for e in evidence_list if e.evidence_type}
        evidence_count = {}
        for e in evidence_list:
            if e.evidence_type:
                evidence_count[e.evidence_type] = evidence_count.get(e.evidence_type, 0) + 1

        has_policy = "policy" in evidence_types
        has_procedure = "procedure" in evidence_types
        has_technical = "technical" in evidence_types
        has_operational = "operational" in evidence_types
        has_assessment = "assessment" in evidence_types

        # STRICT DETERMINISTIC SCORING with verbalizable rationale
        if has_policy and has_procedure and (has_technical or has_operational):
            # FULL = 1.0 (exactly)
            rationale_parts = [
                f"FULL: {evidence_count.get('policy', 0)} policy",
                f"{evidence_count.get('procedure', 0)} procedure"
            ]
            if has_technical and has_operational:
                rationale_parts.append(f"{evidence_count.get('technical', 0)} technical")
                rationale_parts.append(f"{evidence_count.get('operational', 0)} operational")
            elif has_technical:
                rationale_parts.append(f"{evidence_count.get('technical', 0)} technical")
            else:
                rationale_parts.append(f"{evidence_count.get('operational', 0)} operational")
            
            if has_assessment:
                rationale_parts.append(f"{evidence_count.get('assessment', 0)} assessment")
            
            rationale = " + ".join(rationale_parts) + " evidence validated"
            return 1.0, "fully-implemented", rationale

        elif has_policy and has_procedure:
            # MOSTLY = 0.66 (exactly)
            rationale_parts = [
                f"MOSTLY: {evidence_count.get('policy', 0)} policy",
                f"{evidence_count.get('procedure', 0)} procedure"
            ]
            if has_assessment:
                rationale_parts.append(f"{evidence_count.get('assessment', 0)} assessment")
                rationale = " + ".join(rationale_parts) + " evidence, missing enforcement"
            else:
                rationale = " + ".join(rationale_parts) + " evidence, missing technical/operational enforcement"
            return 0.66, "largely-implemented", rationale

        elif has_policy or has_procedure or has_technical or has_operational:
            # PARTIAL = 0.33 (exactly)
            rationale_parts = []
            for etype in ["policy", "procedure", "technical", "operational", "assessment"]:
                if etype in evidence_count:
                    rationale_parts.append(f"{evidence_count[etype]} {etype}")
            
            missing_parts = []
            if not has_policy:
                missing_parts.append("policy")
            if not has_procedure:
                missing_parts.append("procedure")
            if not (has_technical or has_operational):
                missing_parts.append("enforcement")
            
            rationale = f"PARTIAL: {', '.join(rationale_parts)} evidence, missing {', '.join(missing_parts)}"
            return 0.33, "partially-implemented", rationale

        else:
            # Should not reach here, but enforce 0.0 if we do
            return 0.0, "not-implemented", "NONE: No valid evidence types identified"


    def _calculate_weighted_score(self, evidence_list: List[Evidence]) -> tuple[float, str, str]:
        """
        Calculate score using weighted evidence approach with STRICT quantization.
        This provides more granular scoring than the basic boolean method.
        
        ENFORCEMENT: All scores are quantized to exactly 0.0, 0.33, 0.66, or 1.0
        
        Returns: (score_value, score_label, rationale)
        """
        if not evidence_list:
            return 0.0, "not-implemented", "NONE: No validated evidence"
        
        # Calculate weighted score
        total_weight = 0.0
        evidence_breakdown = {}
        
        for evidence in evidence_list:
            if not evidence.evidence_type:
                continue
                
            # Get base weight for evidence type
            base_weight = self.EVIDENCE_WEIGHTS.get(evidence.evidence_type, 0.1)
            
            # Apply confidence multiplier
            confidence_mult = self.CONFIDENCE_MULTIPLIERS.get(evidence.confidence, 0.85)
            
            # Calculate final weight
            weighted_value = base_weight * confidence_mult
            total_weight += weighted_value
            
            # Track evidence types for rationale
            if evidence.evidence_type not in evidence_breakdown:
                evidence_breakdown[evidence.evidence_type] = 0
            evidence_breakdown[evidence.evidence_type] += 1
        
        # Normalize score to 0.0 - 1.0 range
        # Cap at 1.0 (100%)
        normalized_score = min(total_weight, 1.0)
        
        # STRICT quantization to exactly 0.0, 0.33, 0.66, or 1.0
        if normalized_score >= 0.90:
            score_value = 1.0
            score_label = "fully-implemented"
            level = "FULL"
        elif normalized_score >= 0.60:
            score_value = 0.66
            score_label = "largely-implemented"
            level = "MOSTLY"
        elif normalized_score >= 0.25:
            score_value = 0.33
            score_label = "partially-implemented"
            level = "PARTIAL"
        else:
            score_value = 0.0
            score_label = "not-implemented"
            level = "NONE"
        
        # Build verbalizable rationale with counts
        evidence_summary = ", ".join([f"{count} {etype}" for etype, count in sorted(evidence_breakdown.items())])
        rationale = f"{level}: Weighted {normalized_score:.2f} from {evidence_summary} (quantized to {score_value})"
        
        return score_value, score_label, rationale
    
    def calculate_control_score_advanced(self, control_id: int, use_weighted: bool = False, trigger_rollup: bool = True) -> Score:
        """
        Calculate score with option to use weighted scoring.
        
        Args:
            control_id: The control to score
            use_weighted: If True, uses weighted scoring; if False, uses standard boolean logic
            trigger_rollup: If True, triggers rollup recalculation (default: True)
        """
        # Get evidence (same as standard method)
        primary_statement = select(Evidence).where(
            Evidence.control_id == control_id,
            Evidence.status == "accepted"
        )
        primary_evidence = self.session.exec(primary_statement).all()

        linked_statement = (
            select(Evidence)
            .join(EvidenceControlLink, Evidence.id == EvidenceControlLink.evidence_id)
            .where(
                EvidenceControlLink.control_id == control_id,
                Evidence.status == "accepted"
            )
        )
        linked_evidence = self.session.exec(linked_statement).all()
        all_evidence = list(primary_evidence) + list(linked_evidence)

        # Choose scoring method
        if use_weighted:
            new_score_value, new_score_label, rationale = self._calculate_weighted_score(all_evidence)
        else:
            new_score_value, new_score_label, rationale = self._determine_score(all_evidence)

        # STRICT ENFORCEMENT: Ensure score is exactly 0.0, 0.33, 0.66, or 1.0
        assert new_score_value in [0.0, 0.33, 0.66, 1.0], f"Invalid score: {new_score_value}"

        # Rest of the logic is same as calculate_control_score
        score_statement = select(Score).where(Score.control_id == control_id)
        score = self.session.exec(score_statement).first()

        if score:
            if score.score_value != new_score_value:
                event = ScoreEvent(
                    control_id=control_id,
                    old_score=score.score_value,
                    new_score=new_score_value,
                    old_label=score.score_label,
                    new_label=new_score_label,
                    reason=f"Score recalculation ({'weighted' if use_weighted else 'standard'}): {rationale}"
                )
                self.session.add(event)

            score.score_value = new_score_value
            score.score_label = new_score_label
            score.score_rationale = rationale
            score.calculated_at = datetime.utcnow()
        else:
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
        self._generate_gaps(control_id, new_score_value, all_evidence)

        # GUARANTEE: Trigger rollup recalculation
        if trigger_rollup:
            self._ensure_rollups_updated(control_id)

        return score
    
    def recalculate_all_scores_advanced(self, use_weighted: bool = False) -> dict:
        """Recalculate all control scores with option for weighted scoring."""
        from app.models import Control
        
        statement = select(Control)
        controls = self.session.exec(statement).all()
        
        updated = 0
        for control in controls:
            self.calculate_control_score_advanced(control.id, use_weighted=use_weighted)
            updated += 1
        
        return {
            "updated": updated,
            "total": len(controls),
            "method": "weighted" if use_weighted else "standard"
        }

    def _generate_gaps(self, control_id: int, score_value: float, evidence_list: List[Evidence]):
        """
        Generate or update gaps based on current score and evidence with DETERMINISTIC classification.
        Gaps are the inverse of the score - they identify what's missing.
        
        SPEC: Deterministic gap classification rules
        - Each gap type has explicit criteria
        - Severity is calculated based on score impact
        - Gap resolution is automatic when criteria are met
        """
        evidence_types = {e.evidence_type for e in evidence_list if e.evidence_type}

        # DETERMINISTIC GAP CLASSIFICATION
        expected_gaps = []

        # RULE 1: Missing Control (score = 0.0)
        if score_value == 0.0:
            expected_gaps.append({
                "gap_type": "missing_control",
                "description": "DETERMINISTIC: No validated evidence for this control",
                "severity": "critical",
                "acceptance_criteria": "Validate at least one piece of evidence (policy, procedure, technical, or operational)"
            })
        
        # RULE 2-5: Missing specific evidence types (only if score < 1.0)
        if score_value < 1.0:
            if "policy" not in evidence_types:
                expected_gaps.append({
                    "gap_type": "missing_policy",
                    "description": "DETERMINISTIC: No policy documentation validated for this control",
                    "severity": "high",
                    "acceptance_criteria": "Validate evidence of type 'policy' for this control"
                })
            
            if "procedure" not in evidence_types:
                # Severity escalates if we have policy but no procedure
                severity = "critical" if "policy" in evidence_types else "high"
                expected_gaps.append({
                    "gap_type": "missing_procedure",
                    "description": "DETERMINISTIC: No procedural documentation validated for this control",
                    "severity": severity,
                    "acceptance_criteria": "Validate evidence of type 'procedure' for this control"
                })
            
            if "technical" not in evidence_types and "operational" not in evidence_types:
                # High severity if we have policy+procedure but no enforcement
                severity = "high" if ("policy" in evidence_types and "procedure" in evidence_types) else "medium"
                expected_gaps.append({
                    "gap_type": "missing_technical_enforcement",
                    "description": "DETERMINISTIC: No technical or operational enforcement validated for this control",
                    "severity": severity,
                    "acceptance_criteria": "Validate evidence of type 'technical' OR 'operational' for this control"
                })
            
            # RULE 6: Incomplete implementation (some evidence, score < 1.0, not covered by above)
            if len(evidence_types) > 0:
                # Calculate what's still missing
                missing_types = []
                if "policy" not in evidence_types:
                    missing_types.append("policy")
                if "procedure" not in evidence_types:
                    missing_types.append("procedure")
                if "technical" not in evidence_types and "operational" not in evidence_types:
                    missing_types.append("enforcement (technical or operational)")
                
                if missing_types:  # Only add if there are specific missing pieces
                    expected_gaps.append({
                        "gap_type": "incomplete_implementation",
                        "description": f"DETERMINISTIC: Control partially implemented with {', '.join(evidence_types)}. Missing: {', '.join(missing_types)}",
                        "severity": "medium" if score_value >= 0.66 else "high",
                        "acceptance_criteria": f"Validate evidence for: {', '.join(missing_types)}"
                    })

        # Get existing gaps for this control (excluding resolved)
        existing_gaps = self.session.exec(
            select(Gap).where(
                Gap.control_id == control_id,
                Gap.status != "resolved"
            )
        ).all()

        # Create a map of existing gap types
        existing_gap_map = {g.gap_type: g for g in existing_gaps}

        # Add or update gaps
        for gap_data in expected_gaps:
            gap_type = gap_data["gap_type"]
            
            if gap_type not in existing_gap_map:
                # Create new gap
                new_gap = Gap(
                    control_id=control_id,
                    gap_type=gap_type,
                    description=gap_data["description"],
                    severity=gap_data["severity"],
                    status="open"
                )
                # Note: acceptance_criteria not in Gap model, stored in linked Action
                self.session.add(new_gap)
            else:
                # Update existing gap if severity changed
                existing_gap = existing_gap_map[gap_type]
                if existing_gap.severity != gap_data["severity"]:
                    existing_gap.severity = gap_data["severity"]
                if existing_gap.description != gap_data["description"]:
                    existing_gap.description = gap_data["description"]

        # AUTOMATIC CLOSURE: Resolve gaps that no longer apply (acceptance criteria met)
        expected_gap_types = {g["gap_type"] for g in expected_gaps}
        for gap in existing_gaps:
            if gap.gap_type not in expected_gap_types and gap.status == "open":
                # Acceptance criteria met - gap no longer applies
                gap.status = "resolved"
                gap.resolved_at = datetime.utcnow()
                print(f"AUTO-RESOLVED: Gap {gap.id} ({gap.gap_type}) - acceptance criteria met through evidence validation")

        self.session.commit()

    def _ensure_rollups_updated(self, control_id: int):
        """
        GUARANTEE: Ensure function and category rollups are recalculated when a control score changes.
        This method is called automatically after score updates to maintain data consistency.
        
        Args:
            control_id: The control whose score just changed
        """
        # Get the control to find its function and category
        from app.models import Control
        control_statement = select(Control).where(Control.id == control_id)
        control = self.session.exec(control_statement).first()
        
        if not control:
            return
        
        # Recalculate function score (in-memory, not persisted separately in this implementation)
        # The get_function_rollups() and get_category_rollups() methods calculate on-demand
        # This ensures they always reflect current state
        
        # NOTE: In a production system with cached rollups, you would update cached values here
        # For this implementation, rollups are always calculated fresh from Score table,
        # so they are automatically "updated" by virtue of the score change being committed
        
        # Log the rollup update for audit trail
        print(f"Rollups updated for control {control_id} (function: {control.function}, category: {control.category})")
        # Could add ScoreEvent here if we want to track rollup recalculations

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

    def get_overall_score(self) -> Dict[str, Any]:
        """Get overall score across all controls."""
        statement = select(Control, Score).join(Score, Control.id == Score.control_id, isouter=True)
        results = self.session.exec(statement).all()
        
        total_controls = len(results)
        if total_controls == 0:
            return {"average_score": 0.0, "total_controls": 0, "controls_with_evidence": 0}
        
        scores = [r[1].score_value if r[1] else 0.0 for r in results]
        controls_with_scores = sum(1 for r in results if r[1])
        
        return {
            "average_score": round(sum(scores) / total_controls, 2),
            "total_controls": total_controls,
            "controls_with_evidence": controls_with_scores
        }
    
    def get_function_rollups(self) -> List[Dict[str, Any]]:
        """Get score rollups by NIST CSF function."""
        functions = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
        rollups = []
        
        for func in functions:
            statement = (
                select(Control, Score)
                .join(Score, Control.id == Score.control_id, isouter=True)
                .where(Control.function == func)
            )
            results = self.session.exec(statement).all()
            
            if results:
                total_controls = len(results)
                scores = [r[1].score_value if r[1] else 0.0 for r in results]
                avg_score = sum(scores) / total_controls
                
                rollups.append({
                    "function": func,
                    "average_score": round(avg_score, 2),
                    "total_controls": total_controls,
                    "controls_with_evidence": sum(1 for r in results if r[1])
                })
        
        return rollups
    
    def get_category_rollups(self) -> List[Dict[str, Any]]:
        """Get score rollups by NIST CSF category."""
        statement = select(Control.category).distinct()
        categories = self.session.exec(statement).all()
        
        rollups = []
        for category in categories:
            cat_statement = (
                select(Control, Score)
                .join(Score, Control.id == Score.control_id, isouter=True)
                .where(Control.category == category)
            )
            results = self.session.exec(cat_statement).all()
            
            if results:
                total_controls = len(results)
                scores = [r[1].score_value if r[1] else 0.0 for r in results]
                avg_score = sum(scores) / total_controls
                
                rollups.append({
                    "category": category,
                    "average_score": round(avg_score, 2),
                    "total_controls": total_controls,
                    "controls_with_evidence": sum(1 for r in results if r[1])
                })
        
        return sorted(rollups, key=lambda x: x["category"])
    
    def get_needs_validation_count(self) -> int:
        """Count evidence items needing validation."""
        statement = select(func.count()).select_from(Evidence).where(Evidence.status == "pending")
        return self.session.exec(statement).one()
    def get_score_distribution(self) -> Dict[str, int]:
        '''Get count of controls by score level.'''
        statement = select(Score)
        scores = self.session.exec(statement).all()
        
        return {
            'full': sum(1 for s in scores if s.score_value >= 0.9),
            'mostly': sum(1 for s in scores if 0.6 <= s.score_value < 0.9),
            'partial': sum(1 for s in scores if 0.2 <= s.score_value < 0.6),
            'none': sum(1 for s in scores if s.score_value < 0.2)
        }
