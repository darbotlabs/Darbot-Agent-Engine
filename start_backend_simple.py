# Thought into existence by Darbot
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Add src to Python path
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import and run the backend
from src.backend.app_kernel import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting Darbot Backend Server...")
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)
