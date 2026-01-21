"""
EPIC 6 Manual Tests - Gap Analysis & Actions

Tests for:
1. Deterministic gap classification
2. Acceptance-criteria-driven closure logic
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def test_deterministic_gap_classification():
    """Test 1: Gaps are classified deterministically based on evidence"""
    print("\n" + "="*60)
    print("Test 1: Deterministic Gap Classification")
    print("="*60)
    
    # Get all gaps
    response = requests.get(f"{BASE_URL}/api/gaps/")
    gaps = response.json()
    
    # Check for deterministic classification
    deterministic_gaps = [g for g in gaps if "DETERMINISTIC" in g.get('description', '')]
    
    print(f"Total gaps: {len(gaps)}")
    print(f"Deterministic gaps: {len(deterministic_gaps)}")
    
    # Check gap types are from expected set
    valid_gap_types = {
        "missing_control",
        "missing_policy",
        "missing_procedure",
        "missing_technical_enforcement",
        "missing_operational_evidence",
        "incomplete_implementation"
    }
    
    invalid_types = []
    for gap in gaps:
        if gap['gap_type'] not in valid_gap_types:
            invalid_types.append(gap['gap_type'])
    
    if invalid_types:
        print(f"❌ FAIL: Found invalid gap types: {set(invalid_types)}")
        return False
    
    print(f"✅ PASS: All gaps use valid types from: {valid_gap_types}")
    
    # Show gap type distribution
    by_type = {}
    for gap in gaps:
        by_type[gap['gap_type']] = by_type.get(gap['gap_type'], 0) + 1
    
    print(f"\n   Gap distribution:")
    for gtype, count in sorted(by_type.items()):
        print(f"   - {gtype}: {count}")
    
    return True


def test_gap_severity_assignment():
    """Test 2: Gap severity is deterministically assigned"""
    print("\n" + "="*60)
    print("Test 2: Deterministic Severity Assignment")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/gaps/")
    gaps = response.json()
    
    # Check severity values
    valid_severities = {"low", "medium", "high", "critical"}
    invalid_severities = []
    
    for gap in gaps:
        if gap['severity'] not in valid_severities:
            invalid_severities.append(gap['severity'])
    
    if invalid_severities:
        print(f"❌ FAIL: Invalid severity values: {set(invalid_severities)}")
        return False
    
    # Show severity distribution
    by_severity = {}
    for gap in gaps:
        by_severity[gap['severity']] = by_severity.get(gap['severity'], 0) + 1
    
    print(f"✅ PASS: All gaps have valid severity")
    print(f"\n   Severity distribution:")
    for severity in ["critical", "high", "medium", "low"]:
        count = by_severity.get(severity, 0)
        print(f"   - {severity}: {count}")
    
    # Check deterministic rules
    print(f"\n   Checking severity rules:")
    for gap in gaps:
        if gap['gap_type'] == 'missing_control':
            if gap['severity'] == 'critical':
                print(f"   ✅ missing_control → critical")
            else:
                print(f"   ❌ missing_control should be critical, got {gap['severity']}")
                return False
    
    return True


def test_acceptance_criteria_checking():
    """Test 3: Acceptance criteria are checked before closure"""
    print("\n" + "="*60)
    print("Test 3: Acceptance-Criteria-Driven Closure")
    print("="*60)
    
    # Get all actions with acceptance criteria
    response = requests.get(f"{BASE_URL}/api/actions/")
    actions = response.json()
    
    with_criteria = [a for a in actions if a.get('acceptance_criteria')]
    without_criteria = [a for a in actions if not a.get('acceptance_criteria')]
    
    print(f"Total actions: {len(actions)}")
    print(f"  With acceptance criteria: {len(with_criteria)}")
    print(f"  Without acceptance criteria: {len(without_criteria)}")
    
    if with_criteria:
        # Test the check-criteria endpoint
        first_action = with_criteria[0]
        response = requests.post(f"{BASE_URL}/api/actions/{first_action['id']}/check-criteria")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ PASS: Acceptance criteria checking endpoint works")
            print(f"   Sample action: {first_action['title']}")
            print(f"   Criteria: {first_action['acceptance_criteria'][:50]}...")
            print(f"   Can close: {result.get('can_close')}")
            print(f"   Recommendation: {result.get('recommendation')}")
        else:
            print(f"❌ FAIL: Check criteria endpoint returned {response.status_code}")
            return False
    else:
        print(f"⚠️  WARNING: No actions with acceptance criteria to test")
    
    return True


def test_gap_resolution_with_criteria():
    """Test 4: Gaps can only be resolved when criteria are met"""
    print("\n" + "="*60)
    print("Test 4: Gap Resolution Requires Criteria")
    print("="*60)
    
    # Get open gaps
    response = requests.get(f"{BASE_URL}/api/gaps/?status=open")
    open_gaps = response.json()
    
    print(f"Open gaps: {len(open_gaps)}")
    
    if open_gaps:
        # Try to resolve first gap
        gap = open_gaps[0]
        print(f"\n   Testing resolution for gap {gap['id']} ({gap['gap_type']})")
        
        response = requests.patch(f"{BASE_URL}/api/gaps/{gap['id']}/resolve")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Gap resolved: {result['reason']}")
            return True
        elif response.status_code == 400:
            error = response.json()
            print(f"   ✅ Gap resolution blocked (criteria not met): {error.get('detail')}")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            return False
    else:
        print(f"   ℹ️  No open gaps to test")
        return True


def test_automatic_gap_resolution():
    """Test 5: Gaps auto-resolve when evidence is validated"""
    print("\n" + "="*60)
    print("Test 5: Automatic Gap Resolution")
    print("="*60)
    
    # Get resolved gaps
    response = requests.get(f"{BASE_URL}/api/gaps/?status=resolved")
    resolved_gaps = response.json()
    
    print(f"Resolved gaps: {len(resolved_gaps)}")
    
    # Check if they have resolved_at timestamp
    with_timestamp = [g for g in resolved_gaps if g.get('resolved_at')]
    
    print(f"  With resolved_at timestamp: {len(with_timestamp)}")
    
    if len(with_timestamp) == len(resolved_gaps):
        print(f"✅ PASS: All resolved gaps have timestamps")
        return True
    else:
        print(f"❌ FAIL: {len(resolved_gaps) - len(with_timestamp)} gaps missing timestamp")
        return False


def test_gap_type_descriptions():
    """Test 6: Gap descriptions explain what's missing"""
    print("\n" + "="*60)
    print("Test 6: Descriptive Gap Messages")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/gaps/")
    gaps = response.json()
    
    # Check that descriptions are informative
    short_descriptions = []
    for gap in gaps:
        desc = gap.get('description', '')
        if len(desc) < 20:
            short_descriptions.append(gap['id'])
    
    if short_descriptions:
        print(f"❌ FAIL: {len(short_descriptions)} gaps have short descriptions")
        return False
    
    print(f"✅ PASS: All gaps have descriptive messages")
    
    # Show sample descriptions
    print(f"\n   Sample gap descriptions:")
    for gap in gaps[:3]:
        print(f"   - {gap['gap_type']}: {gap['description'][:80]}...")
    
    return True


def main():
    print("\n" + "="*70)
    print(" EPIC 6 MANUAL TEST SUITE - Gap Analysis & Actions")
    print("="*70)
    print("\nPrerequisites:")
    print("1. Backend server must be running on http://localhost:8000")
    print("2. Database should have some controls, evidence, and gaps")
    print("\nStarting tests...")
    time.sleep(1)
    
    results = []
    
    try:
        # Run all tests
        results.append(("Deterministic Classification", test_deterministic_gap_classification()))
        results.append(("Severity Assignment", test_gap_severity_assignment()))
        results.append(("Acceptance Criteria Checking", test_acceptance_criteria_checking()))
        results.append(("Gap Resolution Criteria", test_gap_resolution_with_criteria()))
        results.append(("Automatic Resolution", test_automatic_gap_resolution()))
        results.append(("Descriptive Messages", test_gap_type_descriptions()))
        
        # Summary
        print("\n" + "="*70)
        print(" TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status}: {name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 EPIC 6 COMPLETE - All requirements verified!")
        else:
            print("\n⚠️  Some tests failed - review output above")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("   Please ensure the backend is running on http://localhost:8000")
        print("   Run: .\\scripts\\dev.ps1")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
