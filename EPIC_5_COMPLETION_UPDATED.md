# EPIC 5: Advanced Scoring & Rollups - COMPLETE ✅

**Status**: Fully Implemented  
**Date Completed**: January 20, 2026

---

## Overview

EPIC 5 provides strict, deterministic scoring with comprehensive audit trails. All scores are exactly 0.0, 0.33, 0.66, or 1.0, with clear verbalizable rationales explaining how each score was calculated. Evidence-type composition rules ensure defensible scoring, and rollup recalculations are guaranteed.

---

## Requirements Delivered

### 1. ✅ Strict Score Enforcement (0.0 / 0.33 / 0.66 / 1.0)

**What it does**: Enforces that ALL scores are exactly one of four values

**Implementation**:
- Assertion checks in `calculate_control_score()` and `calculate_control_score_advanced()`
- No fractional scores between levels
- Weighted scoring mode also quantizes to exact values
- Invalid scores cannot be created

**Code Location**: `backend/app/services/scoring_service.py`
- Line 126: `assert new_score_value in [0.0, 0.33, 0.66, 1.0]`
- Line 290: Quantization in weighted scoring

**Score Mapping**:
- `0.0` = not-implemented (no evidence)
- `0.33` = partially-implemented (some evidence, missing key components)
- `0.66` = largely-implemented (policy + procedure, missing enforcement)
- `1.0` = fully-implemented (policy + procedure + technical/operational)

---

### 2. ✅ Evidence-Type Composition Rules

**What it does**: Clear rules for which evidence combinations produce which scores

**Composition Rules**:
```
NONE (0.0):
- No validated evidence

PARTIAL (0.33):
- Policy only
- Procedure only
- Technical only
- Operational only
- Any single evidence type without complete coverage

MOSTLY (0.66):
- Policy + Procedure
- Missing technical OR operational enforcement

FULL (1.0):
- Policy + Procedure + (Technical OR Operational)
- Complete evidence coverage
```

**Evidence Type Weights** (for weighted scoring):
- Policy: 25%
- Procedure: 25%
- Technical: 30%
- Operational: 20%
- Assessment: 15%

**Code Location**: `backend/app/services/scoring_service.py`
- Lines 119-214: `_determine_score()` method
- Lines 216-276: `_calculate_weighted_score()` method

---

### 3. ✅ Verbalizable Rationale Generation

**What it does**: Every score includes a human-readable explanation with evidence counts

**Rationale Format**:
```
LEVEL: [counts of evidence types] evidence [, missing components]
```

**Examples**:
- `"NONE: No validated evidence provided"`
- `"PARTIAL: 1 policy evidence, missing procedure, enforcement"`
- `"MOSTLY: 2 policy + 1 procedure evidence, missing enforcement"`
- `"FULL: 1 policy + 1 procedure + 1 technical evidence validated"`

**Features**:
- Includes exact counts of each evidence type
- States what's present AND what's missing
- Score level keyword (NONE/PARTIAL/MOSTLY/FULL) at start
- Verbalizable = can be read aloud and understood immediately

**Code Location**: `backend/app/services/scoring_service.py`
- Lines 146-214: Rationale building in `_determine_score()`
- Lines 267-271: Rationale building in weighted scoring

---

### 4. ✅ Rollup Recalculation Guarantees

**What it does**: Ensures function and category rollups stay synchronized with control scores

**Guarantee Mechanism**:
- Every score calculation can trigger rollup updates via `trigger_rollup` parameter
- `_ensure_rollups_updated()` method called after score changes
- Rollups calculated on-demand from current Score table (always fresh)
- No stale rollup data possible

**Rollup Types**:
1. **Function Rollups**: Average score across all controls in a NIST CSF function (Govern, Identify, Protect, Detect, Respond, Recover)
2. **Category Rollups**: Average score across all controls in a category
3. **Overall Score**: Average score across all controls

**Code Location**: `backend/app/services/scoring_service.py`
- Lines 132-133: Trigger rollup recalculation
- Lines 476-495: `_ensure_rollups_updated()` method
- Lines 497-547: `calculate_function_score()` and `calculate_category_score()` methods

**API Endpoints**:
- `GET /api/scores/function-rollups` - Get all function rollups
- `GET /api/scores/category-rollups` - Get all category rollups
- `GET /api/scores/overall` - Get overall compliance score

---

## Additional Features

### Score Change Tracking

Every score change is logged in `ScoreEvent` table with:
- Old score value and label
- New score value and label
- Reason for change
- Timestamp
- User (for manual overrides)

### Manual Override Support

Authorized users can override automated scores with:
- Full audit trail
- Required justification notes
- Same strict value enforcement (0.0, 0.33, 0.66, 1.0)
- Visual indicator in UI (`method="manual"`)

### Weighted Scoring Option

Alternative scoring method using evidence type weights and confidence multipliers:
- Base weights by evidence type
- Confidence multipliers (high: 1.0, medium: 0.85, low: 0.70)
- Still enforces strict quantization to 0.0/0.33/0.66/1.0
- More granular than boolean logic

---

## Testing

### Manual Test Suite

**Location**: `backend/test_epic5_manual.py`

**Run with**:
```bash
# Start backend server first
.\scripts\dev.ps1

# In another terminal, run tests
python backend/test_epic5_manual.py
```

**Tests**:
1. Strict score value enforcement
2. Verbalizable rationale generation
3. Evidence-type composition rules
4. Rollup calculations
5. Only accepted evidence counts

### Unit Test Suite

**Location**: `backend/tests/test_epic5_scoring.py`

**Tests**:
- Score enforcement for all levels (0.0, 0.33, 0.66, 1.0)
- Evidence composition rules
- Pending/rejected evidence exclusion
- Score event tracking
- Weighted scoring quantization
- Function rollup calculations

---

## Database Schema

### Score Table
```python
class Score(SQLModel, table=True):
    id: int
    control_id: int
    score_value: float  # MUST be 0.0, 0.33, 0.66, or 1.0
    score_label: str
    score_rationale: str
    method: str  # "auto" or "manual"
    notes: Optional[str]
    calculated_at: datetime
```

### ScoreEvent Table
```python
class ScoreEvent(SQLModel, table=True):
    id: int
    control_id: int
    old_score: float
    new_score: float
    old_label: str
    new_label: str
    reason: str
    user: Optional[str]
    created_at: datetime
```

---

## Usage Examples

### Calculate Control Score (Standard)
```python
from app.services.scoring_service import ScoringService

scoring_service = ScoringService(session)
score = scoring_service.calculate_control_score(
    control_id=1,
    trigger_rollup=True  # Ensures rollups are updated
)

print(f"Score: {score.score_value}")  # e.g., 0.66
print(f"Label: {score.score_label}")  # e.g., "largely-implemented"
print(f"Rationale: {score.score_rationale}")  # e.g., "MOSTLY: 1 policy + 1 procedure..."
```

### Calculate with Weighted Scoring
```python
score = scoring_service.calculate_control_score_advanced(
    control_id=1,
    use_weighted=True,
    trigger_rollup=True
)
```

### Get Function Rollups
```python
rollups = scoring_service.get_function_rollups()
# [
#   {"function": "Govern", "average_score": 0.45, "total_controls": 5},
#   {"function": "Protect", "average_score": 0.33, "total_controls": 8},
#   ...
# ]
```

### Manual Score Override (API)
```bash
curl -X POST http://localhost:8000/api/scores/1/override \
  -H "Content-Type: application/json" \
  -d '{
    "score_value": 1.0,
    "score_label": "full",
    "notes": "Compensating controls in place",
    "user": "admin"
  }'
```

---

## API Endpoints

### Scores
- `GET /api/scores/` - List all scores
- `POST /api/scores/recalculate-all` - Recalculate all control scores
- `POST /api/scores/{control_id}/override` - Manually override a score
- `GET /api/scores/function-rollups` - Get function-level rollups
- `GET /api/scores/category-rollups` - Get category-level rollups
- `GET /api/scores/overall` - Get overall compliance score
- `GET /api/scores/dashboard` - Get dashboard summary with all metrics

---

## Key Design Decisions

### Why Four Discrete Levels?

1. **Defensibility**: Easy to explain to auditors
2. **NIST Alignment**: Maps to standard implementation tiers
3. **Clear Thresholds**: No ambiguity about what each level means
4. **Progress Tracking**: Clear path from 0.0 → 0.33 → 0.66 → 1.0

### Why Evidence-Type Composition?

1. **Completeness**: Policy alone doesn't prove implementation
2. **Defense-in-Depth**: Requires documentation + enforcement
3. **Audit Trail**: Each evidence type serves a specific purpose
4. **Risk-Based**: Missing technical enforcement is a higher risk than missing operational evidence

### Why Verbalizable Rationales?

1. **Transparency**: Users understand how scores are calculated
2. **Auditability**: Rationales are evidence in themselves
3. **Debugging**: Easy to identify scoring issues
4. **Communication**: Can be shared in reports and presentations

---

## Success Criteria

✅ All scores are exactly 0.0, 0.33, 0.66, or 1.0  
✅ Evidence composition rules are deterministic and documented  
✅ Every score includes a clear, verbalizable rationale  
✅ Rollups recalculate automatically when scores change  
✅ Only accepted evidence affects scores  
✅ Score changes are tracked with full audit trail  
✅ Manual overrides are supported with justification  
✅ Weighted scoring option available  
✅ Function and category rollups are always current  

---

## EPIC 5 COMPLETE ✅

All requirements delivered and tested. The scoring system is now production-ready with strict enforcement, clear composition rules, verbalizable rationales, and guaranteed rollup consistency.

**Next Epic**: EPIC 6 (Gap Analysis) - Now being completed with deterministic gap classification and acceptance-criteria-driven closure logic.
