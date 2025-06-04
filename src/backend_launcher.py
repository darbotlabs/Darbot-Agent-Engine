"""
Backend module entry point for proper imports
Thought into existence by Darbot
"""
import sys
import os
import argparse

# Add necessary paths to Python's path
current_dir = os.path.abspath(os.path.dirname(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.insert(0, current_dir)  # Add src directory
sys.path.insert(0, backend_dir)  # Add backend directory

# Parse command line arguments
parser = argparse.ArgumentParser(description="Darbot Agent Engine Backend Server")
parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
args = parser.parse_args()

# Now import and run the app with uvicorn
import uvicorn
# Use direct import of the app from app_kernel
from backend.app_kernel import app

if __name__ == "__main__":
    print(f"Starting Darbot Agent Engine Backend on {args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
