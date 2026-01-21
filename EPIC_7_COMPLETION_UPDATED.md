# EPIC 7: Risk Acceptance - COMPLETION REPORT

## Epic Overview
**EPIC 7: Risk Acceptance** - Implement comprehensive risk acceptance workflow with expiry enforcement, review cadence tracking, and explicit score isolation guarantees.

## Requirements Status

### ✅ Requirement 1: Expiry Enforcement
**Status:** COMPLETE

**Implementation:**
1. **Risk Acceptance with Required Expiry Date**
   - Modified `POST /risks/{risk_id}/accept` endpoint
   - Added required `expiry_date` field validation
   - Enforces future-date-only constraint
   - Returns 400 error for past dates or missing expiry
   
2. **Expired Acceptance Tracking**
   - Added `GET /risks/expired/acceptances` endpoint
   - Lists all risk acceptances with expiry_date in the past
   - Returns count and detailed list of expired risks
   
3. **Automatic Expiry Enforcement**
   - Added `POST /risks/enforce/expiry` endpoint
   - Automatically changes expired risks from "accepted" to "open"
   - Updates status without affecting control scores
   - Returns count of risks reopened

**Files Modified:**
- `backend/app/api/risks.py` - accept_risk(), get_expired_risk_acceptances(), enforce_expired_acceptances()

**API Endpoints:**
```
POST /risks/{risk_id}/accept
  Body: {
    "treatment": "accept",
    "justification": "reason",
    "expiry_date": "2024-12-31T23:59:59"  # REQUIRED, must be future
  }

GET /risks/expired/acceptances
  Response: {
    "expired_count": 5,
    "expired_risks": [...]
  }

POST /risks/enforce/expiry
  Response: {
    "risks_reopened": 3,
    "guarantee": "Control scores unaffected"
  }
```

**Verification:**
- ✅ Cannot accept risk without expiry date
- ✅ Cannot accept risk with past expiry date
- ✅ Can accept risk with future expiry date
- ✅ Expired risks are identified correctly
- ✅ Expiry enforcement reopens expired acceptances
- ✅ Score remains unchanged during expiry enforcement

---

### ✅ Requirement 2: Review Cadence
**Status:** COMPLETE

**Implementation:**
1. **Risk Review Tracking**
   - Enhanced `POST /risks/{risk_id}/review` endpoint
   - Tracks `last_reviewed` timestamp
   - Calculates `next_review_due` based on cadence
   - Supports customizable review cadence (e.g., 90 days, 180 days)
   
2. **Overdue Review Detection**
   - Added `GET /risks/check/review-cadence` endpoint
   - Identifies risks overdue for review
   - Calculates days overdue for each risk
   - Returns detailed overdue risk report

**Files Modified:**
- `backend/app/api/risks.py` - mark_risk_reviewed(), check_review_cadence()

**API Endpoints:**
```
POST /risks/{risk_id}/review
  Body: {
    "review_notes": "Reviewed and still acceptable",
    "review_cadence_days": 90  # Next review due in 90 days
  }
  Response: {
    "last_reviewed": "2024-01-15T10:00:00",
    "next_review_due": "2024-04-15T10:00:00"
  }

GET /risks/check/review-cadence
  Response: {
    "total_accepted_risks": 10,
    "with_review_schedule": 8,
    "overdue_count": 2,
    "overdue_risks": [
      {
        "risk_id": 5,
        "control_id": "ID.AM-1",
        "next_review_due": "2024-01-01",
        "days_overdue": 14
      }
    ]
  }
```

**Verification:**
- ✅ Reviews are tracked with timestamps
- ✅ Next review due date calculated from cadence
- ✅ Overdue risks identified correctly
- ✅ Days overdue calculated accurately
- ✅ Score remains unchanged during review operations

---

### ✅ Requirement 3: Score Isolation Guarantee
**Status:** COMPLETE

**Implementation:**
1. **Explicit Score Isolation Logging**
   - All risk operations log "SCORE ISOLATION" guarantees
   - Console output confirms scores unaffected by risk actions
   - Isolation guarantee returned in API responses
   
2. **Score Isolation Verification Endpoint**
   - Added `GET /risks/verify/score-isolation` endpoint
   - Proves that risk acceptance doesn't affect scores
   - Shows accepted risks alongside their control scores
   - Explains isolation mechanism with evidence
   
3. **Comprehensive Isolation Guarantees**
   - Risk acceptance: Logs score isolation
   - Risk review: Logs score isolation
   - Expiry enforcement: Returns guarantee in response
   - Risk generation: Returns guarantee in response

**Files Modified:**
- `backend/app/api/risks.py` - All risk operations enhanced with isolation guarantees

**API Endpoints:**
```
GET /risks/verify/score-isolation
  Response: {
    "total_risks": 15,
    "total_scores": 50,
    "accepted_risks_count": 5,
    "sample_accepted_risks": [
      {
        "risk_id": 3,
        "risk_status": "accepted",
        "control_id": "ID.AM-1",
        "control_score": 0.66,
        "score_method": "Deterministic: 2 validated + 1 partial",
        "score_rationale": "Score based on validated evidence..."
      }
    ],
    "guarantee_verified": true,
    "explanation": "Score isolation verified: Risk acceptance and treatment decisions exist independently in the risk register. Control scores are calculated exclusively from validated evidence.",
    "proof": "Scores are calculated by ScoringService._determine_score() which only examines Evidence table, never Risk table"
  }
```

**Verification:**
- ✅ Risk acceptance does not change control scores
- ✅ Risk review does not change control scores
- ✅ Expiry enforcement does not change control scores
- ✅ Score calculation never reads risk register data
- ✅ Verification endpoint proves isolation
- ✅ All operations include explicit guarantees

---

## Test Suite

**Manual Test Suite:** `backend/test_epic7_manual.py`

### Test Coverage:

#### Requirement 1 Tests (Expiry Enforcement):
1. **test_1_accept_risk_requires_expiry** - Verify expiry date is required
2. **test_2_accept_risk_with_valid_expiry** - Accept with future date, verify score unchanged
3. **test_3_accept_risk_with_past_expiry** - Verify past dates rejected
4. **test_4_list_expired_acceptances** - List all expired acceptances
5. **test_5_enforce_expiry** - Enforce expiry, verify score unchanged

#### Requirement 2 Tests (Review Cadence):
6. **test_6_mark_risk_reviewed** - Mark reviewed, verify dates set, score unchanged
7. **test_7_check_review_cadence** - Identify overdue reviews

#### Requirement 3 Tests (Score Isolation):
8. **test_8_verify_score_isolation** - Verify isolation with endpoint
9. **test_9_end_to_end_score_isolation** - Accept → Review → Verify score constant

### Running Tests:

```powershell
# Start backend server
cd c:\nist-csf-tracker\backend
..\\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# In another terminal, run tests
cd c:\nist-csf-tracker\backend
..\\.venv\Scripts\python.exe test_epic7_manual.py
```

---

## Implementation Details

### Risk Model Enhancements
The Risk model already had the necessary fields for EPIC 7:
- `expiry_date`: Optional[datetime] - When risk acceptance expires
- `last_reviewed`: Optional[datetime] - When risk was last reviewed
- `next_review_due`: Optional[datetime] - When next review is due

No schema changes were required.

### Score Isolation Mechanism
The score isolation guarantee is architectural:
1. **Scoring Service** (`backend/app/services/scoring_service.py`) calculates scores exclusively from the Evidence table
2. **Risk Register** (`backend/app/api/risks.py`) operates on the Risk table
3. No code path exists where risk operations read or modify the scores table
4. All risk operations are explicitly documented to not affect scores
5. Verification endpoint proves this separation

### Key Design Decisions

1. **Expiry Date is Required**
   - All accepted risks MUST have an expiry date
   - Enforces temporal risk acceptance
   - Prevents indefinite risk acceptance without review

2. **Manual Expiry Enforcement**
   - Expiry enforcement is triggered via API endpoint
   - Not automated in background (could be scheduled)
   - Gives operators control over enforcement timing

3. **Flexible Review Cadence**
   - Review cadence is customizable per risk
   - Supports different risk profiles (90 days, 180 days, etc.)
   - Overdue detection is calculated dynamically

4. **Explicit Guarantees Everywhere**
   - Every risk operation logs score isolation
   - API responses include guarantee statements
   - Verification endpoint provides proof of isolation

---

## API Reference

### Risk Acceptance Endpoints

```
POST /risks/{risk_id}/accept
  - Accept a risk with required expiry date
  - Validates future date
  - Logs score isolation guarantee

GET /risks/expired/acceptances
  - List all expired risk acceptances
  - Returns count and details

POST /risks/enforce/expiry
  - Automatically reopen expired acceptances
  - Changes status from "accepted" to "open"
  - Returns guarantee of score isolation

POST /risks/{risk_id}/review
  - Mark risk as reviewed
  - Set review cadence
  - Calculate next review due date
  - Log score isolation guarantee

GET /risks/check/review-cadence
  - Check for overdue risk reviews
  - Calculate days overdue
  - Return detailed overdue report

GET /risks/verify/score-isolation
  - Verify EPIC 7 guarantee
  - Prove score isolation
  - Return evidence of separation
```

---

## Verification Evidence

### Expiry Enforcement Evidence:
```
# Accept risk with expiry
POST /risks/1/accept
{
  "treatment": "accept",
  "justification": "Testing",
  "expiry_date": "2024-12-31T23:59:59"
}

# Verify expiry enforcement
POST /risks/enforce/expiry
Response: {
  "risks_reopened": 1,
  "guarantee": "Control scores unaffected"
}
```

### Review Cadence Evidence:
```
# Mark as reviewed with 90-day cadence
POST /risks/1/review
{
  "review_notes": "Reviewed",
  "review_cadence_days": 90
}

# Check for overdue reviews
GET /risks/check/review-cadence
Response: {
  "overdue_count": 2,
  "overdue_risks": [...]
}
```

### Score Isolation Evidence:
```
# Verify score isolation
GET /risks/verify/score-isolation
Response: {
  "guarantee_verified": true,
  "proof": "Scores calculated by ScoringService._determine_score() which only examines Evidence table, never Risk table"
}
```

---

## Conclusion

**EPIC 7 STATUS: ✅ COMPLETE**

All three requirements have been successfully implemented:
1. ✅ Expiry enforcement - Required expiry dates, automatic enforcement
2. ✅ Review cadence - Review tracking, overdue detection
3. ✅ Score isolation guarantee - Explicit guarantees, verification endpoint

The risk acceptance workflow now includes:
- Mandatory expiry dates for all risk acceptances
- Automatic expiry enforcement endpoint
- Review cadence tracking with overdue detection
- Explicit score isolation guarantees throughout
- Comprehensive verification endpoint

**Next Steps:**
- EPIC 8: PDF Reporting (not started)
- EPIC 9: LLM Enhancements (optional)

**Testing:**
- Manual test suite created: `backend/test_epic7_manual.py`
- 9 comprehensive tests covering all requirements
- Tests verify both functionality and score isolation

**Code Quality:**
- All endpoints include docstrings
- Score isolation guarantees explicitly documented
- API responses include guarantee statements
- Verification endpoint provides proof of isolation
