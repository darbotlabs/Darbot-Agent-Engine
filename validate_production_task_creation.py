#!/usr/bin/env python3
"""
Production Task Creation Validation Script
Validates that task creation works properly with production Azure services
and captures detailed audit logs for analysis.
"""

import asyncio
import json
import logging
import os
import requests
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production_validation_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionTaskCreationValidator:
    """Validates task creation against production Azure services with audit logging."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.session_id = f"prod-validation-{uuid.uuid4().hex[:8]}"
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "tests": {},
            "audit_events": [],
            "azure_service_status": {},
            "overall_success": False,
            "errors": []
        }
        
    def log_audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event for tracking."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": self.session_id,
            "details": details
        }
        self.validation_results["audit_events"].append(audit_entry)
        logger.info(f"AUDIT: {event_type} - {details}")
        
    def check_azure_service_configuration(self) -> bool:
        """Check if Azure services are properly configured."""
        logger.info("🔍 Checking Azure service configuration...")
        
        required_configs = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT_NAME", 
            "AZURE_AI_PROJECT_ENDPOINT",
            "APPLICATIONINSIGHTS_CONNECTION_STRING"
        ]
        
        config_status = {}
        all_configured = True
        
        for config in required_configs:
            value = os.getenv(config)
            is_configured = bool(value and not value.startswith("mock") and not value.startswith("00000000"))
            config_status[config] = {
                "configured": is_configured,
                "value_type": "production" if is_configured else "mock/missing"
            }
            if not is_configured:
                all_configured = False
                
        self.validation_results["azure_service_status"] = config_status
        
        self.log_audit_event("AZURE_CONFIG_CHECK", {
            "all_configured": all_configured,
            "config_details": config_status
        })
        
        if all_configured:
            logger.info("✅ All Azure services configured for production")
        else:
            logger.warning("⚠️ Some Azure services using mock/default values")
            
        return all_configured
        
    def test_backend_health_detailed(self) -> bool:
        """Test backend health with detailed service status."""
        logger.info("🏥 Testing backend health with service details...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=15)
            
            if response.status_code == 200:
                health_data = response.json()
                
                self.log_audit_event("BACKEND_HEALTH_CHECK", {
                    "status": "success",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "health_data": health_data
                })
                
                logger.info(f"✅ Backend health: {health_data}")
                self.validation_results["tests"]["backend_health"] = True
                return True
            else:
                self.log_audit_event("BACKEND_HEALTH_CHECK", {
                    "status": "failed",
                    "status_code": response.status_code,
                    "response": response.text
                })
                logger.error(f"❌ Backend health failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_audit_event("BACKEND_HEALTH_CHECK", {
                "status": "error",
                "error": str(e)
            })
            logger.error(f"❌ Backend health check error: {e}")
            return False
            
    def test_production_task_creation(self) -> bool:
        """Test task creation with production Azure services."""
        logger.info("🚀 Testing production task creation...")
        
        # Use a realistic business task that would exercise Azure AI capabilities
        task_data = {
            "session_id": self.session_id,
            "description": "Create a comprehensive marketing strategy for launching a new SaaS product targeting small businesses, including market analysis, competitive positioning, pricing strategy, and go-to-market plan with specific deliverables and timelines."
        }
        
        self.log_audit_event("TASK_CREATION_START", {
            "task_description": task_data["description"],
            "session_id": self.session_id
        })
        
        try:
            start_time = time.time()
            
            # Send task creation request
            response = requests.post(
                f"{self.backend_url}/api/input_task",
                json=task_data,
                headers={
                    "Content-Type": "application/json",
                    "X-Test-User": "production-validation-user"  # Test header
                },
                timeout=60  # Increased timeout for production services
            )
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.log_audit_event("TASK_CREATION_RESPONSE", {
                "status_code": response.status_code,
                "processing_time_seconds": processing_time,
                "response_size_bytes": len(response.content),
                "response_headers": dict(response.headers)
            })
            
            if response.status_code == 200:
                response_data = response.json()
                
                self.log_audit_event("TASK_CREATION_SUCCESS", {
                    "plan_id": response_data.get("plan_id"),
                    "session_id": response_data.get("session_id"),
                    "status": response_data.get("status"),
                    "processing_time": processing_time
                })
                
                logger.info(f"✅ Task creation successful!")
                logger.info(f"📊 Response: {response_data}")
                logger.info(f"⏱️ Processing time: {processing_time:.2f}s")
                
                # Test plan retrieval
                return self.test_plan_retrieval(response_data.get("plan_id"))
                
            else:
                self.log_audit_event("TASK_CREATION_FAILED", {
                    "status_code": response.status_code,
                    "error_response": response.text,
                    "processing_time": processing_time
                })
                
                logger.error(f"❌ Task creation failed: {response.status_code}")
                logger.error(f"📄 Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            self.log_audit_event("TASK_CREATION_TIMEOUT", {
                "timeout_seconds": 60,
                "session_id": self.session_id
            })
            logger.error("❌ Task creation timed out after 60 seconds")
            return False
            
        except Exception as e:
            self.log_audit_event("TASK_CREATION_ERROR", {
                "error": str(e),
                "error_type": type(e).__name__
            })
            logger.error(f"❌ Task creation error: {e}")
            return False
            
    def test_plan_retrieval(self, plan_id: Optional[str]) -> bool:
        """Test plan retrieval to validate task processing."""
        if not plan_id:
            logger.warning("⚠️ No plan ID provided, skipping plan retrieval test")
            return True
            
        logger.info(f"📋 Testing plan retrieval for plan ID: {plan_id}")
        
        try:
            # Wait for plan processing
            time.sleep(3)
            
            response = requests.get(
                f"{self.backend_url}/api/plans",
                params={"session_id": self.session_id},
                timeout=10
            )
            
            if response.status_code == 200:
                plans = response.json()
                
                self.log_audit_event("PLAN_RETRIEVAL_SUCCESS", {
                    "plans_count": len(plans),
                    "plan_details": plans
                })
                
                logger.info(f"✅ Retrieved {len(plans)} plans")
                
                if plans:
                    for plan in plans:
                        logger.info(f"📌 Plan ID: {plan.get('id')}")
                        logger.info(f"📝 Goal: {plan.get('initial_goal', 'N/A')}")
                        logger.info(f"📊 Status: {plan.get('overall_status', 'N/A')}")
                        logger.info(f"🔢 Total Steps: {plan.get('total_steps', 0)}")
                        
                self.validation_results["tests"]["plan_retrieval"] = True
                return True
            else:
                self.log_audit_event("PLAN_RETRIEVAL_FAILED", {
                    "status_code": response.status_code,
                    "response": response.text
                })
                logger.error(f"❌ Plan retrieval failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_audit_event("PLAN_RETRIEVAL_ERROR", {
                "error": str(e)
            })
            logger.error(f"❌ Plan retrieval error: {e}")
            return False
            
    def test_azure_ai_connectivity(self) -> bool:
        """Test Azure AI services connectivity through health endpoint."""
        logger.info("🤖 Testing Azure AI services connectivity...")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health/ai", timeout=15)
            
            if response.status_code == 200:
                ai_health = response.json()
                
                self.log_audit_event("AZURE_AI_CONNECTIVITY", {
                    "status": "success",
                    "ai_health_data": ai_health
                })
                
                logger.info(f"✅ Azure AI services connected: {ai_health}")
                self.validation_results["tests"]["azure_ai_connectivity"] = True
                return True
            else:
                self.log_audit_event("AZURE_AI_CONNECTIVITY", {
                    "status": "failed",
                    "status_code": response.status_code,
                    "response": response.text
                })
                logger.warning(f"⚠️ Azure AI health check returned: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_audit_event("AZURE_AI_CONNECTIVITY", {
                "status": "error", 
                "error": str(e)
            })
            logger.warning(f"⚠️ Azure AI connectivity test failed: {e}")
            return False
            
    def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        logger.info("📊 Generating audit report...")
        
        # Calculate overall success
        test_results = self.validation_results["tests"]
        required_tests = ["backend_health", "plan_retrieval"]
        
        self.validation_results["overall_success"] = all(
            test_results.get(test, False) for test in required_tests
        )
        
        # Save audit report
        report_filename = f"audit_report_{self.session_id}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.validation_results, f, indent=2)
            
        logger.info(f"📄 Audit report saved to: {report_filename}")
        
        return self.validation_results
        
    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete production validation suite."""
        logger.info("🎯 Starting production task creation validation...")
        logger.info(f"🔢 Session ID: {self.session_id}")
        
        self.log_audit_event("VALIDATION_START", {
            "session_id": self.session_id,
            "backend_url": self.backend_url
        })
        
        # Step 1: Check Azure configuration
        azure_configured = self.check_azure_service_configuration()
        
        # Step 2: Test backend health
        health_ok = self.test_backend_health_detailed()
        
        # Step 3: Test Azure AI connectivity
        ai_ok = self.test_azure_ai_connectivity()
        
        # Step 4: Test task creation (main test)
        if health_ok:
            task_ok = self.test_production_task_creation()
            self.validation_results["tests"]["task_creation"] = task_ok
        else:
            logger.error("❌ Skipping task creation due to health check failure")
            self.validation_results["tests"]["task_creation"] = False
            
        # Generate final report
        report = self.generate_audit_report()
        
        self.log_audit_event("VALIDATION_COMPLETE", {
            "overall_success": report["overall_success"],
            "total_tests": len(report["tests"]),
            "successful_tests": sum(1 for result in report["tests"].values() if result),
            "azure_configured": azure_configured
        })
        
        if report["overall_success"]:
            logger.info("🎉 Production validation PASSED!")
        else:
            logger.error("❌ Production validation FAILED!")
            
        return report

async def main():
    """Main function to run the validation."""
    validator = ProductionTaskCreationValidator()
    
    try:
        report = await validator.run_full_validation()
        
        print("\n" + "="*60)
        print("PRODUCTION VALIDATION SUMMARY")
        print("="*60)
        print(f"Session ID: {report['session_id']}")
        print(f"Overall Success: {report['overall_success']}")
        print(f"Azure Services Configured: {all(s.get('configured', False) for s in report['azure_service_status'].values())}")
        print(f"Total Audit Events: {len(report['audit_events'])}")
        
        print("\nTest Results:")
        for test_name, result in report['tests'].items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
            
        if report['errors']:
            print(f"\nErrors Encountered: {len(report['errors'])}")
            for error in report['errors']:
                print(f"  - {error}")
        
        print(f"\nDetailed audit log: production_validation_audit.log")
        print(f"JSON report: audit_report_{report['session_id']}.json")
        print("="*60)
        
        return 0 if report['overall_success'] else 1
        
    except Exception as e:
        logger.error(f"❌ Validation failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)