"""
Risk service for risk scoring, calculations, and business logic.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session

from ..models import Risk, Gap, Control


class RiskService:
    """Service for risk management operations."""
    
    # Risk scoring matrices
    LIKELIHOOD_VALUES = {
        "low": 1,
        "medium": 3,
        "high": 4,
        "very_high": 5,
    }
    
    IMPACT_VALUES = {
        "low": 1,
        "medium": 3,
        "high": 4,
        "critical": 5,
    }
    
    REVIEW_FREQUENCY_DAYS = {
        "monthly": 30,
        "quarterly": 90,
        "semi_annually": 180,
        "annually": 365,
    }
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_risk_score(self, likelihood: str, impact: str) -> int:
        """
        Calculate inherent risk score based on likelihood and impact.
        
        Risk Score = Likelihood Value × Impact Value
        
        Scale:
        - 1-4: Low risk
        - 5-9: Medium risk
        - 10-16: High risk
        - 20-25: Critical risk
        
        Args:
            likelihood: One of "low", "medium", "high", "very_high"
            impact: One of "low", "medium", "high", "critical"
        
        Returns:
            Risk score (integer 1-25)
        """
        l_value = self.LIKELIHOOD_VALUES.get(likelihood.lower(), 3)
        i_value = self.IMPACT_VALUES.get(impact.lower(), 3)
        
        return l_value * i_value
    
    def get_risk_level(self, risk_score: int) -> str:
        """
        Convert numerical risk score to risk level label.
        
        Args:
            risk_score: Numerical risk score (1-25)
        
        Returns:
            Risk level: "low", "medium", "high", or "critical"
        """
        if risk_score >= 20:
            return "critical"
        elif risk_score >= 10:
            return "high"
        elif risk_score >= 5:
            return "medium"
        else:
            return "low"
    
    def calculate_next_review_date(
        self,
        review_frequency: str,
        base_date: datetime = None
    ) -> datetime:
        """
        Calculate next review date based on review frequency.
        
        Args:
            review_frequency: One of "monthly", "quarterly", "semi_annually", "annually"
            base_date: Starting date for calculation (defaults to now)
        
        Returns:
            Next review datetime
        """
        if base_date is None:
            base_date = datetime.utcnow()
        
        days = self.REVIEW_FREQUENCY_DAYS.get(review_frequency, 90)
        return base_date + timedelta(days=days)
    
    def create_risk_from_gap(self, gap: Gap, control: Control) -> Risk:
        """
        Create a Risk entry from a Gap.
        
        Maps gap severity to likelihood and impact, generates risk title/statement.
        
        Args:
            gap: Gap model instance
            control: Control model instance
        
        Returns:
            Risk model instance (not yet committed)
        """
        # Map gap severity to risk parameters
        severity_mapping = {
            "critical": {"likelihood": "high", "impact": "critical"},
            "high": {"likelihood": "high", "impact": "high"},
            "medium": {"likelihood": "medium", "impact": "medium"},
            "low": {"likelihood": "low", "impact": "low"},
        }
        
        params = severity_mapping.get(gap.severity, {"likelihood": "medium", "impact": "medium"})
        
        # Generate risk title and statement
        risk_title = f"{control.csf_id}: {gap.gap_type.replace('_', ' ').title()}"
        risk_statement = f"{gap.description}\n\nControl: {control.name}\nGap Type: {gap.gap_type}"
        
        # Determine risk category based on control function
        category_mapping = {
            "Identify": "operational",
            "Protect": "technical",
            "Detect": "technical",
            "Respond": "operational",
            "Recover": "operational",
        }
        risk_category = category_mapping.get(control.function, "compliance")
        
        # Create risk
        risk = Risk(
            control_id=control.id,
            gap_id=gap.id,
            risk_title=risk_title,
            risk_statement=risk_statement,
            likelihood=params["likelihood"],
            impact=params["impact"],
            inherent_risk_score=self.calculate_risk_score(params["likelihood"], params["impact"]),
            treatment="mitigate",  # Default to mitigation
            status="open",
            risk_category=risk_category,
            review_frequency="quarterly",
            created_at=datetime.utcnow(),
        )
        
        # Set next review date
        risk.next_review_date = self.calculate_next_review_date("quarterly")
        
        return risk
    
    def generate_heatmap_data(self, risks: List[Risk]) -> Dict[str, int]:
        """
        Generate risk heat map data from a list of risks.
        
        Creates a matrix of counts for each likelihood/impact combination.
        
        Args:
            risks: List of Risk model instances
        
        Returns:
            Dictionary with keys like "low_low", "high_critical", etc., and count values
        """
        heatmap = {}
        
        # Initialize all cells to 0
        for likelihood in ["low", "medium", "high", "very_high"]:
            for impact in ["low", "medium", "high", "critical"]:
                key = f"{likelihood}_{impact}"
                heatmap[key] = 0
        
        # Count risks in each cell
        for risk in risks:
            key = f"{risk.likelihood}_{risk.impact}"
            heatmap[key] = heatmap.get(key, 0) + 1
        
        return heatmap
    
    def assess_control_risk(self, control_id: int, score_value: float) -> Dict[str, Any]:
        """
        Assess risk for a control based on its current score.
        
        Lower scores = higher risk.
        
        Args:
            control_id: Control ID
            score_value: Current control score (0.0 - 1.0)
        
        Returns:
            Dictionary with suggested likelihood, impact, and risk statement
        """
        # Map score to risk parameters
        if score_value == 0.0:
            return {
                "likelihood": "very_high",
                "impact": "critical",
                "risk_statement": "Control not implemented. No evidence of any security measures.",
            }
        elif score_value <= 0.33:
            return {
                "likelihood": "high",
                "impact": "high",
                "risk_statement": "Control minimally implemented. Significant gaps in coverage.",
            }
        elif score_value <= 0.66:
            return {
                "likelihood": "medium",
                "impact": "medium",
                "risk_statement": "Control partially implemented. Some gaps remain.",
            }
        else:
            return {
                "likelihood": "low",
                "impact": "low",
                "risk_statement": "Control mostly implemented. Minor improvements needed.",
            }
    
    def calculate_residual_risk(
        self,
        inherent_risk_score: int,
        mitigation_effectiveness: float
    ) -> int:
        """
        Calculate residual risk after mitigation.
        
        Residual Risk = Inherent Risk × (1 - Mitigation Effectiveness)
        
        Args:
            inherent_risk_score: Original risk score (1-25)
            mitigation_effectiveness: Mitigation effectiveness (0.0 - 1.0)
                                     e.g., 0.5 = 50% reduction
        
        Returns:
            Residual risk score (integer)
        """
        residual = inherent_risk_score * (1 - mitigation_effectiveness)
        return max(1, int(round(residual)))  # Minimum score of 1
    
    def is_risk_due_for_review(self, risk: Risk) -> bool:
        """
        Check if a risk is due for review.
        
        Args:
            risk: Risk model instance
        
        Returns:
            True if due for review, False otherwise
        """
        if not risk.next_review_date:
            return False
        
        return datetime.utcnow() >= risk.next_review_date
    
    def is_acceptance_expired(self, risk: Risk) -> bool:
        """
        Check if a risk acceptance has expired.
        
        Args:
            risk: Risk model instance
        
        Returns:
            True if acceptance is expired, False otherwise
        """
        if risk.treatment != "accept":
            return False
        
        if not risk.acceptance_expiry_date:
            return False
        
        return datetime.utcnow() >= risk.acceptance_expiry_date
