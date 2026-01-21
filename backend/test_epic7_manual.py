"""
Manual Test Suite for EPIC 7: Risk Acceptance

EPIC 7 Requirements:
1. Expiry enforcement: Risk acceptances must have expiry dates and auto-expire
2. Review cadence: Risk acceptances have review cadence enforcement
3. Score isolation guarantee: Risk acceptance/treatment does not affect control scores

Prerequisites:
- Backend server running on localhost:8000
- Database seeded with controls and some evidence
- At least one gap with critical/high severity

Run each test manually and verify the results.
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def print_test_header(test_name):
    print("\n" + "="*70)
    print(f"TEST: {test_name}")
    print("="*70)

def print_result(response):
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

# ============================================================================
# REQUIREMENT 1: EXPIRY ENFORCEMENT
# ============================================================================

def test_1_accept_risk_requires_expiry():
    """
    Test that accepting a risk requires an expiry date.
    Expected: Should fail without expiry date.
    """
    print_test_header("1a. Accept risk WITHOUT expiry date (should fail)")
    
    # First, generate some risks from gaps
    print("\nGenerating risks from gaps...")
    response = requests.post(f"{BASE_URL}/risks/generate/from-gaps")
    print_result(response)
    
    # Get first available risk
    response = requests.get(f"{BASE_URL}/risks")
    risks = response.json()
    if not risks:
        print("❌ No risks available. Create some gaps first.")
        return
    
    risk_id = risks[0]["id"]
    print(f"\nUsing risk ID: {risk_id}")
    
    # Try to accept without expiry
    print("\nAttempting to accept risk WITHOUT expiry date...")
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/accept",
        json={
            "treatment": "accept",
            "justification": "Testing without expiry"
            # No expiry_date
        }
    )
    print_result(response)
    
    if response.status_code == 422 or "expiry" in response.text.lower():
        print("✅ PASS: Risk acceptance correctly requires expiry date")
    else:
        print("❌ FAIL: Should have required expiry date")


def test_2_accept_risk_with_valid_expiry():
    """
    Test accepting a risk with a valid future expiry date.
    Expected: Should succeed and log score isolation guarantee.
    """
    print_test_header("1b. Accept risk WITH valid future expiry date")
    
    # Get first open risk
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "open"]
    if not risks:
        print("❌ No open risks available")
        return
    
    risk_id = risks[0]["id"]
    control_id = risks[0]["control_id"]
    
    print(f"\nRisk ID: {risk_id}")
    print(f"Control ID: {control_id}")
    
    # Get control score BEFORE acceptance
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    control_before = response.json()
    score_before = control_before.get("current_score")
    print(f"Score BEFORE acceptance: {score_before}")
    
    # Accept with valid expiry (30 days from now)
    expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
    print(f"\nAccepting risk with expiry: {expiry_date}")
    
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/accept",
        json={
            "treatment": "accept",
            "justification": "Testing with valid expiry",
            "expiry_date": expiry_date
        }
    )
    print_result(response)
    
    # Get control score AFTER acceptance
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    control_after = response.json()
    score_after = control_after.get("current_score")
    print(f"\nScore AFTER acceptance: {score_after}")
    
    # Verify score unchanged
    if score_before == score_after:
        print(f"✅ PASS: Score unchanged ({score_before} == {score_after})")
    else:
        print(f"❌ FAIL: Score changed ({score_before} != {score_after})")
    
    if response.status_code == 200:
        print("✅ PASS: Risk accepted successfully")
    else:
        print("❌ FAIL: Risk acceptance failed")


def test_3_accept_risk_with_past_expiry():
    """
    Test that accepting a risk with a past expiry date fails.
    Expected: Should reject past dates.
    """
    print_test_header("1c. Accept risk WITH past expiry date (should fail)")
    
    # Get first open risk
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "open"]
    if not risks:
        print("❌ No open risks available")
        return
    
    risk_id = risks[0]["id"]
    
    # Try to accept with past expiry
    past_date = (datetime.now() - timedelta(days=10)).isoformat()
    print(f"\nAttempting to accept with past expiry: {past_date}")
    
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/accept",
        json={
            "treatment": "accept",
            "justification": "Testing with past expiry",
            "expiry_date": past_date
        }
    )
    print_result(response)
    
    if response.status_code == 400 or "future" in response.text.lower():
        print("✅ PASS: Past expiry date correctly rejected")
    else:
        print("❌ FAIL: Should have rejected past expiry date")


def test_4_list_expired_acceptances():
    """
    Test listing expired risk acceptances.
    Expected: Should return risks with expiry dates in the past.
    """
    print_test_header("1d. List expired risk acceptances")
    
    response = requests.get(f"{BASE_URL}/risks/expired/acceptances")
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nExpired acceptances: {data.get('expired_count', 0)}")
        print("✅ PASS: Expired acceptances endpoint works")
    else:
        print("❌ FAIL: Expired acceptances endpoint failed")


def test_5_enforce_expiry():
    """
    Test automatic enforcement of expired risk acceptances.
    Expected: Should change expired risks from 'accepted' to 'open'.
    """
    print_test_header("1e. Enforce expired risk acceptances")
    
    # First, accept a risk with near-immediate expiry
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "open"]
    if risks:
        risk_id = risks[0]["id"]
        control_id = risks[0]["control_id"]
        
        # Accept with 1-second expiry for testing
        expiry_date = (datetime.now() + timedelta(seconds=1)).isoformat()
        print(f"\nAccepting risk {risk_id} with near-immediate expiry: {expiry_date}")
        
        response = requests.post(
            f"{BASE_URL}/risks/{risk_id}/accept",
            json={
                "treatment": "accept",
                "justification": "Testing immediate expiry",
                "expiry_date": expiry_date
            }
        )
        print_result(response)
        
        # Wait for expiry
        import time
        print("\nWaiting 2 seconds for expiry...")
        time.sleep(2)
        
        # Get control score BEFORE enforcement
        response = requests.get(f"{BASE_URL}/controls/{control_id}")
        score_before = response.json().get("current_score")
        print(f"Score BEFORE enforcement: {score_before}")
        
        # Enforce expiry
        print("\nEnforcing expired acceptances...")
        response = requests.post(f"{BASE_URL}/risks/enforce/expiry")
        print_result(response)
        
        # Get control score AFTER enforcement
        response = requests.get(f"{BASE_URL}/controls/{control_id}")
        score_after = response.json().get("current_score")
        print(f"Score AFTER enforcement: {score_after}")
        
        # Verify score unchanged
        if score_before == score_after:
            print(f"✅ PASS: Score unchanged during expiry enforcement ({score_before} == {score_after})")
        else:
            print(f"❌ FAIL: Score changed during expiry enforcement ({score_before} != {score_after})")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("risks_reopened", 0) > 0:
                print("✅ PASS: Expired acceptances enforced successfully")
            else:
                print("⚠️ WARNING: No risks were reopened (may need adjustment)")
        else:
            print("❌ FAIL: Expiry enforcement failed")


# ============================================================================
# REQUIREMENT 2: REVIEW CADENCE
# ============================================================================

def test_6_mark_risk_reviewed():
    """
    Test marking a risk as reviewed with review cadence.
    Expected: Should set last_reviewed and next_review_due dates.
    """
    print_test_header("2a. Mark risk as reviewed with 90-day cadence")
    
    # Get first accepted risk
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "accepted"]
    if not risks:
        print("❌ No accepted risks available. Accept a risk first.")
        return
    
    risk_id = risks[0]["id"]
    control_id = risks[0]["control_id"]
    
    print(f"\nRisk ID: {risk_id}")
    print(f"Control ID: {control_id}")
    
    # Get control score BEFORE review
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    score_before = response.json().get("current_score")
    print(f"Score BEFORE review: {score_before}")
    
    # Mark as reviewed with 90-day cadence
    print("\nMarking risk as reviewed...")
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/review",
        json={
            "review_notes": "Testing review cadence",
            "review_cadence_days": 90
        }
    )
    print_result(response)
    
    # Get control score AFTER review
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    score_after = response.json().get("current_score")
    print(f"Score AFTER review: {score_after}")
    
    # Verify score unchanged
    if score_before == score_after:
        print(f"✅ PASS: Score unchanged during review ({score_before} == {score_after})")
    else:
        print(f"❌ FAIL: Score changed during review ({score_before} != {score_after})")
    
    if response.status_code == 200:
        data = response.json()
        if "last_reviewed" in data and "next_review_due" in data:
            print("✅ PASS: Review dates set correctly")
        else:
            print("❌ FAIL: Review dates missing")
    else:
        print("❌ FAIL: Review marking failed")


def test_7_check_review_cadence():
    """
    Test checking which risks are overdue for review.
    Expected: Should identify risks with next_review_due in the past.
    """
    print_test_header("2b. Check review cadence for overdue risks")
    
    # First, mark a risk with immediate review due date
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "accepted"]
    if risks:
        risk_id = risks[0]["id"]
        
        # Mark as reviewed with 0-day cadence (immediate review due)
        print(f"\nMarking risk {risk_id} as reviewed with 0-day cadence...")
        response = requests.post(
            f"{BASE_URL}/risks/{risk_id}/review",
            json={
                "review_notes": "Testing immediate review due",
                "review_cadence_days": 0
            }
        )
        print_result(response)
    
    # Check for overdue reviews
    print("\nChecking review cadence...")
    response = requests.get(f"{BASE_URL}/risks/check/review-cadence")
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nTotal accepted risks: {data.get('total_accepted_risks', 0)}")
        print(f"Overdue for review: {data.get('overdue_count', 0)}")
        print("✅ PASS: Review cadence check works")
    else:
        print("❌ FAIL: Review cadence check failed")


# ============================================================================
# REQUIREMENT 3: SCORE ISOLATION GUARANTEE
# ============================================================================

def test_8_verify_score_isolation():
    """
    Test explicit verification that risk operations don't affect scores.
    Expected: Should prove score isolation with detailed analysis.
    """
    print_test_header("3. Verify score isolation guarantee")
    
    response = requests.get(f"{BASE_URL}/risks/verify/score-isolation")
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("guarantee_verified"):
            print("\n✅ PASS: Score isolation guarantee verified")
            print(f"Explanation: {data.get('explanation')}")
            print(f"Proof: {data.get('proof')}")
        else:
            print("❌ FAIL: Score isolation NOT verified")
    else:
        print("❌ FAIL: Score isolation verification endpoint failed")


def test_9_end_to_end_score_isolation():
    """
    End-to-end test: Accept risk, review it, enforce expiry - verify score never changes.
    Expected: Control score remains identical throughout entire risk lifecycle.
    """
    print_test_header("3. End-to-end score isolation test")
    
    # Get an open risk
    response = requests.get(f"{BASE_URL}/risks")
    risks = [r for r in response.json() if r["status"] == "open"]
    if not risks:
        print("❌ No open risks available")
        return
    
    risk_id = risks[0]["id"]
    control_id = risks[0]["control_id"]
    
    print(f"\nRisk ID: {risk_id}")
    print(f"Control ID: {control_id}")
    
    # Step 1: Get initial score
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    initial_score = response.json().get("current_score")
    print(f"\n1. Initial score: {initial_score}")
    
    # Step 2: Accept risk
    expiry_date = (datetime.now() + timedelta(days=30)).isoformat()
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/accept",
        json={
            "treatment": "accept",
            "justification": "End-to-end test",
            "expiry_date": expiry_date
        }
    )
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    score_after_accept = response.json().get("current_score")
    print(f"2. Score after acceptance: {score_after_accept}")
    
    # Step 3: Review risk
    response = requests.post(
        f"{BASE_URL}/risks/{risk_id}/review",
        json={
            "review_notes": "End-to-end test review",
            "review_cadence_days": 90
        }
    )
    response = requests.get(f"{BASE_URL}/controls/{control_id}")
    score_after_review = response.json().get("current_score")
    print(f"3. Score after review: {score_after_review}")
    
    # Step 4: Verify all scores are identical
    if initial_score == score_after_accept == score_after_review:
        print(f"\n✅ PASS: Score remained constant throughout risk lifecycle: {initial_score}")
    else:
        print(f"\n❌ FAIL: Score changed during risk operations:")
        print(f"   Initial: {initial_score}")
        print(f"   After accept: {score_after_accept}")
        print(f"   After review: {score_after_review}")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all EPIC 7 tests in sequence."""
    print("\n" + "#"*70)
    print("# EPIC 7 MANUAL TEST SUITE")
    print("# Requirements: Expiry enforcement, Review cadence, Score isolation")
    print("#"*70)
    
    tests = [
        ("Requirement 1: Expiry Enforcement", [
            test_1_accept_risk_requires_expiry,
            test_2_accept_risk_with_valid_expiry,
            test_3_accept_risk_with_past_expiry,
            test_4_list_expired_acceptances,
            test_5_enforce_expiry,
        ]),
        ("Requirement 2: Review Cadence", [
            test_6_mark_risk_reviewed,
            test_7_check_review_cadence,
        ]),
        ("Requirement 3: Score Isolation", [
            test_8_verify_score_isolation,
            test_9_end_to_end_score_isolation,
        ])
    ]
    
    for requirement_name, test_functions in tests:
        print("\n" + "="*70)
        print(requirement_name)
        print("="*70)
        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                print(f"\n❌ TEST ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "#"*70)
    print("# TEST SUITE COMPLETE")
    print("#"*70)


if __name__ == "__main__":
    print("\n⚠️  Make sure the backend server is running on localhost:8000")
    print("⚠️  Make sure the database is seeded with controls and evidence")
    input("\nPress Enter to start tests...")
    
    run_all_tests()
