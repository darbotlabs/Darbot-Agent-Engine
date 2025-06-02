# Thought into existence by Darbot
# Backend API direct testing script
import asyncio
import aiohttp
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_backend_direct():
    """Test the backend API directly without going through the frontend server"""
    backend_url = "http://localhost:8001"
    session_id = f"test_session_{int(asyncio.get_event_loop().time())}"
    
    logging.info(f"Testing backend direct access with session ID: {session_id}")
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        logging.info("Testing health endpoint...")
        async with session.get(f"{backend_url}/health") as response:
            status = response.status
            text = await response.text()
            logging.info(f"Health endpoint response: {status} - {text}")
        
        # Test server info endpoint
        logging.info("Testing server info endpoint...")
        async with session.get(f"{backend_url}/api/server-info") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                logging.info(f"Server info: {json.dumps(data, indent=2)}")
            else:
                text = await response.text()
                logging.error(f"Server info error: {status} - {text}")
        
        # Test task submission endpoint with and without /api prefix
        task_data = {
            "session_id": session_id,
            "description": "Test task for direct API testing"
        }
        
        # Test with /api prefix
        logging.info("Testing task submission with /api prefix...")
        async with session.post(
            f"{backend_url}/api/input_task", 
            json=task_data
        ) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                logging.info(f"Task submission response: {json.dumps(data, indent=2)}")
            else:
                text = await response.text()
                logging.error(f"Task submission error: {status} - {text}")
        
        # Test without /api prefix (should fail but let's verify)
        logging.info("Testing task submission without /api prefix (expect 404)...")
        async with session.post(
            f"{backend_url}/input_task", 
            json=task_data
        ) as response:
            status = response.status
            text = await response.text()
            logging.info(f"No-prefix endpoint response: {status} - {text}")
        
        # Test plans endpoint
        logging.info("Testing plans endpoint...")
        async with session.get(f"{backend_url}/api/plans?session_id={session_id}") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                logging.info(f"Plans endpoint response: {json.dumps(data, indent=2)}")
            else:
                text = await response.text()
                logging.error(f"Plans endpoint error: {status} - {text}")

if __name__ == "__main__":
    asyncio.run(test_backend_direct())
