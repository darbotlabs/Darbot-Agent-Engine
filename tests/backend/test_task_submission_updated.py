# Thought into existence by Darbot
# Task submission test helper (Updated version with fallback logic)
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
    # Set up URLs for testing
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
        
        logging.info("Step 1: Submitting task...")
        
        try:
            # Try direct backend first
            logging.info("Trying direct backend submission...")
            async with session.post(
                f"{backend_url}/api/plans", 
                json=task_data,
                timeout=30
            ) as response:
                status = response.status
                if status == 200 or status == 201:
                    data = await response.json()
                    logging.info(f"Task submission successful via backend: {json.dumps(data, indent=2)}")
                    plan_id = data.get('plan_id')
                    session_id = data.get('session_id')
                    if not plan_id or not session_id:
                        logging.error("No plan ID or session ID returned in response")
                        
                        # Try frontend proxy as fallback
                        logging.info("Trying frontend proxy submission as fallback...")
                        async with session.post(
                            f"{frontend_url}/api/plans", 
                            json=task_data,
                            timeout=30
                        ) as proxy_response:
                            proxy_status = proxy_response.status
                            if proxy_status == 200 or proxy_status == 201:
                                proxy_data = await proxy_response.json()
                                logging.info(f"Task submission successful via proxy: {json.dumps(proxy_data, indent=2)}")
                                plan_id = proxy_data.get('plan_id')
                                session_id = proxy_data.get('session_id')
                                if not plan_id or not session_id:
                                    logging.error("No plan ID or session ID returned in proxy response")
                                    return False
                            else:
                                proxy_text = await proxy_response.text()
                                logging.error(f"Task submission failed via proxy: {proxy_status} - {proxy_text}")
                                return False
                    
                    logging.info(f"Created plan with ID: {plan_id}, session ID: {session_id}")
                else:
                    text = await response.text()
                    logging.error(f"Task submission failed via backend: {status} - {text}")
                    
                    # Try frontend proxy as fallback
                    logging.info("Trying frontend proxy submission as fallback...")
                    async with session.post(
                        f"{frontend_url}/api/plans", 
                        json=task_data,
                        timeout=30
                    ) as proxy_response:
                        proxy_status = proxy_response.status
                        if proxy_status == 200 or proxy_status == 201:
                            proxy_data = await proxy_response.json()
                            logging.info(f"Task submission successful via proxy: {json.dumps(proxy_data, indent=2)}")
                            plan_id = proxy_data.get('plan_id')
                            session_id = proxy_data.get('session_id')
                            if not plan_id or not session_id:
                                logging.error("No plan ID or session ID returned in proxy response")
                                return False
                            logging.info(f"Created plan with ID: {plan_id}, session ID: {session_id}")
                        else:
                            proxy_text = await proxy_response.text()
                            logging.error(f"Task submission failed via proxy: {proxy_status} - {proxy_text}")
                            return False
        except Exception as e:
            logging.error(f"Task submission exception: {str(e)}")
            return False
        
        # Step 2: Verify the task was created by fetching plan details
        logging.info("Step 2: Verifying task creation by fetching plan details...")
        try:
            # Wait a bit for the plan to be processed
            await asyncio.sleep(2)
            
            async with session.get(
                f"{frontend_url}/api/plans/{session_id}",
                timeout=30
            ) as response:
                status = response.status
                if status == 200:
                    data = await response.json()
                    logging.info(f"Plan details: {json.dumps(data, indent=2)}")
                    plan_status = data.get('overall_status')
                    logging.info(f"Plan status: {plan_status}")
                    return True
                else:
                    text = await response.text()
                    logging.error(f"Failed to fetch plan details: {status} - {text}")
                    return False
        except Exception as e:
            logging.error(f"Error fetching plan details: {str(e)}")
            return False

async def main():
    success = await test_task_submission()
    if success:
        logging.info("✅ End-to-end task submission test passed")
    else:
        logging.error("❌ End-to-end task submission test failed")

if __name__ == "__main__":
    asyncio.run(main())
