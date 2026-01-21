"""
Manual Test for EPIC 8: PDF Report Generation

Tests all PDF report endpoints.
"""

import requests
import time

BASE_URL = "http://localhost:8000/api"

def test_reports():
    """Test all PDF report generation endpoints."""
    
    # Wait for server to be ready
    print("Waiting for server...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Server is ready\n")
                break
        except:
            time.sleep(1)
    
    # Test 1: List available reports
    print("=" * 70)
    print("TEST 1: List Available Reports")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/reports/available")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Available reports: {len(data['reports'])}")
            for report in data['reports']:
                print(f"  - {report['name']}: {report['description']}")
            print("✅ PASS: List available reports")
        else:
            print(f"❌ FAIL: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n")
    
    # Test 2: Generate Executive Summary
    print("=" * 70)
    print("TEST 2: Generate Executive Summary PDF")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/reports/executive-summary?organization=Test%20Organization")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            # Save PDF for manual inspection
            with open("test_executive_summary.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PASS: Executive summary PDF generated (saved as test_executive_summary.pdf)")
        else:
            print(f"❌ FAIL: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n")
    
    # Test 3: Generate Compliance Report
    print("=" * 70)
    print("TEST 3: Generate Compliance Report PDF")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/reports/compliance?organization=Test%20Organization")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            with open("test_compliance_report.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PASS: Compliance report PDF generated (saved as test_compliance_report.pdf)")
        else:
            print(f"❌ FAIL: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n")
    
    # Test 4: Generate Gap Analysis Report
    print("=" * 70)
    print("TEST 4: Generate Gap Analysis Report PDF")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/reports/gap-analysis?organization=Test%20Organization")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            with open("test_gap_analysis.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PASS: Gap analysis PDF generated (saved as test_gap_analysis.pdf)")
        else:
            print(f"❌ FAIL: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n")
    
    # Test 5: Generate Action Plan Report
    print("=" * 70)
    print("TEST 5: Generate Action Plan Report PDF")
    print("=" * 70)
    try:
        response = requests.get(f"{BASE_URL}/reports/action-plan?organization=Test%20Organization")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
            with open("test_action_plan.pdf", "wb") as f:
                f.write(response.content)
            print("✅ PASS: Action plan PDF generated (saved as test_action_plan.pdf)")
        else:
            print(f"❌ FAIL: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n")
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("All PDF files have been saved to the current directory.")
    print("Please open them manually to verify content quality.")
    print("=" * 70)


if __name__ == "__main__":
    test_reports()
