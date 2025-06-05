#!/usr/bin/env python3
"""
Focused Production Task Creation Validator
Tests task creation functionality specifically for production Azure services
with comprehensive audit logging and error analysis.
"""

import json
import logging
import os
import requests
import time
import uuid
from datetime import datetime
from typing import Dict, Any

# Set up audit logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('task_creation_audit.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class TaskCreationAuditor:
    """Focused validator for task creation with production Azure services."""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.session_id = f"audit-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        self.audit_log = []
        
    def audit_event(self, event_type: str, details: Dict[str, Any]):
        """Log audit event with timestamp."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "session_id": self.session_id,
            "details": details
        }
        self.audit_log.append(event)
        logger.info(f"AUDIT: {event_type} - {json.dumps(details, indent=2)}")
        
    def check_azure_config(self) -> Dict[str, Any]:
        """Check Azure configuration status."""
        logger.info("🔍 Auditing Azure configuration...")
        
        azure_configs = {
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", ""),
            "AZURE_AI_PROJECT_ENDPOINT": os.getenv("AZURE_AI_PROJECT_ENDPOINT", ""),
            "APPLICATIONINSIGHTS_CONNECTION_STRING": os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", ""),
            "COSMOSDB_ENDPOINT": os.getenv("COSMOSDB_ENDPOINT", ""),
            "USE_LOCAL_MEMORY": os.getenv("USE_LOCAL_MEMORY", "true")
        }
        
        config_analysis = {}
        production_ready = True
        
        for key, value in azure_configs.items():
            is_mock = not value or value.startswith("mock") or value.startswith("00000000") or value.startswith("https://mock")
            is_production = value and not is_mock and key != "USE_LOCAL_MEMORY"
            
            config_analysis[key] = {
                "value": value[:50] + "..." if len(value) > 50 else value,
                "configured": bool(value),
                "is_production": is_production,
                "is_mock": is_mock
            }
            
            if key != "USE_LOCAL_MEMORY" and not is_production:
                production_ready = False
                
        config_analysis["overall_production_ready"] = production_ready
        
        self.audit_event("AZURE_CONFIG_AUDIT", config_analysis)
        
        return config_analysis
        
    def test_health_endpoints(self) -> Dict[str, Any]:
        """Test all health endpoints and analyze responses."""
        logger.info("🏥 Testing health endpoints...")
        
        health_results = {}
        
        # Test main health endpoint
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            end_time = time.time()
            
            health_results["basic_health"] = {
                "status_code": response.status_code,
                "response_time_ms": (end_time - start_time) * 1000,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
            
        except Exception as e:
            health_results["basic_health"] = {
                "error": str(e),
                "success": False
            }
            
        # Test API health endpoint
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/health", timeout=15)
            end_time = time.time()
            
            health_results["api_health"] = {
                "status_code": response.status_code,
                "response_time_ms": (end_time - start_time) * 1000,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
            
        except Exception as e:
            health_results["api_health"] = {
                "error": str(e),
                "success": False
            }
            
        self.audit_event("HEALTH_ENDPOINTS_TEST", health_results)
        
        return health_results
        
    def test_task_creation_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive test of task creation functionality."""
        logger.info("🚀 Testing task creation with comprehensive analysis...")
        
        test_cases = [
            {
                "name": "simple_task",
                "description": "Create a simple project plan for organizing a team meeting"
            },
            {
                "name": "complex_business_task", 
                "description": "Develop a comprehensive go-to-market strategy for a new SaaS product targeting enterprise customers, including competitive analysis, pricing model, sales enablement materials, and 90-day launch timeline"
            },
            {
                "name": "technical_task",
                "description": "Design and implement a microservices architecture for a scalable e-commerce platform with automated deployment pipelines"
            }
        ]
        
        task_results = {}
        
        for test_case in test_cases:
            logger.info(f"📋 Testing: {test_case['name']}")
            
            task_data = {
                "session_id": f"{self.session_id}-{test_case['name']}",
                "description": test_case["description"]
            }
            
            try:
                start_time = time.time()
                
                response = requests.post(
                    f"{self.backend_url}/api/input_task",
                    json=task_data,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "TaskCreationAuditor/1.0"
                    },
                    timeout=30
                )
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                result = {
                    "status_code": response.status_code,
                    "processing_time_seconds": processing_time,
                    "response_size_bytes": len(response.content),
                    "success": response.status_code == 200
                }
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        result["response_data"] = response_data
                        result["plan_id"] = response_data.get("plan_id")
                        result["returned_session_id"] = response_data.get("session_id")
                        
                        # Test plan retrieval if successful
                        plan_result = self.test_plan_retrieval(response_data.get("session_id"))
                        result["plan_retrieval"] = plan_result
                        
                    except json.JSONDecodeError as e:
                        result["json_error"] = str(e)
                        result["raw_response"] = response.text
                else:
                    result["error_response"] = response.text
                    try:
                        error_data = response.json()
                        result["error_data"] = error_data
                    except:
                        pass
                        
                task_results[test_case["name"]] = result
                
            except requests.exceptions.Timeout:
                task_results[test_case["name"]] = {
                    "error": "Request timeout after 30 seconds",
                    "success": False
                }
                
            except Exception as e:
                task_results[test_case["name"]] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "success": False
                }
                
        self.audit_event("TASK_CREATION_COMPREHENSIVE_TEST", task_results)
        
        return task_results
        
    def test_plan_retrieval(self, session_id: str) -> Dict[str, Any]:
        """Test plan retrieval for a given session."""
        if not session_id:
            return {"error": "No session ID provided"}
            
        try:
            # Wait briefly for plan processing
            time.sleep(1)
            
            response = requests.get(
                f"{self.backend_url}/api/plans",
                params={"session_id": session_id},
                timeout=10
            )
            
            result = {
                "status_code": response.status_code,
                "success": response.status_code == 200
            }
            
            if response.status_code == 200:
                plans_data = response.json()
                result["plans_count"] = len(plans_data)
                result["plans_data"] = plans_data
            else:
                result["error_response"] = response.text
                
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
            
    def test_backend_errors_analysis(self) -> Dict[str, Any]:
        """Analyze backend error patterns and system status."""
        logger.info("🔍 Analyzing backend error patterns...")
        
        # Test various endpoints to understand system status
        test_endpoints = [
            "/",
            "/docs",
            "/health",
            "/api/health",
            "/api/health/ai",
            "/api/plans",
            "/api/sessions"
        ]
        
        endpoint_results = {}
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                endpoint_results[endpoint] = {
                    "status_code": response.status_code,
                    "response_size": len(response.content),
                    "content_type": response.headers.get("content-type", ""),
                    "accessible": response.status_code < 500
                }
                
            except Exception as e:
                endpoint_results[endpoint] = {
                    "error": str(e),
                    "accessible": False
                }
                
        self.audit_event("BACKEND_ERROR_ANALYSIS", endpoint_results)
        
        return endpoint_results
        
    def generate_final_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        logger.info("📊 Generating final audit report...")
        
        report = {
            "audit_metadata": {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "total_audit_events": len(self.audit_log)
            },
            "audit_events": self.audit_log,
            "summary": {
                "azure_config_production_ready": False,
                "health_endpoints_working": False,
                "task_creation_working": False,
                "overall_assessment": "NEEDS_INVESTIGATION"
            }
        }
        
        # Analyze audit events for summary
        for event in self.audit_log:
            event_type = event["event_type"]
            details = event["details"]
            
            if event_type == "AZURE_CONFIG_AUDIT":
                report["summary"]["azure_config_production_ready"] = details.get("overall_production_ready", False)
                
            elif event_type == "HEALTH_ENDPOINTS_TEST":
                api_health = details.get("api_health", {})
                report["summary"]["health_endpoints_working"] = api_health.get("success", False)
                
            elif event_type == "TASK_CREATION_COMPREHENSIVE_TEST":
                # Check if any task creation succeeded
                any_success = any(
                    result.get("success", False) 
                    for result in details.values()
                )
                report["summary"]["task_creation_working"] = any_success
                
        # Determine overall assessment
        if report["summary"]["task_creation_working"]:
            report["summary"]["overall_assessment"] = "WORKING"
        elif report["summary"]["health_endpoints_working"]:
            report["summary"]["overall_assessment"] = "PARTIAL_WORKING"
        else:
            report["summary"]["overall_assessment"] = "NEEDS_INVESTIGATION"
            
        # Save report
        report_filename = f"task_creation_audit_report_{self.session_id}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📄 Audit report saved: {report_filename}")
        
        return report
        
    def run_full_audit(self) -> Dict[str, Any]:
        """Run complete audit of task creation functionality."""
        logger.info("🎯 Starting comprehensive task creation audit...")
        logger.info(f"🔢 Session ID: {self.session_id}")
        
        # Step 1: Check Azure configuration
        azure_config = self.check_azure_config()
        
        # Step 2: Test health endpoints
        health_results = self.test_health_endpoints()
        
        # Step 3: Analyze backend error patterns
        error_analysis = self.test_backend_errors_analysis()
        
        # Step 4: Test task creation comprehensively
        task_results = self.test_task_creation_comprehensive()
        
        # Step 5: Generate final report
        final_report = self.generate_final_audit_report()
        
        # Print summary
        print("\n" + "="*70)
        print("TASK CREATION AUDIT SUMMARY")
        print("="*70)
        print(f"Session ID: {self.session_id}")
        print(f"Azure Config Production Ready: {final_report['summary']['azure_config_production_ready']}")
        print(f"Health Endpoints Working: {final_report['summary']['health_endpoints_working']}")
        print(f"Task Creation Working: {final_report['summary']['task_creation_working']}")
        print(f"Overall Assessment: {final_report['summary']['overall_assessment']}")
        print(f"Total Audit Events: {len(self.audit_log)}")
        print("="*70)
        
        return final_report

def main():
    """Main function."""
    # Set up environment for production testing
    os.system("source /home/runner/work/Darbot-Agent-Engine/Darbot-Agent-Engine/setup_production_env.sh")
    
    auditor = TaskCreationAuditor()
    
    try:
        report = auditor.run_full_audit()
        
        if report["summary"]["task_creation_working"]:
            print("✅ Task creation is working with production Azure services!")
            return 0
        else:
            print("❌ Task creation needs investigation.")
            print("📄 Check the audit log and report for detailed analysis.")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Audit failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())