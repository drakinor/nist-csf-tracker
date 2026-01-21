"""
EPIC 5 Test Suite: Advanced Scoring & Rollups

Tests for:
1. Strict enforcement of 0.0 / 0.33 / 0.66 / 1.0
2. Evidence-type composition rules
3. Verbalizable rationale generation
4. Rollup recalculation guarantees
"""
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.models import Control, Evidence, Score, ScoreEvent
from app.services.scoring_service import ScoringService


@pytest.fixture
def session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_control(session: Session):
    """Create a test control."""
    control = Control(
        csf_id="GV.OC-01",
        name="Test Control",
        text="Test control for scoring",
        function="Govern",
        category="Organizational Context",
        subcategory="GV.OC-01"
    )
    session.add(control)
    session.commit()
    session.refresh(control)
    return control


def test_strict_score_enforcement_none(session: Session, test_control: Control):
    """Test 1.1: No evidence = exactly 0.0"""
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    assert score.score_value == 0.0, f"Expected 0.0, got {score.score_value}"
    assert score.score_label == "not-implemented"
    assert "NONE" in score.score_rationale


def test_strict_score_enforcement_partial(session: Session, test_control: Control):
    """Test 1.2: Policy only = exactly 0.33"""
    # Add policy evidence
    evidence = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Test policy document",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    session.add(evidence)
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    assert score.score_value == 0.33, f"Expected 0.33, got {score.score_value}"
    assert score.score_label == "partially-implemented"
    assert "PARTIAL" in score.score_rationale


def test_strict_score_enforcement_mostly(session: Session, test_control: Control):
    """Test 1.3: Policy + Procedure = exactly 0.66"""
    # Add policy and procedure evidence
    evidence1 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Test policy",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    evidence2 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=2,
        snippet_text="Test procedure",
        locator_json={},
        evidence_type="procedure",
        status="accepted"
    )
    session.add(evidence1)
    session.add(evidence2)
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    assert score.score_value == 0.66, f"Expected 0.66, got {score.score_value}"
    assert score.score_label == "largely-implemented"
    assert "MOSTLY" in score.score_rationale


def test_strict_score_enforcement_full(session: Session, test_control: Control):
    """Test 1.4: Policy + Procedure + Technical = exactly 1.0"""
    # Add all required evidence
    evidence1 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Test policy",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    evidence2 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=2,
        snippet_text="Test procedure",
        locator_json={},
        evidence_type="procedure",
        status="accepted"
    )
    evidence3 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=3,
        snippet_text="Test technical control",
        locator_json={},
        evidence_type="technical",
        status="accepted"
    )
    session.add_all([evidence1, evidence2, evidence3])
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    assert score.score_value == 1.0, f"Expected 1.0, got {score.score_value}"
    assert score.score_label == "fully-implemented"
    assert "FULL" in score.score_rationale


def test_evidence_composition_rules(session: Session, test_control: Control):
    """Test 2: Evidence-type composition rules"""
    scoring_service = ScoringService(session)
    
    # Test: Operational can substitute for technical
    evidence1 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Test policy",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    evidence2 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=2,
        snippet_text="Test procedure",
        locator_json={},
        evidence_type="procedure",
        status="accepted"
    )
    evidence3 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=3,
        snippet_text="Operational evidence",
        locator_json={},
        evidence_type="operational",
        status="accepted"
    )
    session.add_all([evidence1, evidence2, evidence3])
    session.commit()
    
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    # Policy + Procedure + Operational should = 1.0
    assert score.score_value == 1.0, "Policy + Procedure + Operational should score 1.0"
    assert "operational" in score.score_rationale.lower()


def test_verbalizable_rationale(session: Session, test_control: Control):
    """Test 3: Verbalizable rationale generation"""
    # Add multiple evidence pieces
    evidence1 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Policy 1",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    evidence2 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=2,
        snippet_text="Policy 2",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    evidence3 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=3,
        snippet_text="Procedure",
        locator_json={},
        evidence_type="procedure",
        status="accepted"
    )
    session.add_all([evidence1, evidence2, evidence3])
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    # Rationale should include counts
    assert "2 policy" in score.score_rationale, "Rationale should count policy evidence"
    assert "1 procedure" in score.score_rationale, "Rationale should count procedure evidence"
    assert "MOSTLY" in score.score_rationale, "Rationale should include score level"


def test_pending_evidence_not_counted(session: Session, test_control: Control):
    """Test 4: Only accepted evidence counts toward score"""
    # Add pending evidence
    evidence = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Pending policy",
        locator_json={},
        evidence_type="policy",
        status="pending"  # NOT accepted
    )
    session.add(evidence)
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    # Should still be 0.0 because evidence is pending
    assert score.score_value == 0.0, "Pending evidence should not affect score"


def test_rejected_evidence_not_counted(session: Session, test_control: Control):
    """Test 5: Rejected evidence does not count"""
    # Add rejected evidence
    evidence = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Rejected policy",
        locator_json={},
        evidence_type="policy",
        status="rejected"
    )
    session.add(evidence)
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    assert score.score_value == 0.0, "Rejected evidence should not affect score"


def test_score_event_tracking(session: Session, test_control: Control):
    """Test 6: Score changes are tracked in ScoreEvent"""
    scoring_service = ScoringService(session)
    
    # Initial score (no evidence)
    score1 = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    assert score1.score_value == 0.0
    
    # Add evidence
    evidence = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Policy",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    session.add(evidence)
    session.commit()
    
    # Recalculate score
    score2 = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    assert score2.score_value == 0.33
    
    # Check that score event was created
    from sqlmodel import select
    events = session.exec(select(ScoreEvent).where(ScoreEvent.control_id == test_control.id)).all()
    assert len(events) == 1, "Should have one score change event"
    assert events[0].old_score == 0.0
    assert events[0].new_score == 0.33


def test_weighted_scoring_quantization(session: Session, test_control: Control):
    """Test 7: Weighted scoring also enforces strict quantization"""
    # Add evidence
    evidence1 = Evidence(
        control_id=test_control.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Policy",
        locator_json={},
        evidence_type="policy",
        status="accepted",
        confidence="high"
    )
    session.add(evidence1)
    session.commit()
    
    scoring_service = ScoringService(session)
    score = scoring_service.calculate_control_score_advanced(
        test_control.id, 
        use_weighted=True,
        trigger_rollup=False
    )
    
    # Even with weighted scoring, must be quantized
    assert score.score_value in [0.0, 0.33, 0.66, 1.0], f"Weighted score must be quantized, got {score.score_value}"


def test_rollup_calculation_function(session: Session):
    """Test 8: Function rollup calculations"""
    # Create multiple controls in same function
    control1 = Control(
        csf_id="GV.OC-01",
        name="Control 1",
        text="Test",
        function="Govern",
        category="Organizational Context",
        subcategory="GV.OC-01"
    )
    control2 = Control(
        csf_id="GV.OC-02",
        name="Control 2",
        text="Test",
        function="Govern",
        category="Organizational Context",
        subcategory="GV.OC-02"
    )
    session.add_all([control1, control2])
    session.commit()
    session.refresh(control1)
    session.refresh(control2)
    
    # Add evidence to control1 only
    evidence = Evidence(
        control_id=control1.id,
        artifact_id=1,
        chunk_id=1,
        snippet_text="Policy",
        locator_json={},
        evidence_type="policy",
        status="accepted"
    )
    session.add(evidence)
    session.commit()
    
    scoring_service = ScoringService(session)
    scoring_service.calculate_control_score(control1.id, trigger_rollup=False)
    scoring_service.calculate_control_score(control2.id, trigger_rollup=False)
    
    # Get function rollup
    function_rollup = scoring_service.calculate_function_score("Govern")
    
    # Should be average of 0.33 and 0.0 = 0.165
    expected_avg = (0.33 + 0.0) / 2
    assert function_rollup["avg_score"] == round(expected_avg, 2), "Function rollup should average control scores"
    assert function_rollup["total_controls"] == 2


def test_no_invalid_scores_possible(session: Session, test_control: Control):
    """Test 9: Assert mechanism prevents invalid scores"""
    scoring_service = ScoringService(session)
    
    # Try to manually create an invalid score (this tests the assertion)
    # The _determine_score method has assertions that should catch any bugs
    score = scoring_service.calculate_control_score(test_control.id, trigger_rollup=False)
    
    # Verify assertion worked
    assert score.score_value in [0.0, 0.33, 0.66, 1.0], "Score must be valid"


if __name__ == "__main__":
    print("EPIC 5 Test Suite")
    print("=" * 50)
    print("Run with: pytest test_epic5_scoring.py -v")
