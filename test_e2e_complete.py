#!/usr/bin/env python3
"""
Darbot Agent Engine End-to-End Test
Validates the complete setup including task creation workflow
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

class DarbotE2ETest:
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        self.test_session_id = f"test_session_{int(time.time())}"
        self.results = {
            "backend_health": False,
            "frontend_health": False,
            "task_creation": False,
            "api_connectivity": False,
            "errors": []
        }

    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            print("🔍 Testing backend health...")
            response = requests.get(f"{self.backend_url}/api/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Backend health: {health_data.get('overall_status', 'unknown')}")
                self.results["backend_health"] = True
                return True
            else:
                print(f"❌ Backend health failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Backend health check failed: {e}")
            self.results["errors"].append(f"Backend health error: {e}")
            return False

    def test_frontend_health(self) -> bool:
        """Test frontend accessibility"""
        try:
            print("🌐 Testing frontend accessibility...")
            response = requests.get(self.frontend_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Frontend is accessible")
                self.results["frontend_health"] = True
                return True
            else:
                print(f"❌ Frontend failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            self.results["errors"].append(f"Frontend error: {e}")
            return False

    def test_api_connectivity(self) -> bool:
        """Test API endpoints connectivity"""
        try:
            print("🔗 Testing API connectivity...")
            
            # Test plans endpoint
            response = requests.get(f"{self.backend_url}/api/plans", timeout=10)
            if response.status_code == 200:
                print("✅ Plans API accessible")
                self.results["api_connectivity"] = True
                return True
            else:
                print(f"❌ Plans API failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ API connectivity test failed: {e}")
            self.results["errors"].append(f"API connectivity error: {e}")
            return False

    def test_task_creation(self) -> bool:
        """Test task creation with authentication headers"""
        try:
            print("📝 Testing task creation...")
            
            headers = {
                "Content-Type": "application/json",
                "X-Ms-Client-Principal-Id": "test-user-12345",
                "X-Ms-Client-Principal-Name": "Test User"
            }
            
            task_data = {
                "description": "I need help with testing the Darbot Agent Engine setup",
                "session_id": self.test_session_id
            }
            
            print(f"📤 Submitting task: {task_data['description']}")
            response = requests.post(
                f"{self.backend_url}/api/input_task",
                json=task_data,
                headers=headers,
                timeout=30
            )
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Task created successfully: {result}")
                self.results["task_creation"] = True
                return True
            else:
                print(f"❌ Task creation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Task creation test failed: {e}")
            self.results["errors"].append(f"Task creation error: {e}")
            return False

    def run_full_test(self) -> Dict[str, Any]:
        """Run all tests and return results"""
        print("🚀 Starting Darbot Agent Engine E2E Test...")
        print("=" * 50)
        
        # Test backend health
        self.test_backend_health()
        
        # Test frontend health
        self.test_frontend_health()
        
        # Test API connectivity
        self.test_api_connectivity()
        
        # Test task creation
        self.test_task_creation()
        
        # Generate summary
        total_tests = 4
        passed_tests = sum([
            self.results["backend_health"],
            self.results["frontend_health"],
            self.results["api_connectivity"], 
            self.results["task_creation"]
        ])
        
        print("\n" + "=" * 50)
        print("🎯 TEST SUMMARY")
        print("=" * 50)
        print(f"✅ Backend Health: {'PASS' if self.results['backend_health'] else 'FAIL'}")
        print(f"✅ Frontend Health: {'PASS' if self.results['frontend_health'] else 'FAIL'}")
        print(f"✅ API Connectivity: {'PASS' if self.results['api_connectivity'] else 'FAIL'}")
        print(f"✅ Task Creation: {'PASS' if self.results['task_creation'] else 'FAIL'}")
        print(f"\n📊 Overall: {passed_tests}/{total_tests} tests passed")
        
        if self.results["errors"]:
            print(f"\n❌ Errors encountered: {len(self.results['errors'])}")
            for error in self.results["errors"]:
                print(f"   • {error}")
        
        # Overall status
        overall_success = passed_tests == total_tests
        print(f"\n🏁 Overall Status: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
        
        return {
            "success": overall_success,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": self.results
        }

if __name__ == "__main__":
    tester = DarbotE2ETest()
    result = tester.run_full_test()
    
    # Exit with appropriate code
    exit(0 if result["success"] else 1)
