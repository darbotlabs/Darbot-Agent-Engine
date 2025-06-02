# Thought into existence by Darbot
# Task submission test helper
import asyncio
import aiohttp
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_task_submission():
    """Test task submission flow end-to-end"""
    # Step 1: Submit a task via the frontend proxy
    frontend_url = "http://localhost:3000"
    backend_url = "http://localhost:8001"
    
    logging.info(f"Starting end-to-end task submission test")
    
    async with aiohttp.ClientSession() as session:
        # First check if servers are up
        try:
            async with session.get(f"{backend_url}/health", timeout=5) as response:
                if response.status == 200:
                    logging.info(f"Backend server health check: OK")
                else:
                    logging.error(f"Backend server health check failed: {response.status}")
        except Exception as e:
            logging.error(f"Backend server health check error: {str(e)}")
        
        # Step 1: Submit the task
        task_data = {
            "prompt": "Create a project plan for website redesign",
            "agent_type": "PlannerAgent",
            "model": "gpt-35-turbo"
        }
        
        logging.info("Step 1: Submitting task...")        try:
            async with session.post(
                f"{frontend_url}/api/plans", 
                json=task_data,
                timeout=30
            ) as response:
                status = response.status
                if status == 200 or status == 201:
                    data = await response.json()
                    logging.info(f"Task submission successful: {json.dumps(data, indent=2)}")
                    plan_id = data.get('plan_id')
                    session_id = data.get('session_id')
                    if not plan_id or not session_id:
                        logging.error("No plan ID or session ID returned in response")
                        return False
                    logging.info(f"Created plan with ID: {plan_id}, session ID: {session_id}")
                else:
                    text = await response.text()
                    logging.error(f"Task submission failed: {status} - {text}")
                    return False
        except Exception as e:
            logging.error(f"Task submission exception: {str(e)}")
            return False
        
        # Step 2: Verify the task was created by fetching plans
        logging.info("Step 2: Verifying task creation by fetching plan details...")
        try:
            async with session.get(
                f"{frontend_url}/api/plans/{session_id}",
                timeout=30
            ) as response:
                status = response.status
                if status == 200:
                    data = await response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        # Look for our session ID
                        matching_plans = [p for p in data if p.get('session_id') == session_id]
                        if matching_plans:
                            logging.info(f"Found plan: {matching_plans[0].get('id')} with status: {matching_plans[0].get('overall_status')}")
                            return True
                        else:
                            logging.error("Plan not found in response")
                            return False
                    else:
                        logging.error("No plans returned or unexpected response format")
                        return False
                else:
                    text = await response.text()
                    logging.error(f"Failed to fetch plans: {status} - {text}")
                    return False
        except Exception as e:
            logging.error(f"Error fetching plans: {str(e)}")
            return False

async def main():
    success = await test_task_submission()
    if success:
        logging.info("✅ End-to-end task submission test passed")
    else:
        logging.error("❌ End-to-end task submission test failed")

if __name__ == "__main__":
    asyncio.run(main())
