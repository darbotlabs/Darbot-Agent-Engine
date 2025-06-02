import os
import subprocess
import sys
import platform
import json
import httpx
import logging
from urllib.parse import urljoin

import uvicorn
from fastapi.logger import logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
from fastapi import FastAPI, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    JSONResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles

# Resolve wwwroot path relative to this script
WWWROOT_PATH = os.path.join(os.path.dirname(__file__), "wwwroot")

# Debugging information
print(f"Current Working Directory: {os.getcwd()}")
print(f"Absolute path to wwwroot: {WWWROOT_PATH}")
if not os.path.exists(WWWROOT_PATH):
    raise FileNotFoundError(f"wwwroot directory not found at path: {WWWROOT_PATH}")
print(f"Files in wwwroot: {os.listdir(WWWROOT_PATH)}")

app = FastAPI()

import html


@app.get("/config.js", response_class=PlainTextResponse)
def get_config():
    backend_url = html.escape(os.getenv("BACKEND_API_URL", "http://localhost:8001"))
    auth_enabled = html.escape(os.getenv("AUTH_ENABLED", "True"))
    # Thought into existence by Darbot - Using the frontend server itself as the API endpoint
    return f"""
        // Using empty string to enable proxy approach
        const BACKEND_API_URL = "";  
        const AUTH_ENABLED = "{auth_enabled}";
        console.log("Config loaded - using proxy approach for API calls");
        """


# Redirect root to app.html
@app.get("/")
async def index_redirect():
    return RedirectResponse(url="/app.html?v=home")


# API Proxy route to avoid CORS issues
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def api_proxy(path: str, request: Request):
    backend_url = os.getenv("BACKEND_API_URL", "http://localhost:8001")
    target_url = urljoin(f"{backend_url}/api/", path)
    
    # Get the request body if it exists
    body = await request.body()
    body_str = body.decode() if body else None
    
    # Forwarded headers, but filter out host
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    
    method = request.method
    
    # Special handling for OPTIONS requests for CORS preflight
    if method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "*",
            },
        )
    
    # Log the complete request details for debugging
    query_params = request.query_params._dict if hasattr(request.query_params, '_dict') else dict(request.query_params)
    logging.info(f"Proxying {method} request to: {target_url}")
    logging.info(f"Query params: {query_params}")
    logging.info(f"Headers: {headers}")
    if body_str and len(body_str) < 1000:  # Only log if not too large
        logging.info(f"Request body: {body_str}")
    
    try:
        # Use httpx for the API request with increased timeout
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Combine URL with query parameters
            target_url_with_params = target_url
            if query_params:
                # Reconstruct query string
                query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
                if "?" not in target_url:
                    target_url_with_params = f"{target_url}?{query_string}"
                else:
                    target_url_with_params = f"{target_url}&{query_string}"
            
            # Make the request to the backend
            response = await client.request(
                method=method,
                url=target_url_with_params,
                headers=headers,
                content=body,
            )
            
            logging.info(f"Proxy response: {response.status_code}")
            
            # Forward the response headers and content
            content = response.content
            response_headers = dict(response.headers)
            
            # Try to parse as JSON first
            try:
                content_json = response.json()
                logging.info(f"JSON response: {content_json[:200] if isinstance(content_json, str) else content_json}")
                return JSONResponse(
                    content=content_json,
                    status_code=response.status_code,
                    headers=response_headers,
                )
            except Exception as json_error:
                logging.info(f"Not JSON response, returning raw content. Error: {json_error}")
                # If not JSON, return raw content with correct headers
                return Response(
                    content=content,
                    status_code=response.status_code,
                    headers=response_headers,
                )
    except Exception as e:
        logging.error(f"Proxy error: {str(e)}", exc_info=True)
        return JSONResponse(
            content={"error": f"Proxy error: {str(e)}"},
            status_code=500,
        )


# Mount static files
app.mount("/", StaticFiles(directory=WWWROOT_PATH, html=True), name="static")


# Debugging route
@app.get("/debug")
async def debug_route():
    return {
        "message": "Frontend debug route working",
        "wwwroot_path": WWWROOT_PATH,
        "files": os.listdir(WWWROOT_PATH),
    }


# Catch-all route for SPA
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    print(f"Requested path: {full_path}")
    app_html_path = os.path.join(WWWROOT_PATH, "app.html")

    if os.path.exists(app_html_path):
        return FileResponse(app_html_path)
    else:
        return HTMLResponse(
            content=f"app.html not found. Current path: {app_html_path}",
            status_code=404,
        )


def open_edge_browser(url):
    """Open Microsoft Edge browser with the specified URL."""
    # Thought into existence by Darbot
    try:
        if platform.system() == 'Windows':
            subprocess.Popen(['start', 'msedge', url], shell=True)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', '-a', 'Microsoft Edge', url])
        elif platform.system() == 'Linux':
            subprocess.Popen(['microsoft-edge', url])
        else:
            print(f"Unsupported operating system: {platform.system()}")
            return False
        return True
    except Exception as e:
        print(f"Error opening Microsoft Edge: {e}")
        return False

if __name__ == "__main__":
    # Start the server
    host = "127.0.0.1"
    port = 3000
    print(f"Starting server at http://{host}:{port}")
    
    # Open Microsoft Edge after a short delay to ensure the server is running
    import threading
    import time
    
    def open_browser():
        time.sleep(2)  # Wait for server to start
        url = f"http://{host}:{port}"
        print(f"Opening Microsoft Edge with URL: {url}")
        if not open_edge_browser(url):
            print("Failed to open Edge browser automatically. Please open it manually.")
    
    threading.Thread(target=open_browser).start()
    
    # Run the server
    uvicorn.run(app, host=host, port=port)
