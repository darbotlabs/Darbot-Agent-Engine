# Thought into existence by Darbot
# Frontend proxy troubleshooting script
import asyncio
import aiohttp
import json
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_frontend_proxy():
    """Test the frontend server's proxy functionality"""
    frontend_url = "http://localhost:3000"
    session_id = f"test_session_{int(time.time())}"
    
    logging.info(f"Testing frontend proxy with session ID: {session_id}")
    
    async with aiohttp.ClientSession() as session:
        # Test proxy for server info
        logging.info("Testing proxy for server info...")
        async with session.get(f"{frontend_url}/api/server-info") as response:
            status = response.status
            if status == 200:
                data = await response.json()
                logging.info(f"Server info via proxy: {json.dumps(data, indent=2)}")
            else:
                text = await response.text()
                logging.error(f"Server info proxy error: {status} - {text}")
                # Add detailed error headers
                logging.error(f"Response headers: {response.headers}")
        
        # Test proxy for task submission
        task_data = {
            "session_id": session_id,
            "description": "Test task via frontend proxy"
        }
        
        logging.info("Testing task submission through proxy...")
        try:
            async with session.post(
                f"{frontend_url}/api/input_task", 
                json=task_data,
                timeout=30
            ) as response:
                status = response.status
                if status == 200:
                    data = await response.json()
                    logging.info(f"Task submission via proxy: {json.dumps(data, indent=2)}")
                else:
                    text = await response.text()
                    logging.error(f"Task submission proxy error: {status} - {text}")
                    # Add detailed error headers
                    logging.error(f"Response headers: {response.headers}")
        except asyncio.TimeoutError:
            logging.error("Task submission proxy request timed out")
        except Exception as e:
            logging.error(f"Task submission proxy exception: {str(e)}")
        
        # Test proxy for plans endpoint
        logging.info("Testing plans endpoint through proxy...")
        try:
            async with session.get(
                f"{frontend_url}/api/plans?session_id={session_id}",
                timeout=30
            ) as response:
                status = response.status
                if status == 200:
                    data = await response.json()
                    logging.info(f"Plans endpoint via proxy: {json.dumps(data, indent=2)}")
                else:
                    text = await response.text()
                    logging.error(f"Plans endpoint proxy error: {status} - {text}")
        except Exception as e:
            logging.error(f"Plans endpoint proxy exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_frontend_proxy())
