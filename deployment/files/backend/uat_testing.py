# =============================================================================
# MILESTONE 6: USER ACCEPTANCE TESTING (UAT) SCRIPT
# =============================================================================
# PURPOSE: Automated testing suite to validate deployment success
# TESTS: API endpoints, model predictions, dashboard functionality
# =============================================================================

import requests
import json
import time
from datetime import datetime
from typing import Dict, List

# Configuration
API_BASE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:3000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class UATTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results = []
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} | {test_name}")
        if message:
            print(f"      {message}")
        
        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_health_endpoint(self):
        """Test 1: Health Check Endpoint"""
        print(f"\n{Colors.BLUE}TEST 1: Health Check{Colors.END}")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                data.get("status") == "healthy" and
                data.get("model_loaded") is True
            )
            
            self.log_test(
                "Health Check Endpoint",
                passed,
                f"Status: {data.get('status')}, Model Loaded: {data.get('model_loaded')}"
            )
        except Exception as e:
            self.log_test("Health Check Endpoint", False, f"Error: {str(e)}")
    
    def test_single_prediction(self):
        """Test 2: Single Prediction Endpoint"""
        print(f"\n{Colors.BLUE}TEST 2: Single Prediction{Colors.END}")
        try:
            payload = {
                "price": 75.0,
                "cost": 50.0,
                "discount_pct": 10.0,
                "inventory_units": 150,
                "competitor_price": 80.0,
                "category": 1,
                "region": 0,
                "seasonality": 2,
                "weather_condition": 1,
                "month": 4,
                "day_of_week": 2
            }
            
            response = requests.post(
                f"{self.base_url}/predict",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            # Validate response structure
            required_fields = [
                "predicted_demand",
                "recommended_price",
                "expected_revenue",
                "profit_margin",
                "confidence_interval"
            ]
            
            has_all_fields = all(field in data for field in required_fields)
            valid_values = (
                data.get("predicted_demand", 0) > 0 and
                data.get("expected_revenue", 0) > 0
            )
            
            passed = response.status_code == 200 and has_all_fields and valid_values
            
            self.log_test(
                "Single Prediction Endpoint",
                passed,
                f"Predicted Demand: {data.get('predicted_demand', 'N/A')}, Revenue: ₹{data.get('expected_revenue', 'N/A')}"
            )
        except Exception as e:
            self.log_test("Single Prediction Endpoint", False, f"Error: {str(e)}")
    
    def test_batch_prediction(self):
        """Test 3: Batch Prediction Endpoint"""
        print(f"\n{Colors.BLUE}TEST 3: Batch Prediction{Colors.END}")
        try:
            payload = {
                "predictions": [
                    {
                        "price": 70.0, "cost": 50.0, "discount_pct": 5.0,
                        "inventory_units": 100, "competitor_price": 75.0,
                        "category": 0, "region": 0, "seasonality": 1,
                        "weather_condition": 0, "month": 4, "day_of_week": 1
                    },
                    {
                        "price": 80.0, "cost": 55.0, "discount_pct": 15.0,
                        "inventory_units": 200, "competitor_price": 85.0,
                        "category": 1, "region": 1, "seasonality": 2,
                        "weather_condition": 1, "month": 5, "day_of_week": 3
                    }
                ]
            }
            
            response = requests.post(
                f"{self.base_url}/predict/batch",
                json=payload,
                timeout=15
            )
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                "predictions" in data and
                len(data["predictions"]) == 2 and
                "total_expected_revenue" in data
            )
            
            self.log_test(
                "Batch Prediction Endpoint",
                passed,
                f"Processed {data.get('count', 0)} predictions, Total Revenue: ₹{data.get('total_expected_revenue', 'N/A')}"
            )
        except Exception as e:
            self.log_test("Batch Prediction Endpoint", False, f"Error: {str(e)}")
    
    def test_price_optimization(self):
        """Test 4: Price Optimization Endpoint"""
        print(f"\n{Colors.BLUE}TEST 4: Price Optimization{Colors.END}")
        try:
            payload = {
                "base_price": 75.0,
                "cost": 50.0,
                "min_margin": 0.2,
                "max_discount": 0.3,
                "inventory_units": 100,
                "competitor_price": 80.0,
                "category": 1,
                "region": 0,
                "seasonality": 2,
                "weather_condition": 1,
                "month": 4,
                "day_of_week": 2
            }
            
            response = requests.post(
                f"{self.base_url}/optimize",
                json=payload,
                timeout=10
            )
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                "optimal_price" in data and
                "expected_revenue" in data and
                data.get("optimal_price", 0) >= payload["cost"] * (1 + payload["min_margin"])
            )
            
            self.log_test(
                "Price Optimization Endpoint",
                passed,
                f"Optimal Price: ₹{data.get('optimal_price', 'N/A')}, Expected Revenue: ₹{data.get('expected_revenue', 'N/A')}"
            )
        except Exception as e:
            self.log_test("Price Optimization Endpoint", False, f"Error: {str(e)}")
    
    def test_metrics_endpoint(self):
        """Test 5: Model Metrics Endpoint"""
        print(f"\n{Colors.BLUE}TEST 5: Model Metrics{Colors.END}")
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=5)
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                "model_info" in data and
                "performance" in data and
                "deployment" in data
            )
            
            self.log_test(
                "Model Metrics Endpoint",
                passed,
                f"Model: {data.get('model_info', {}).get('name', 'N/A')}, RMSE: {data.get('performance', {}).get('rmse', 'N/A')}"
            )
        except Exception as e:
            self.log_test("Model Metrics Endpoint", False, f"Error: {str(e)}")
    
    def test_kpi_dashboard(self):
        """Test 6: KPI Dashboard Endpoint"""
        print(f"\n{Colors.BLUE}TEST 6: KPI Dashboard{Colors.END}")
        try:
            response = requests.get(f"{self.base_url}/kpi/dashboard", timeout=5)
            data = response.json()
            
            required_sections = ["revenue", "demand", "pricing", "performance"]
            has_all_sections = all(section in data for section in required_sections)
            
            passed = response.status_code == 200 and has_all_sections
            
            self.log_test(
                "KPI Dashboard Endpoint",
                passed,
                f"Revenue: ₹{data.get('revenue', {}).get('total', 'N/A')}, ML Lift: {data.get('revenue', {}).get('ml_lift', 'N/A')}%"
            )
        except Exception as e:
            self.log_test("KPI Dashboard Endpoint", False, f"Error: {str(e)}")
    
    def test_ab_testing(self):
        """Test 7: A/B Testing Simulation"""
        print(f"\n{Colors.BLUE}TEST 7: A/B Testing{Colors.END}")
        try:
            payload = {
                "price_a": 70.0,
                "price_b": 75.0,
                "sample_size": 100,
                "features": {}
            }
            
            response = requests.post(
                f"{self.base_url}/experiment/ab_test",
                json=payload,
                timeout=15
            )
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                "variant_a" in data and
                "variant_b" in data and
                "analysis" in data and
                "recommendation" in data
            )
            
            self.log_test(
                "A/B Testing Simulation",
                passed,
                f"Winner: Variant {data.get('analysis', {}).get('winner', 'N/A')}, Lift: {data.get('analysis', {}).get('revenue_lift_pct', 'N/A')}%"
            )
        except Exception as e:
            self.log_test("A/B Testing Simulation", False, f"Error: {str(e)}")
    
    def test_elasticity_analysis(self):
        """Test 8: Price Elasticity Analysis"""
        print(f"\n{Colors.BLUE}TEST 8: Price Elasticity{Colors.END}")
        try:
            response = requests.get(
                f"{self.base_url}/experiment/elasticity?base_price=70&price_range=0.3&steps=10",
                timeout=10
            )
            data = response.json()
            
            passed = (
                response.status_code == 200 and
                "analysis" in data and
                "data_points" in data and
                "optimal_price" in data["analysis"]
            )
            
            self.log_test(
                "Price Elasticity Analysis",
                passed,
                f"Optimal Price: ₹{data.get('analysis', {}).get('optimal_price', 'N/A')}, Elasticity: {data.get('analysis', {}).get('avg_elasticity', 'N/A')}"
            )
        except Exception as e:
            self.log_test("Price Elasticity Analysis", False, f"Error: {str(e)}")
    
    def test_response_time(self):
        """Test 9: API Response Time"""
        print(f"\n{Colors.BLUE}TEST 9: Performance - Response Time{Colors.END}")
        try:
            start = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            latency = (time.time() - start) * 1000  # Convert to ms
            
            passed = response.status_code == 200 and latency < 100  # Under 100ms
            
            self.log_test(
                "API Response Time",
                passed,
                f"Latency: {latency:.2f}ms (Target: <100ms)"
            )
        except Exception as e:
            self.log_test("API Response Time", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test 10: Error Handling"""
        print(f"\n{Colors.BLUE}TEST 10: Error Handling{Colors.END}")
        try:
            # Send invalid data
            payload = {
                "price": -50.0,  # Invalid negative price
                "cost": 50.0
            }
            
            response = requests.post(
                f"{self.base_url}/predict",
                json=payload,
                timeout=5
            )
            
            # Should return 422 Validation Error
            passed = response.status_code == 422
            
            self.log_test(
                "Error Handling (Invalid Input)",
                passed,
                f"Status Code: {response.status_code} (Expected: 422)"
            )
        except Exception as e:
            self.log_test("Error Handling (Invalid Input)", False, f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate final UAT report"""
        print(f"\n{'='*70}")
        print(f"{Colors.BLUE}UAT TEST REPORT - MILESTONE 6{Colors.END}")
        print(f"{'='*70}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"API URL: {self.base_url}")
        print(f"\nTest Results:")
        print(f"  {Colors.GREEN}✓ Passed: {self.passed}{Colors.END}")
        print(f"  {Colors.RED}✗ Failed: {self.failed}{Colors.END}")
        print(f"  Total: {self.passed + self.failed}")
        
        success_rate = (self.passed / (self.passed + self.failed)) * 100 if (self.passed + self.failed) > 0 else 0
        print(f"  Success Rate: {success_rate:.1f}%")
        
        print(f"\n{'='*70}")
        
        if self.failed == 0:
            print(f"{Colors.GREEN}🎉 ALL TESTS PASSED - DEPLOYMENT SUCCESSFUL!{Colors.END}")
            print(f"{Colors.GREEN}✅ System is ready for production rollout{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED - REVIEW REQUIRED{Colors.END}")
            print(f"{Colors.YELLOW}Please fix issues before production deployment{Colors.END}")
        
        print(f"{'='*70}\n")
        
        # Save results to file
        with open("uat_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total": self.passed + self.failed,
                    "passed": self.passed,
                    "failed": self.failed,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "tests": self.results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: uat_test_results.json\n")

def run_uat_tests():
    """Main UAT test runner"""
    print(f"\n{Colors.BLUE}{'='*70}")
    print(f"  PRICEOPTIMA - USER ACCEPTANCE TESTING (UAT)")
    print(f"  Milestone 6: Deployment & Dashboard Validation")
    print(f"{'='*70}{Colors.END}\n")
    
    tester = UATTester(API_BASE_URL)
    
    # Run all tests
    tester.test_health_endpoint()
    tester.test_single_prediction()
    tester.test_batch_prediction()
    tester.test_price_optimization()
    tester.test_metrics_endpoint()
    tester.test_kpi_dashboard()
    tester.test_ab_testing()
    tester.test_elasticity_analysis()
    tester.test_response_time()
    tester.test_error_handling()
    
    # Generate final report
    tester.generate_report()

if __name__ == "__main__":
    print("\n⏳ Starting UAT Test Suite...")
    print("📌 Ensure backend is running at http://localhost:8000\n")
    
    try:
        # Check if API is reachable
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            run_uat_tests()
        else:
            print(f"{Colors.RED}❌ API not responding correctly. Please start the backend first.{Colors.END}")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Cannot connect to API at {API_BASE_URL}")
        print(f"Please ensure the backend is running:{Colors.END}")
        print(f"  1. cd backend")
        print(f"  2. uvicorn main:app --reload")
        print(f"  OR")
        print(f"  docker-compose up -d\n")
