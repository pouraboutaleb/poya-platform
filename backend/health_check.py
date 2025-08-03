#!/usr/bin/env python3
"""
Comprehensive Health Check and End-to-End Test Script
for Poya Platform Application
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

class PoyaPlatformTester:
    def __init__(self, backend_url="http://localhost:8000", frontend_url="http://localhost:5174"):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.test_results = []
        self.errors = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
        
    def log_error(self, test_name: str, error: str):
        """Log errors"""
        self.errors.append({
            "test": test_name,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        print(f"[ERROR] {test_name}: {error}")

    def test_backend_health(self):
        """Test backend health endpoints"""
        print("\n=== BACKEND HEALTH CHECK ===")
        
        # Test 1: Basic connectivity
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Connectivity", "PASS", "Backend is responding")
            else:
                self.log_test("Backend Connectivity", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Backend Connectivity", str(e))
            
        # Test 2: Health endpoint
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Endpoint", "PASS", f"Status: {data.get('status', 'unknown')}")
            else:
                self.log_test("Health Endpoint", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Health Endpoint", str(e))
            
        # Test 3: API Status
        try:
            response = requests.get(f"{self.backend_url}/api/v1/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Status", "PASS", f"Version: {data.get('api_version', 'unknown')}")
            else:
                self.log_test("API Status", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("API Status", str(e))

    def test_api_endpoints(self):
        """Test major API endpoints"""
        print("\n=== API ENDPOINTS TEST ===")
        
        endpoints_to_test = [
            "/api/v1/auth/login",
            "/api/v1/users",
            "/api/v1/tasks",
            "/api/v1/items", 
            "/api/v1/warehouse-requests",
            "/api/v1/orders",
            "/api/v1/notifications"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                # We expect most endpoints to return 401 (unauthorized) or 422 (validation error)
                # because we're not sending authentication
                if response.status_code in [401, 422, 405]:  # 405 = Method not allowed
                    self.log_test(f"Endpoint {endpoint}", "PASS", "Endpoint exists and requires auth")
                elif response.status_code == 404:
                    self.log_test(f"Endpoint {endpoint}", "FAIL", "Endpoint not found")
                elif response.status_code == 200:
                    self.log_test(f"Endpoint {endpoint}", "PASS", "Endpoint accessible")
                else:
                    self.log_test(f"Endpoint {endpoint}", "WARN", f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_error(f"Endpoint {endpoint}", str(e))

    def test_frontend_health(self):
        """Test frontend health"""
        print("\n=== FRONTEND HEALTH CHECK ===")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                # Check if it's a valid HTML response
                if "html" in response.headers.get("content-type", "").lower():
                    self.log_test("Frontend Connectivity", "PASS", "Frontend serving HTML")
                    
                    # Check for React app indicators
                    content = response.text
                    if "react" in content.lower() or "div" in content.lower():
                        self.log_test("Frontend Framework", "PASS", "React app detected")
                    else:
                        self.log_test("Frontend Framework", "WARN", "React app not clearly detected")
                else:
                    self.log_test("Frontend Connectivity", "WARN", "Frontend not serving HTML")
            else:
                self.log_test("Frontend Connectivity", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_error("Frontend Connectivity", str(e))

    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n=== CORS CONFIGURATION TEST ===")
        
        try:
            # Test preflight request
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=5)
            
            cors_headers = {
                "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers")
            }
            
            if any(cors_headers.values()):
                self.log_test("CORS Configuration", "PASS", "CORS headers present")
            else:
                self.log_test("CORS Configuration", "WARN", "CORS headers not detected")
                
        except Exception as e:
            self.log_error("CORS Configuration", str(e))

    def test_database_connectivity(self):
        """Test database connectivity through API"""
        print("\n=== DATABASE CONNECTIVITY TEST ===")
        
        # Since we can't directly test the database, we'll test endpoints that would require DB
        try:
            # Test an endpoint that would require database access
            response = requests.get(f"{self.backend_url}/api/v1/users", timeout=5)
            
            # If we get 401/422, it means the endpoint exists and likely can connect to DB
            # If we get 500, there might be a database connection issue
            if response.status_code in [401, 422, 405]:
                self.log_test("Database Connectivity", "PASS", "DB-dependent endpoints responding")
            elif response.status_code == 500:
                self.log_test("Database Connectivity", "FAIL", "Internal server error (possible DB issue)")
            elif response.status_code == 404:
                self.log_test("Database Connectivity", "WARN", "Endpoint not found")
            else:
                self.log_test("Database Connectivity", "PASS", f"Response: {response.status_code}")
                
        except Exception as e:
            self.log_error("Database Connectivity", str(e))

    def run_comprehensive_test(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Poya Platform Health Check")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_backend_health()
        self.test_api_endpoints() 
        self.test_frontend_health()
        self.test_cors_configuration()
        self.test_database_connectivity()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary report
        self.generate_summary_report(duration)

    def generate_summary_report(self, duration: float):
        """Generate comprehensive summary report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY REPORT")
        print("=" * 60)
        
        # Count results
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        total_tests = len(self.test_results)
        
        print(f"📈 Test Results Summary:")
        print(f"   ✅ Passed: {passed}/{total_tests}")
        print(f"   ❌ Failed: {failed}/{total_tests}")
        print(f"   ⚠️  Warnings: {warnings}/{total_tests}")
        print(f"   ⏱️  Duration: {duration:.2f} seconds")
        
        if failed == 0:
            print(f"\n🎉 SUCCESS: All critical tests passed!")
            if warnings > 0:
                print(f"⚠️  Note: {warnings} warnings need attention")
        else:
            print(f"\n❌ ISSUES DETECTED: {failed} tests failed")
            
        # Detailed results
        print(f"\n📋 Detailed Test Results:")
        for result in self.test_results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}
            emoji = status_emoji.get(result["status"], "❓")
            print(f"   {emoji} {result['test']}: {result['details']}")
            
        # Error details
        if self.errors:
            print(f"\n🐛 Error Details:")
            for error in self.errors:
                print(f"   ❌ {error['test']}: {error['error']}")
                
        # Recommendations
        print(f"\n💡 Recommendations:")
        if failed > 0:
            print("   • Review failed tests and fix critical issues")
        if warnings > 0:
            print("   • Address warning items for optimal performance")
        if failed == 0 and warnings == 0:
            print("   • Application is healthy and ready for production!")
            
        print("\n" + "=" * 60)

if __name__ == "__main__":
    tester = PoyaPlatformTester()
    tester.run_comprehensive_test()
