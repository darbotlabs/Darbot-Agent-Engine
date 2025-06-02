#!/usr/bin/env python3
"""
Darbot Agent Engine Server Startup Script
Thought into existence by Darbot

This script provides centralized server management for the Darbot Agent Engine backend.
It ensures consistent port usage and proper server lifecycle management.
"""

import logging
import os
import signal
import sys
from pathlib import Path

import uvicorn
from backend.app_config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DarbotServerManager:
    """Manages the Darbot Agent Engine server lifecycle."""
    
    def __init__(self):
        self.host = config.BACKEND_HOST
        self.port = config.BACKEND_PORT
        self.server = None
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        if self.server:
            self.server.should_exit = True
        sys.exit(0)
    
    def check_port_available(self) -> bool:
        """Check if the configured port is available."""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                return True
        except OSError:
            return False
    
    def start_server(self, reload: bool = False):
        """Start the Darbot Agent Engine server."""
        logger.info("="*60)
        logger.info("🤖 DARBOT AGENT ENGINE - STARTING SERVER")
        logger.info("="*60)
        
        # Check port availability
        if not self.check_port_available():
            logger.error(f"❌ Port {self.port} is already in use!")
            logger.info("💡 Use 'netstat -ano | findstr :8001' to find the process")
            return False
        
        # Server configuration
        logger.info(f"🌐 Host: {self.host}")
        logger.info(f"🔌 Port: {self.port}")
        logger.info(f"🔄 Reload: {reload}")
        logger.info(f"📁 Working Directory: {os.getcwd()}")
        
        try:
            # Start the server
            logger.info("🚀 Starting FastAPI server...")
            uvicorn.run(
                "app_kernel:app",
                host=self.host,
                port=self.port,
                reload=reload,
                log_level="info",
                access_log=True,
                loop="asyncio"
            )
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
        
        return True

def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Darbot Agent Engine Server")
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=config.BACKEND_PORT,
        help=f"Port to run the server on (default: {config.BACKEND_PORT})"
    )
    parser.add_argument(
        "--host", 
        default=config.BACKEND_HOST,
        help=f"Host to bind the server to (default: {config.BACKEND_HOST})"
    )
    
    args = parser.parse_args()
    
    # Override config if command line arguments provided
    config.BACKEND_HOST = args.host
    config.BACKEND_PORT = args.port
    
    # Start the server
    server_manager = DarbotServerManager()
    success = server_manager.start_server(reload=args.reload)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
