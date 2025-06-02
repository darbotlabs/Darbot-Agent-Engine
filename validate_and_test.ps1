# Thought into existence by Darbot
# PowerShell script to start Darbot Agent Engine, validate fixes with Playwright, and then kill servers

# Define the paths
$backendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\backend"
$frontendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\frontend"
$pythonPath = "d:\0GH_PROD\Darbot-Agent-Engine\src"

# Set environment variables
$env:PYTHONPATH = $pythonPath

# Force local storage mode for testing
$env:USE_LOCAL_STORAGE = "true"

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
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app_kernel:app --host 0.0.0.0 --port 8001 --reload" -WorkingDirectory $backendPath -PassThru -NoNewWindow

# Wait for the backend server to start
Write-Host "Waiting for backend server to start..."
Start-Sleep -Seconds 5

# Start the frontend server
Write-Host "Starting frontend server..."
$frontendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn frontend_server:app --host 127.0.0.1 --port 3000 --reload" -WorkingDirectory $frontendPath -PassThru -NoNewWindow

# Wait for the frontend server to start
Write-Host "Waiting for frontend server to start..."
Start-Sleep -Seconds 5

# Check if we have Node.js installed
try {
    $nodeVersion = node -v
    Write-Host "Node.js version: $nodeVersion"
    
    # Check if Playwright is installed
    try {
        $playwrightModule = npm list playwright
        if (-not $playwrightModule) {
            Write-Host "Installing Playwright..."
            npm install playwright
        }
        
        # Run the Playwright test script
        Write-Host "Running UI validation tests with Playwright..."
        node validate_ui_fixes.js
    }
    catch {
        Write-Host "Error running Playwright: $_"
        Write-Host "Installing Playwright..."
        npm install playwright
        
        # Try running the test again
        Write-Host "Retrying UI validation tests..."
        node validate_ui_fixes.js
    }
}
catch {
    Write-Host "Node.js is not installed or not in the PATH. Skipping Playwright validation."
    Write-Host "Please install Node.js or manually run: node validate_ui_fixes.js"
}

# Ask user if they want to keep the servers running
$keepRunning = Read-Host -Prompt "Do you want to keep the servers running? (y/n)"

if ($keepRunning -ne "y") {
    # Stop the servers
    Write-Host "Stopping servers..."
    if ($backendProcess) { 
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue 
    }
    if ($frontendProcess) { 
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue 
    }
    
    # Kill any remaining processes on the ports
    if (Test-PortInUse 8001) {
        $connections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
    
    if (Test-PortInUse 3000) {
        $connections = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host "Servers stopped."
} else {
    Write-Host "Servers will continue running."
    Write-Host "Press Ctrl+C to exit and stop the servers when done."
    
    # Keep the script running to maintain the servers
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        # This will run when Ctrl+C is pressed
        Write-Host "Stopping servers..."
        if ($backendProcess) { 
            Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue 
        }
        if ($frontendProcess) { 
            Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue 
        }
        
        # Kill any remaining processes on the ports
        if (Test-PortInUse 8001) {
            $connections = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue
            foreach ($conn in $connections) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
        
        if (Test-PortInUse 3000) {
            $connections = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
            foreach ($conn in $connections) {
                Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
