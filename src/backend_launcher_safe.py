"""
Health-only backend launcher for reliable health checks
This launcher uses a minimal FastAPI app with only health endpoints
to ensure the launcher health check never hangs.
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
parser = argparse.ArgumentParser(description="Darbot Agent Engine Backend Health Server")
parser.add_argument("--host", default="0.0.0.0", help="Host address to bind to")
parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
parser.add_argument("--health-only", action="store_true", help="Start health-only server")
args = parser.parse_args()

# Import uvicorn
import uvicorn

if args.health_only:
    # Use the health-only app for reliable health checks
    from backend.health_only_app import health_app as app
    print(f"Starting Darbot Agent Engine Health Server on {args.host}:{args.port}")
else:
    # Try to use the full app, fall back to health-only if it fails
    try:
        from backend.app_kernel import app
        print(f"Starting Darbot Agent Engine Backend on {args.host}:{args.port}")
    except Exception as e:
        print(f"Failed to load full backend, using health-only mode: {e}")
        from backend.health_only_app import health_app as app
        print(f"Starting Darbot Agent Engine Health Server on {args.host}:{args.port}")

if __name__ == "__main__":
    uvicorn.run(app, host=args.host, port=args.port)