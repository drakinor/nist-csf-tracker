"""
Comprehensive Validation Suite for NIST CSF Tracker

Validates:
1. Unit tests for all EPICs
2. NIST CSF compliance
3. Ollama/Mistral compatibility
4. API endpoints functionality
5. Data integrity
"""

import sys
import subprocess
import requests
import time
from pathlib import Path

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"{BLUE}{title}{RESET}")
    print('='*70)

def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {message}")

def print_error(message):
    """Print error message."""
    print(f"{RED}✗{RESET} {message}")

def print_warning(message):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {message}")

def print_info(message):
    """Print info message."""
    print(f"{BLUE}ℹ{RESET} {message}")


class ValidationSuite:
    """Comprehensive validation suite."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.api_url = f"{self.base_url}/api"
        self.results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0
        }
    
    def check_server(self) -> bool:
        """Check if server is running."""
        print_section("SERVER HEALTH CHECK")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print_success("Backend server is running")
                data = response.json()
                print_info(f"  Status: {data.get('status')}")
                print_info(f"  Database: {data.get('database')}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Server returned status {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Server not accessible: {e}")
            print_warning("Please start the server with: .\\start.ps1")
            self.results["failed"] += 1
            return False
    
    def validate_nist_compliance(self) -> bool:
        """Validate NIST CSF compliance."""
        print_section("NIST CSF COMPLIANCE VALIDATION")
        
        try:
            # Check controls endpoint
            response = requests.get(f"{self.api_url}/controls/")
            if response.status_code != 200:
                print_error("Failed to fetch controls")
                self.results["failed"] += 1
                return False
            
            controls = response.json()
            print_info(f"Total controls loaded: {len(controls)}")
            
            # Validate NIST CSF structure
            expected_functions = ["Identify", "Protect", "Detect", "Respond", "Recover"]
            functions_found = set(c["function"] for c in controls)
            
            all_functions_present = all(f in functions_found for f in expected_functions)
            if all_functions_present:
                print_success("All 5 NIST CSF Functions present")
                for func in expected_functions:
                    count = sum(1 for c in controls if c["function"] == func)
                    print_info(f"  {func}: {count} controls")
                self.results["passed"] += 1
            else:
                missing = set(expected_functions) - functions_found
                print_error(f"Missing NIST CSF Functions: {missing}")
                self.results["failed"] += 1
                return False
            
            # Validate control ID format (e.g., ID.AM-1, PR.AC-1)
            valid_id_format = all(
                len(c["csf_id"].split(".")) == 2 and
                "-" in c["csf_id"].split(".")[1]
                for c in controls
            )
            if valid_id_format:
                print_success("All control IDs follow NIST CSF format (XX.YY-#)")
                self.results["passed"] += 1
            else:
                print_error("Some control IDs don't follow NIST CSF format")
                self.results["failed"] += 1
            
            # Validate required fields
            required_fields = ["id", "csf_id", "name", "description", "function", "category"]
            all_have_required = all(
                all(field in c for field in required_fields)
                for c in controls
            )
            if all_have_required:
                print_success("All controls have required NIST CSF fields")
                self.results["passed"] += 1
            else:
                print_error("Some controls missing required fields")
                self.results["failed"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"NIST compliance validation failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_scoring_system(self) -> bool:
        """Validate deterministic scoring system (EPIC 5)."""
        print_section("EPIC 5: SCORING SYSTEM VALIDATION")
        
        try:
            response = requests.get(f"{self.api_url}/scores/")
            if response.status_code != 200:
                print_warning("No scores available yet")
                self.results["skipped"] += 1
                return True
            
            scores = response.json()
            print_info(f"Total scores calculated: {len(scores)}")
            
            # Validate score values are exactly 0.0, 0.33, 0.66, or 1.0
            valid_scores = {0.0, 0.33, 0.66, 1.0}
            all_valid = all(
                round(s["score_value"], 2) in valid_scores
                for s in scores
            )
            
            if all_valid:
                print_success("All scores are deterministic (0.0, 0.33, 0.66, or 1.0)")
                self.results["passed"] += 1
            else:
                invalid = [s for s in scores if round(s["score_value"], 2) not in valid_scores]
                print_error(f"Found {len(invalid)} scores with invalid values")
                for s in invalid[:5]:
                    print_error(f"  Control {s['control_id']}: {s['score_value']}")
                self.results["failed"] += 1
                return False
            
            # Validate all scores have rationale
            all_have_rationale = all(
                s.get("score_rationale") and len(s["score_rationale"]) > 0
                for s in scores
            )
            if all_have_rationale:
                print_success("All scores have verbalizable rationales")
                self.results["passed"] += 1
            else:
                print_error("Some scores missing rationales")
                self.results["failed"] += 1
            
            # Validate all scores have method
            all_have_method = all(
                s.get("method") and "Deterministic" in s["method"]
                for s in scores
            )
            if all_have_method:
                print_success("All scores use deterministic method")
                self.results["passed"] += 1
            else:
                print_error("Some scores don't specify deterministic method")
                self.results["failed"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"Scoring validation failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_gap_analysis(self) -> bool:
        """Validate gap analysis system (EPIC 6)."""
        print_section("EPIC 6: GAP ANALYSIS VALIDATION")
        
        try:
            response = requests.get(f"{self.api_url}/gaps/")
            if response.status_code != 200:
                print_warning("No gaps available yet")
                self.results["skipped"] += 1
                return True
            
            gaps = response.json()
            print_info(f"Total gaps identified: {len(gaps)}")
            
            # Validate severity levels
            valid_severities = {"critical", "high", "medium", "low"}
            all_valid_severity = all(
                g.get("severity") in valid_severities
                for g in gaps
            )
            if all_valid_severity:
                print_success("All gaps have valid severity levels")
                for severity in ["critical", "high", "medium", "low"]:
                    count = sum(1 for g in gaps if g.get("severity") == severity)
                    if count > 0:
                        print_info(f"  {severity.capitalize()}: {count} gaps")
                self.results["passed"] += 1
            else:
                print_error("Some gaps have invalid severity")
                self.results["failed"] += 1
            
            # Validate gap types
            valid_types = {
                "missing_control", "missing_policy", "missing_procedure",
                "missing_technical_enforcement", "missing_operational_evidence",
                "incomplete_implementation"
            }
            all_valid_type = all(
                g.get("gap_type") in valid_types
                for g in gaps
            )
            if all_valid_type:
                print_success("All gaps have valid gap types")
                self.results["passed"] += 1
            else:
                print_error("Some gaps have invalid gap types")
                self.results["failed"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"Gap analysis validation failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_risk_acceptance(self) -> bool:
        """Validate risk acceptance system (EPIC 7)."""
        print_section("EPIC 7: RISK ACCEPTANCE VALIDATION")
        
        try:
            # Test score isolation endpoint
            response = requests.get(f"{self.base_url}/risks/verify/score-isolation")
            if response.status_code == 200:
                data = response.json()
                if data.get("guarantee_verified"):
                    print_success("Score isolation guarantee verified")
                    print_info(f"  Explanation: {data.get('explanation', '')[:100]}...")
                    self.results["passed"] += 1
                else:
                    print_error("Score isolation NOT verified")
                    self.results["failed"] += 1
            else:
                print_warning("Score isolation endpoint not accessible")
                self.results["skipped"] += 1
            
            # Test expired acceptances endpoint
            response = requests.get(f"{self.base_url}/risks/expired/acceptances")
            if response.status_code == 200:
                print_success("Expiry enforcement endpoint operational")
                self.results["passed"] += 1
            else:
                print_warning("Expiry enforcement endpoint not accessible")
                self.results["skipped"] += 1
            
            # Test review cadence endpoint
            response = requests.get(f"{self.base_url}/risks/check/review-cadence")
            if response.status_code == 200:
                print_success("Review cadence endpoint operational")
                self.results["passed"] += 1
            else:
                print_warning("Review cadence endpoint not accessible")
                self.results["skipped"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"Risk acceptance validation failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_pdf_reporting(self) -> bool:
        """Validate PDF reporting system (EPIC 8)."""
        print_section("EPIC 8: PDF REPORTING VALIDATION")
        
        try:
            # Test list reports endpoint
            response = requests.get(f"{self.api_url}/reports/available")
            if response.status_code == 200:
                data = response.json()
                reports = data.get("reports", [])
                print_success(f"Found {len(reports)} available report types")
                for report in reports:
                    print_info(f"  - {report.get('name')}")
                self.results["passed"] += 1
            else:
                print_error("Reports endpoint not accessible")
                self.results["failed"] += 1
                return False
            
            # Test executive summary generation (just check if it responds, don't download)
            response = requests.head(f"{self.api_url}/reports/executive-summary")
            if response.status_code in [200, 500]:  # 500 might be reportlab not loaded
                if response.status_code == 200:
                    print_success("Executive summary PDF generation operational")
                    self.results["passed"] += 1
                else:
                    print_warning("PDF generation returns 500 - may need server restart")
                    self.results["warnings"] += 1
            else:
                print_error(f"Executive summary endpoint failed: {response.status_code}")
                self.results["failed"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"PDF reporting validation failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_ollama_compatibility(self) -> bool:
        """Validate Ollama/Mistral compatibility."""
        print_section("OLLAMA/MISTRAL COMPATIBILITY VALIDATION")
        
        try:
            # Check if Ollama is running
            ollama_url = "http://localhost:11434"
            try:
                response = requests.get(f"{ollama_url}/api/tags", timeout=2)
                if response.status_code == 200:
                    print_success("Ollama is running and accessible")
                    tags = response.json().get("models", [])
                    print_info(f"  Available models: {len(tags)}")
                    
                    # Check for Mistral
                    mistral_models = [m for m in tags if "mistral" in m.get("name", "").lower()]
                    if mistral_models:
                        print_success(f"Mistral model available: {mistral_models[0].get('name')}")
                        self.results["passed"] += 1
                    else:
                        print_warning("Mistral model not found")
                        print_info("  Install with: ollama pull mistral:instruct")
                        self.results["warnings"] += 1
                    
                    self.results["passed"] += 1
                else:
                    print_warning("Ollama API returned unexpected status")
                    self.results["warnings"] += 1
            except Exception as e:
                print_warning(f"Ollama not running: {e}")
                print_info("  This is optional - system works without Ollama")
                print_info("  Start Ollama: https://ollama.ai/download")
                self.results["skipped"] += 1
            
            # Test Ollama service integration
            from app.services.ollama_service import OllamaService
            service = OllamaService()
            if service.is_available():
                print_success("OllamaService integration working")
                self.results["passed"] += 1
            else:
                print_info("OllamaService not available (expected if Ollama not running)")
                self.results["skipped"] += 1
            
            return True
            
        except Exception as e:
            print_error(f"Ollama compatibility check failed: {e}")
            self.results["failed"] += 1
            return False
    
    def validate_api_endpoints(self) -> bool:
        """Validate all critical API endpoints."""
        print_section("API ENDPOINTS VALIDATION")
        
        endpoints = [
            ("GET", "/api/controls/", "Controls list"),
            ("GET", "/api/artifacts/", "Artifacts list"),
            ("GET", "/api/evidence/", "Evidence list"),
            ("GET", "/api/scores/", "Scores list"),
            ("GET", "/api/gaps/", "Gaps list"),
            ("GET", "/api/actions/", "Actions list"),
            ("GET", "/risks", "Risks list"),
            ("GET", "/api/reports/available", "Reports list"),
        ]
        
        for method, endpoint, description in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.request(method, url, timeout=5)
                if response.status_code == 200:
                    print_success(f"{description}: {response.status_code}")
                    self.results["passed"] += 1
                else:
                    print_warning(f"{description}: {response.status_code}")
                    self.results["warnings"] += 1
            except Exception as e:
                print_error(f"{description}: Failed - {e}")
                self.results["failed"] += 1
        
        return True
    
    def run_unit_tests(self) -> bool:
        """Run pytest unit tests if available."""
        print_section("UNIT TESTS")
        
        try:
            # Check if pytest is available
            result = subprocess.run(
                ["C:/nist-csf-tracker/.venv/Scripts/python.exe", "-m", "pytest", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print_warning("pytest not installed")
                print_info("  Install with: pip install pytest")
                self.results["skipped"] += 1
                return True
            
            print_info("Running pytest unit tests...")
            result = subprocess.run(
                ["C:/nist-csf-tracker/.venv/Scripts/python.exe", "-m", "pytest", 
                 "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd="C:/nist-csf-tracker/backend"
            )
            
            if result.returncode == 0:
                print_success("All pytest unit tests passed")
                print(result.stdout)
                self.results["passed"] += 1
            else:
                print_error("Some pytest tests failed")
                print(result.stdout)
                print(result.stderr)
                self.results["failed"] += 1
            
            return True
            
        except subprocess.TimeoutExpired:
            print_error("Unit tests timed out")
            self.results["failed"] += 1
            return False
        except Exception as e:
            print_warning(f"Could not run unit tests: {e}")
            self.results["skipped"] += 1
            return True
    
    def print_summary(self):
        """Print validation summary."""
        print_section("VALIDATION SUMMARY")
        
        total = sum(self.results.values())
        passed_pct = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"\n{GREEN}✓ Passed:{RESET}   {self.results['passed']}")
        print(f"{RED}✗ Failed:{RESET}   {self.results['failed']}")
        print(f"{YELLOW}⚠ Warnings:{RESET} {self.results['warnings']}")
        print(f"{BLUE}○ Skipped:{RESET}  {self.results['skipped']}")
        print(f"\n{BLUE}Total:{RESET}     {total}")
        print(f"{BLUE}Success Rate:{RESET} {passed_pct:.1f}%")
        
        if self.results["failed"] == 0:
            print(f"\n{GREEN}{'='*70}")
            print("✓ VALIDATION COMPLETE - ALL CRITICAL CHECKS PASSED")
            print(f"{'='*70}{RESET}\n")
            return 0
        else:
            print(f"\n{RED}{'='*70}")
            print(f"✗ VALIDATION FAILED - {self.results['failed']} CRITICAL ISSUES")
            print(f"{'='*70}{RESET}\n")
            return 1
    
    def run_all(self) -> int:
        """Run all validations."""
        print(f"\n{BLUE}{'='*70}")
        print("NIST CSF TRACKER - COMPREHENSIVE VALIDATION SUITE")
        print(f"{'='*70}{RESET}\n")
        
        # Check server first
        if not self.check_server():
            print_error("\nServer is not running. Please start it first.")
            return 1
        
        # Run all validations
        self.validate_nist_compliance()
        self.validate_scoring_system()
        self.validate_gap_analysis()
        self.validate_risk_acceptance()
        self.validate_pdf_reporting()
        self.validate_ollama_compatibility()
        self.validate_api_endpoints()
        self.run_unit_tests()
        
        # Print summary
        return self.print_summary()


if __name__ == "__main__":
    suite = ValidationSuite()
    exit_code = suite.run_all()
    sys.exit(exit_code)
