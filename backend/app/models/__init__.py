from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, JSON, Column
from sqlalchemy import Text


class Artifact(SQLModel, table=True):
    """Ingested documents and URLs."""
    __tablename__ = "artifacts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    type: str = Field(index=True)  # docx, pdf, txt, md, xlsx, url
    source_path: Optional[str] = None
    source_url: Optional[str] = None
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    hash: Optional[str] = Field(index=True)
    tags: Optional[str] = None  # JSON array as string
    file_size: Optional[int] = None
    metadata_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class ArtifactChunk(SQLModel, table=True):
    """Text chunks extracted from artifacts with location information."""
    __tablename__ = "artifact_chunks"

    id: Optional[int] = Field(default=None, primary_key=True)
    artifact_id: int = Field(foreign_key="artifacts.id", index=True)
    chunk_text: str = Field(sa_column=Column(Text))
    locator_json: dict = Field(sa_column=Column(JSON))  # {"page": 1, "heading": "...", "para_idx": 3}
    chunk_index: int = Field(default=0)  # Sequence within artifact
    embedding: Optional[str] = None  # For future LLM features


class Control(SQLModel, table=True):
    """NIST CSF control definitions."""
    __tablename__ = "controls"

    id: Optional[int] = Field(default=None, primary_key=True)
    csf_id: str = Field(index=True, unique=True)  # e.g., "ID.AM-1"
    function: str = Field(index=True)  # Identify, Protect, Detect, Respond, Recover
    category: str = Field(index=True)  # e.g., "ID.AM"
    subcategory: str  # Full CSF ID
    name: str
    text: str = Field(sa_column=Column(Text))  # Authoritative CSF language
    intent: Optional[str] = Field(default=None, sa_column=Column(Text))  # What the control ensures
    scoring_rules: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # Deterministic scoring rules
    rubric_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    keywords: Optional[str] = None  # Comma-separated for matching


class Evidence(SQLModel, table=True):
    """Validated evidence snippets linked to controls."""
    __tablename__ = "evidence"

    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="controls.id", index=True)  # Primary control link
    artifact_id: int = Field(foreign_key="artifacts.id", index=True)
    chunk_id: int = Field(foreign_key="artifact_chunks.id", index=True)
    snippet_text: str = Field(sa_column=Column(Text))
    locator_json: dict = Field(sa_column=Column(JSON))
    status: str = Field(default="pending")  # pending, accepted, rejected, superseded
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))  # Human rationale
    confidence: Optional[str] = Field(default=None)  # low, medium, high
    evidence_type: Optional[str] = None  # policy, procedure, technical, operational, assessment
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EvidenceControlLink(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between Evidence and Controls.
    Allows a single piece of evidence to support multiple controls.
    """
    __tablename__ = "evidence_control_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    evidence_id: int = Field(foreign_key="evidence.id", index=True)
    control_id: int = Field(foreign_key="controls.id", index=True)
    relevance_notes: Optional[str] = Field(default=None, sa_column=Column(Text))  # Why this evidence applies to this control
    linked_at: datetime = Field(default_factory=datetime.utcnow)
    linked_by: Optional[str] = None


class Score(SQLModel, table=True):
    """Control scores with calculation method."""
    __tablename__ = "scores"

    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="controls.id", index=True, unique=True)
    score_value: float = Field(default=0.0)  # ONLY: 0.0, 0.33, 0.66, 1.0
    score_label: str = Field(default="none")  # none, partial, mostly, full
    score_rationale: Optional[str] = Field(default=None, sa_column=Column(Text))  # Why this score
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    method: str = Field(default="auto")  # auto, manual, override
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))


class Gap(SQLModel, table=True):
    """Identified gaps in control implementation."""
    __tablename__ = "gaps"

    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="controls.id", index=True)
    gap_type: str = Field(index=True)  # missing_control, missing_policy, missing_procedure, missing_technical_enforcement, missing_operational_evidence, incomplete_implementation
    description: str = Field(sa_column=Column(Text))
    severity: str = Field(default="medium")  # low, medium, high, critical
    status: str = Field(default="open", index=True)  # open, in_progress, resolved, accepted
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class Action(SQLModel, table=True):
    """Remediation action items generated from gaps."""
    __tablename__ = "actions"

    id: Optional[int] = Field(default=None, primary_key=True)
    gap_id: Optional[int] = Field(foreign_key="gaps.id", index=True)  # Linked gap
    control_id: Optional[int] = Field(foreign_key="controls.id", index=True)
    title: str
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    status: str = Field(default="open", index=True)  # open, in_progress, blocked, complete
    acceptance_criteria: Optional[str] = Field(default=None, sa_column=Column(Text))  # What evidence will close this gap
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Risk(SQLModel, table=True):
    """Risk register entries for controls with identified gaps or low scores."""
    __tablename__ = "risks"

    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="controls.id", index=True)
    gap_id: Optional[int] = Field(foreign_key="gaps.id", index=True)  # Optional link to specific gap
    risk_title: str
    risk_statement: str = Field(sa_column=Column(Text))
    
    # Risk scoring
    likelihood: str = Field(default="medium", index=True)  # low, medium, high, very_high
    impact: str = Field(default="medium", index=True)  # low, medium, high, critical
    inherent_risk_score: int = Field(default=9)  # Calculated: likelihood × impact (1-25)
    residual_risk_score: Optional[int] = None  # After mitigation
    
    # Risk treatment decision
    treatment: str = Field(default="mitigate", index=True)  # accept, mitigate, transfer, avoid
    treatment_rationale: Optional[str] = Field(default=None, sa_column=Column(Text))
    
    # Acceptance details (if treatment = accept)
    compensating_controls: Optional[str] = Field(default=None, sa_column=Column(Text))
    acceptance_approver: Optional[str] = None
    acceptance_approved_at: Optional[datetime] = None
    acceptance_expiry_date: Optional[datetime] = None
    
    # Mitigation details (if treatment = mitigate)
    mitigation_plan: Optional[str] = Field(default=None, sa_column=Column(Text))
    mitigation_owner: Optional[str] = None
    mitigation_target_date: Optional[datetime] = None
    
    # Status tracking
    status: str = Field(default="open", index=True)  # open, under_review, accepted, mitigated, transferred, closed
    review_frequency: str = Field(default="quarterly")  # monthly, quarterly, annually
    last_reviewed_at: Optional[datetime] = None
    next_review_date: Optional[datetime] = None
    
    # Category for grouping
    risk_category: Optional[str] = Field(default=None, index=True)  # operational, technical, compliance, strategic
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class ScoreEvent(SQLModel, table=True):
    """Audit trail for score changes."""
    __tablename__ = "score_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    control_id: int = Field(foreign_key="controls.id", index=True)
    old_score: float
    new_score: float
    old_label: str
    new_label: str
    user: Optional[str] = None
    reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ScoreSnapshot(SQLModel, table=True):
    '''Periodic snapshots of aggregate scores for trend analysis.'''
    __tablename__ = 'score_snapshots'

    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    overall_percentage: float = Field(default=0.0)
    total_controls: int = Field(default=0)
    scored_controls: int = Field(default=0)
    function_scores: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # {function: percentage}
    category_scores: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # {category: percentage}
    score_distribution: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # {full, mostly, partial, none counts}
