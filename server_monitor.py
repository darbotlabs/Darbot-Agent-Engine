# Thought into existence by Darbot
# Real-time backend and frontend server monitor
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

class ServerMonitor:
    """Monitor backend and frontend servers for health and errors"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8001"
        self.frontend_url = "http://localhost:3000"
        self.check_interval = 5  # seconds
        self.session = None
        self.healthy = {
            "backend": False,
            "frontend": False
        }
        self.last_status = {}
        
    async def initialize(self):
        """Initialize the HTTP client session"""
        self.session = aiohttp.ClientSession()
        
    async def close(self):
        """Close the HTTP client session"""
        if self.session:
            await self.session.close()
    
    async def check_backend_health(self):
        """Check if the backend server is healthy"""
        try:
            async with self.session.get(f"{self.backend_url}/health", timeout=2) as response:
                if response.status == 200:
                    if not self.healthy["backend"]:
                        logging.info("✅ Backend is now healthy")
                    self.healthy["backend"] = True
                    return True
                else:
                    if self.healthy["backend"]:
                        logging.error(f"❌ Backend is no longer healthy - status: {response.status}")
                    self.healthy["backend"] = False
                    return False
        except Exception as e:
            if self.healthy["backend"]:
                logging.error(f"❌ Backend health check failed: {str(e)}")
            self.healthy["backend"] = False
            return False
    
    async def check_frontend_health(self):
        """Check if the frontend server is healthy"""
        try:
            async with self.session.get(f"{self.frontend_url}/debug", timeout=2) as response:
                if response.status == 200:
                    if not self.healthy["frontend"]:
                        logging.info("✅ Frontend is now healthy")
                    self.healthy["frontend"] = True
                    return True
                else:
                    if self.healthy["frontend"]:
                        logging.error(f"❌ Frontend is no longer healthy - status: {response.status}")
                    self.healthy["frontend"] = False
                    return False
        except Exception as e:
            if self.healthy["frontend"]:
                logging.error(f"❌ Frontend health check failed: {str(e)}")
            self.healthy["frontend"] = False
            return False
    
    async def test_api_call(self):
        """Test a simple API call through the frontend proxy"""
        if not (self.healthy["backend"] and self.healthy["frontend"]):
            return False
            
        try:
            # Use the frontend proxy to access the server-info endpoint
            async with self.session.get(f"{self.frontend_url}/api/server-info", timeout=5) as response:
                status = response.status
                if status == 200:
                    data = await response.json()
                    current_status = json.dumps(data)
                    
                    # Only log if status changed
                    if self.last_status.get("server-info") != current_status:
                        logging.info(f"API Call Success - Server Info: {data}")
                        self.last_status["server-info"] = current_status
                    
                    return True
                else:
                    text = await response.text()
                    logging.error(f"API Call Failed - Status: {status}, Response: {text[:200]}")
                    return False
        except Exception as e:
            logging.error(f"API Call Error: {str(e)}")
            return False
    
    async def run(self):
        """Run the monitor continuously"""
        await self.initialize()
        
        try:
            while True:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Checking servers...", end="\r")
                
                backend_healthy = await self.check_backend_health()
                frontend_healthy = await self.check_frontend_health()
                
                if backend_healthy and frontend_healthy:
                    await self.test_api_call()
                
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            logging.info("Monitor stopped")
        except Exception as e:
            logging.error(f"Monitor error: {str(e)}")
        finally:
            await self.close()

async def main():
    monitor = ServerMonitor()
    await monitor.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Monitor stopped by user")
