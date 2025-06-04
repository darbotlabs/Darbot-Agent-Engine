# Thought into existence by Darbot
# PowerShell script to start Darbot Agent Engine with Microsoft Edge

# Define the paths
$backendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\backend"
$frontendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\frontend"
$pythonPath = "d:\0GH_PROD\Darbot-Agent-Engine\src"

# Set environment variables
$env:PYTHONPATH = $pythonPath

# Function to check if a port is in use
function Test-PortInUse {
    param($port)
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    return $null -ne $connections
}

# Kill any existing processes on ports 8001 and 3000
if (Test-PortInUse 8001) {
    Write-Host "Stopping processes on port 8001..."
    $connections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

if (Test-PortInUse 3000) {
    Write-Host "Stopping processes on port 3000..."
    $connections = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

# Start the backend server
Write-Host "Starting backend server..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn app_kernel:app --host 0.0.0.0 --port 8001" -WorkingDirectory $backendPath -NoNewWindow

# Wait for the backend server to start
Write-Host "Waiting for backend server to start..."
Start-Sleep -Seconds 5

# Start the frontend server
Write-Host "Starting frontend server..."
Start-Process -FilePath "python" -ArgumentList "-m uvicorn frontend_server:app --host 127.0.0.1 --port 3000" -WorkingDirectory $frontendPath -NoNewWindow

# Wait for the frontend server to start
Write-Host "Waiting for frontend server to start..."
Start-Sleep -Seconds 5

# Launch Microsoft Edge with the application
Write-Host "Launching Microsoft Edge..."
Start-Process "msedge" -ArgumentList "http://localhost:3000"

Write-Host "Darbot Agent Engine started successfully with Microsoft Edge."
Write-Host "Press Ctrl+C to exit and stop the servers."

# Keep the script running to maintain the servers
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    # This will run when Ctrl+C is pressed
    Write-Host "Stopping servers..."
    if (Test-PortInUse 8001) {
        Stop-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess -Force
    }
    if (Test-PortInUse 3000) {
        Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force
    }
}
