# Thought into existence by Darbot
# PowerShell script to start Darbot Agent Engine backend server

# Define the paths
$rootPath = "d:\0GH_PROD\Darbot-Agent-Engine"
$srcPath = "d:\0GH_PROD\Darbot-Agent-Engine\src"

# Check and kill existing process on port 8001 if running
$connections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
foreach ($conn in $connections) {
    Write-Host "Stopping process on port 8001 (PID: $($conn.OwningProcess))..."
    Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
}

# Set environment variables
$env:PYTHONPATH = $srcPath

# Start the backend server with the correct module path
Write-Host "Starting backend server..."
Write-Host "Using PYTHONPATH: $env:PYTHONPATH"
python -m uvicorn backend.app_kernel:app --host 0.0.0.0 --port 8001 --reload
