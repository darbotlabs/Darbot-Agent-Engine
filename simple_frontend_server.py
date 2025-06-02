# Thought into existence by Darbot
# Frontend server with proxy to backend
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import httpx
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Create FastAPI app
app = FastAPI(title="Darbot Frontend Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get backend URL from environment variable
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8002")

# Backend proxy timeout in seconds
PROXY_TIMEOUT = int(os.getenv("PROXY_TIMEOUT", "30"))

# Set up static files
frontend_dir = Path("d:/0GH_PROD/Darbot-Agent-Engine/src/frontend/wwwroot")
app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")
app.mount("/libs", StaticFiles(directory=frontend_dir / "libs"), name="libs")
app.mount("/home", StaticFiles(directory=frontend_dir / "home"), name="home")
app.mount("/task", StaticFiles(directory=frontend_dir / "task"), name="task")

@app.get("/", response_class=HTMLResponse)
def get_root():
    try:
        with open(frontend_dir / "app.html", "r") as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading app.html: {e}")
        return "<html><body><h1>Error loading application</h1></body></html>"

@app.get("/config.js", response_class=PlainTextResponse)
def get_config():
    auth_enabled = os.getenv("AUTH_ENABLED", "False")
    # Using empty string for API endpoint to enable proxy approach
    return f"""
        // Using empty string to enable proxy approach
        const BACKEND_API_URL = "";  
        const AUTH_ENABLED = "{auth_enabled}";
        console.log("Config loaded - using proxy approach for API calls");
    """

@app.get("/utils.js", response_class=PlainTextResponse)
def get_utils():
    with open(frontend_dir / "utils.js", "r") as f:
        return f.read()

@app.get("/app.js", response_class=PlainTextResponse)
def get_app_js():
    with open(frontend_dir / "app.js", "r") as f:
        return f.read()

@app.get("/status", response_class=PlainTextResponse)
async def get_status():
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as client:
            response = await client.get(f"{BACKEND_API_URL}/health")
            elapsed = time.time() - start_time
            return f"Frontend: OK\nBackend: {response.text}\nLatency: {elapsed:.2f}s"
    except Exception as e:
        return f"Frontend: OK\nBackend: Error - {str(e)}\n"

# API proxy to backend
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def api_proxy(request: Request, path: str):
    # Log request details 
    logging.info(f"Proxy request: {request.method} /api/{path}")
    logging.info(f"Headers: {request.headers}")
    
    try:
        # Get the raw body content
        body = await request.body()
        
        # Log body if it's not empty
        if body:
            try:
                body_json = await request.json()
                logging.info(f"Request body: {body_json}")
            except:
                logging.info(f"Request body: [binary content of length {len(body)}]")
        
        # Construct target URL by adding path to backend URL
        target_url = f"{BACKEND_API_URL}/api/{path}"
        logging.info(f"Forwarding request to: {target_url}")
        
        # Forward request headers
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")}
        
        start_time = time.time()
        async with httpx.AsyncClient(timeout=PROXY_TIMEOUT) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=True
            )
            
        elapsed = time.time() - start_time
        logging.info(f"Backend response status: {response.status_code} (in {elapsed:.2f}s)")
        
        # Return response from backend to client
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
    except Exception as e:
        logging.error(f"Error proxying request: {str(e)}")
        return Response(
            content=f'{{"error": "Proxy error: {str(e)}"}}',
            status_code=500,
            media_type="application/json"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000, reload=True)
