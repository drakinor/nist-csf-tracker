# EPIC 6: Gap Analysis & Actions - COMPLETE ✅

**Status**: Fully Implemented  
**Date Completed**: January 20, 2026

---

## Overview

EPIC 6 provides deterministic gap analysis with acceptance-criteria-driven closure logic. Gaps are automatically identified based on evidence validation, classified with clear rules, and can only be resolved when specific acceptance criteria are met. This ensures that gap remediation is tracked properly and gaps don't close prematurely.

---

## Requirements Delivered

### 1. ✅ Deterministic Gap Classification

**What it does**: Every gap type has explicit, repeatable classification rules

**Gap Types & Classification Rules**:

| Gap Type | Classification Rule | Severity Logic |
|----------|-------------------|----------------|
| `missing_control` | Score = 0.0 (no evidence) | Always `critical` |
| `missing_policy` | No "policy" evidence type | `high` |
| `missing_procedure` | No "procedure" evidence type | `critical` if policy exists, else `high` |
| `missing_technical_enforcement` | No "technical" OR "operational" evidence | `high` if policy+procedure exist, else `medium` |
| `missing_operational_evidence` | No "operational" evidence | `medium` |
| `incomplete_implementation` | Score < 1.0 with some evidence | `high` if score < 0.66, else `medium` |

**Deterministic Properties**:
- Same evidence → same gaps (reproducible)
- Severity escalates based on context (e.g., procedure without policy is more critical)
- Gaps include "DETERMINISTIC:" prefix in description
- No human interpretation needed

**Code Location**: [scoring_service.py](backend/app/services/scoring_service.py#L375-L467)

```python
# Example: Missing policy classification
if "policy" not in evidence_types:
    expected_gaps.append({
        "gap_type": "missing_policy",
        "description": "DETERMINISTIC: No policy documentation validated",
        "severity": "high",
        "acceptance_criteria": "Validate evidence of type 'policy'"
    })
```

---

### 2. ✅ Acceptance-Criteria-Driven Closure Logic

**What it does**: Gaps can only be resolved when specific acceptance criteria are met

**Automatic Gap Resolution**:
Gaps are automatically resolved when:
1. Evidence of required type is validated
2. Control score improves to meet threshold
3. All linked actions are completed

**Manual Gap Resolution with Validation**:
The `/api/gaps/{gap_id}/resolve` endpoint checks:
- `missing_control` → At least 1 evidence exists
- `missing_policy` → Policy evidence validated
- `missing_procedure` → Procedure evidence validated
- `missing_technical_enforcement` → Technical OR operational evidence validated
- `incomplete_implementation` → Control score ≥ 1.0

**Code Location**: [gaps.py](backend/app/api/gaps.py#L137-L200)

**Example Flow**:
```
1. Gap created: "missing_policy" (severity: high)
2. User uploads policy document
3. User validates evidence as type "policy"
4. Scoring system recalculates score
5. Gap automatically resolved (criteria met)
```

---

### 3. ✅ Action Item Tracking with Acceptance Criteria

**What it does**: Actions can define acceptance criteria that must be met before closure

**Features**:
- Each action can have `acceptance_criteria` field
- `/api/actions/{action_id}/check-criteria` endpoint validates criteria
- Actions linked to gaps auto-resolve gap when all actions complete
- Completion requires meeting criteria

**Code Location**: [actions.py](backend/app/api/actions.py#L82-L126)

**Example**:
```json
{
  "title": "Document password policy",
  "gap_id": 5,
  "acceptance_criteria": "Validate evidence of type 'policy' for AC.1",
  "owner": "Security Team",
  "due_date": "2026-02-01"
}
```

When action is marked complete:
1. System checks if acceptance criteria met
2. If gap linked, checks if all gap actions complete
3. Auto-resolves gap if criteria satisfied

---

## Deterministic Gap Classification Rules

### Rule 1: Missing Control (Score = 0.0)
```
Trigger: No validated evidence
Severity: Critical
Acceptance Criteria: Validate ANY evidence
Auto-Resolves: When first evidence is accepted
```

### Rule 2: Missing Policy
```
Trigger: No evidence with type="policy"
Severity: High
Acceptance Criteria: Validate policy evidence
Auto-Resolves: When policy evidence accepted
```

### Rule 3: Missing Procedure
```
Trigger: No evidence with type="procedure"
Severity: Critical (if policy exists), High (otherwise)
Acceptance Criteria: Validate procedure evidence
Auto-Resolves: When procedure evidence accepted
```

### Rule 4: Missing Technical Enforcement
```
Trigger: No evidence with type="technical" OR type="operational"
Severity: High (if policy+procedure exist), Medium (otherwise)
Acceptance Criteria: Validate technical OR operational evidence
Auto-Resolves: When enforcement evidence accepted
```

### Rule 5: Incomplete Implementation
```
Trigger: Score < 1.0 AND some evidence exists
Severity: High (score < 0.66), Medium (score ≥ 0.66)
Acceptance Criteria: Achieve score = 1.0
Auto-Resolves: When all required evidence validated
```

---

## Acceptance-Criteria-Driven Closure

### Automatic Closure Triggers

**Evidence-Based**:
- Gap resolution happens automatically in `_generate_gaps()` method
- When scoring system runs, it checks what gaps should exist
- Gaps that no longer apply are auto-resolved
- Timestamp `resolved_at` set automatically

**Action-Based**:
- When action marked complete, checks if linked gap can close
- If all actions for a gap are complete, gap auto-resolves
- Ensures coordinated closure across multiple actions

### Manual Closure Validation

**API Endpoint**: `PATCH /api/gaps/{gap_id}/resolve`

**Validation Logic**:
```python
if gap.gap_type == "missing_policy":
    policy_evidence = [e for e in evidence if e.evidence_type == "policy"]
    criteria_met = len(policy_evidence) > 0
    
if not criteria_met:
    raise HTTPException(400, "Acceptance criteria not met")
```

**Returns**:
- Success: `{"message": "Gap resolved", "reason": "..."`
- Failure: `HTTP 400` with reason criteria not met

---

## API Endpoints

### Gaps

**List Gaps**:
```
GET /api/gaps/
  ?status=open|in_progress|resolved|accepted
  &severity=low|medium|high|critical
  &gap_type=missing_policy|...
  &control_id=1
```

**Get Gap Summary**:
```
GET /api/gaps/summary
Returns: {
  "total_gaps": 23,
  "open_gaps": 15,
  "by_severity": {"critical": 3, "high": 8, ...},
  "by_type": {"missing_policy": 5, ...}
}
```

**Resolve Gap (with criteria check)**:
```
PATCH /api/gaps/{gap_id}/resolve
Returns: {
  "message": "Gap resolved",
  "gap": {...},
  "reason": "Policy evidence validated (2 found)"
}
```

**Regenerate All Gaps**:
```
POST /api/gaps/regenerate
Returns: {
  "message": "Gaps regenerated",
  "controls_scored": 23,
  "open_gaps": 15
}
```

### Actions

**List Actions**:
```
GET /api/actions/
  ?status=open|in_progress|blocked|complete
```

**Create Action**:
```
POST /api/actions/
Body: {
  "gap_id": 5,
  "control_id": 1,
  "title": "Document password policy",
  "description": "...",
  "owner": "Security Team",
  "due_date": "2026-02-01",
  "acceptance_criteria": "Validate policy evidence for AC.1"
}
```

**Check Acceptance Criteria**:
```
POST /api/actions/{action_id}/check-criteria
Returns: {
  "has_criteria": true,
  "acceptance_criteria": "...",
  "gap_resolved": false,
  "evidence_exists": true,
  "can_close": true,
  "recommendation": "✅ Ready to close"
}
```

**Update Action (with auto-gap-resolution)**:
```
PATCH /api/actions/{action_id}
Body: {"status": "complete"}

# If linked to gap, checks if all gap actions complete
# Auto-resolves gap if yes
```

**Kanban Board**:
```
GET /api/actions/kanban/board
Returns: {
  "open": [...],
  "in_progress": [...],
  "blocked": [...],
  "complete": [...]
}
```

---

## Testing

### Manual Test Suite

**Location**: `backend/test_epic6_manual.py`

**Run with**:
```bash
# Start backend first
.\scripts\dev.ps1

# In another terminal
python backend/test_epic6_manual.py
```

**Tests**:
1. Deterministic gap classification
2. Severity assignment rules
3. Acceptance criteria checking
4. Gap resolution validation
5. Automatic gap resolution
6. Descriptive gap messages

---

## Usage Examples

### Example 1: Automatic Gap Generation

```python
from app.services.scoring_service import ScoringService

scoring_service = ScoringService(session)

# When evidence is validated, score recalculates
# Gaps are automatically generated/resolved
score = scoring_service.calculate_control_score(control_id=1)

# Gaps now reflect current evidence state
```

### Example 2: Create Action with Acceptance Criteria

```python
POST /api/actions/
{
  "gap_id": 5,
  "title": "Document password policy",
  "acceptance_criteria": "Validate evidence: password policy document (type=policy) for control AC.1",
  "owner": "Security Team",
  "due_date": "2026-02-01"
}
```

### Example 3: Complete Action (Auto-Resolves Gap)

```python
# Mark action complete
PATCH /api/actions/123
{"status": "complete"}

# System checks:
# 1. Are acceptance criteria met?
# 2. Are all actions for linked gap complete?
# 3. If yes, auto-resolve gap
```

### Example 4: Try to Resolve Gap (Criteria Not Met)

```python
PATCH /api/gaps/5/resolve

# Response: HTTP 400
{
  "detail": "Acceptance criteria not met. Policy evidence validated (0 found). Please validate required evidence first."
}
```

---

## Database Schema

### Gap Model
```python
class Gap(SQLModel, table=True):
    id: int
    control_id: int
    gap_type: str  # DETERMINISTIC types
    description: str  # Includes "DETERMINISTIC:" prefix
    severity: str  # Calculated by rules
    status: str  # open, in_progress, resolved, accepted
    created_at: datetime
    resolved_at: Optional[datetime]  # Set when auto-resolved
```

### Action Model
```python
class Action(SQLModel, table=True):
    id: int
    gap_id: Optional[int]
    control_id: Optional[int]
    title: str
    description: Optional[str]
    owner: Optional[str]
    due_date: Optional[datetime]
    status: str  # open, in_progress, blocked, complete
    acceptance_criteria: Optional[str]  # What must be done
    created_at: datetime
    completed_at: Optional[datetime]
```

---

## Key Design Decisions

### Why Deterministic Classification?

1. **Reproducibility**: Same evidence → same gaps always
2. **Auditability**: Clear rules = defensible decisions
3. **Automation**: No human judgment needed for gap detection
4. **Consistency**: Everyone sees same gaps for same state

### Why Acceptance-Criteria-Driven Closure?

1. **Prevents Premature Closure**: Can't close until work done
2. **Traceability**: Clear link between action and gap resolution
3. **Validation**: System enforces criteria checking
4. **Accountability**: Criteria must be explicitly met

### Why Automatic Gap Resolution?

1. **Efficiency**: Reduces manual work
2. **Accuracy**: System knows when criteria met
3. **Timeliness**: Gaps close immediately when evidence validated
4. **Consistency**: No forgotten or stale gaps

---

## Success Criteria

✅ Gap classification is deterministic and repeatable  
✅ All gap types have explicit classification rules  
✅ Severity assignment follows clear logic  
✅ Gaps include acceptance criteria  
✅ Manual resolution validates criteria are met  
✅ Automatic resolution when evidence validated  
✅ Actions can define acceptance criteria  
✅ Action completion checks criteria  
✅ Gap auto-resolves when all actions complete  
✅ API endpoints enforce validation  

---

## EPIC 6 COMPLETE ✅

All requirements delivered and tested. Gap analysis is now deterministic with acceptance-criteria-driven closure, ensuring that gaps are properly tracked and only closed when remediation work is complete.

**Next Epic**: EPIC 7 (Risk Acceptance) - Risk register with expiry enforcement and review cadence.
