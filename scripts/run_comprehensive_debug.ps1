# Thought into existence by Darbot
# PowerShell script to run all debug tests and validate fixes

# Set environment variables
$env:USE_LOCAL_STORAGE = "true"
$env:PYTHONPATH = "d:\0GH_PROD\Darbot-Agent-Engine\src"

# Add mock environment variables for testing
$env:AZURE_OPENAI_ENDPOINT = "https://mockendpoint.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY = "mock-key-for-testing-only"
$env:AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-35-turbo"
$env:AZURE_OPENAI_API_VERSION = "2023-05-15"
$env:AZURE_AI_PROJECT_NAME = "mockproject"
$env:AZURE_AI_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
$env:AZURE_AI_RESOURCE_GROUP = "mockgroup"

# Paths
$backendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\backend"
$frontendPath = "d:\0GH_PROD\Darbot-Agent-Engine\src\frontend"

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

# Create log directory if it doesn't exist
$logDir = "d:\0GH_PROD\Darbot-Agent-Engine\debug_logs"
if (-not (Test-Path $logDir)) {
    New-Item -Path $logDir -ItemType Directory | Out-Null
}

# Timestamp for log files
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

# Start the backend server
Write-Host "Starting backend server..."
$backendLog = Join-Path $logDir "backend_$timestamp.log"
$backendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn app_kernel:app --host 0.0.0.0 --port 8001 --reload" -WorkingDirectory $backendPath -PassThru -NoNewWindow -RedirectStandardOutput $backendLog -RedirectStandardError "$backendLog.err"

# Wait for the backend server to start
    Write-Host "Waiting for backend server to start..."
    Start-Sleep -Seconds 15

    # Start the frontend server
    Write-Host "Starting frontend server..."
    $frontendLog = Join-Path $logDir "frontend_$timestamp.log"
    $frontendProcess = Start-Process -FilePath "python" -ArgumentList "-m uvicorn frontend_server:app --host 127.0.0.1 --port 3000 --reload" -WorkingDirectory $frontendPath -PassThru -NoNewWindow -RedirectStandardOutput $frontendLog -RedirectStandardError "$frontendLog.err"

    # Wait for the frontend server to start
    Write-Host "Waiting for frontend server to start..."
    Start-Sleep -Seconds 15

# Run direct backend API tests
Write-Host "Running backend API tests..."
$backendApiLog = Join-Path $logDir "backend_api_test_$timestamp.log"
Start-Process -FilePath "python" -ArgumentList "debug_backend_api.py" -WorkingDirectory "d:\0GH_PROD\Darbot-Agent-Engine" -NoNewWindow -Wait -RedirectStandardOutput $backendApiLog -RedirectStandardError "$backendApiLog.err"

# Run frontend proxy tests
Write-Host "Running frontend proxy tests..."
$frontendProxyLog = Join-Path $logDir "frontend_proxy_test_$timestamp.log"
Start-Process -FilePath "python" -ArgumentList "debug_frontend_proxy.py" -WorkingDirectory "d:\0GH_PROD\Darbot-Agent-Engine" -NoNewWindow -Wait -RedirectStandardOutput $frontendProxyLog -RedirectStandardError "$frontendProxyLog.err"

# Check if we have Node.js installed for running Playwright tests
try {
    $nodeVersion = node -v
    Write-Host "Node.js version: $nodeVersion"
    
    # Check if Playwright is installed
    $playwrightCheck = npm list playwright 2>$null
    if (-not $playwrightCheck -or $playwrightCheck -like "*empty*") {
        Write-Host "Installing Playwright..."
        npm install playwright
    }
    
    # Run UI validation test
    Write-Host "Running UI validation tests with Playwright..."
    $playwrightLog = Join-Path $logDir "playwright_test_$timestamp.log"
    Start-Process -FilePath "node" -ArgumentList "validate_ui_fixes.js" -WorkingDirectory "d:\0GH_PROD\Darbot-Agent-Engine" -NoNewWindow -Wait -RedirectStandardOutput $playwrightLog -RedirectStandardError "$playwrightLog.err"
}
catch {
    Write-Host "Node.js is not installed or not in the PATH. Skipping Playwright validation."
}

# Create a summary report
$summaryFile = Join-Path $logDir "debug_summary_$timestamp.txt"
"Debug Summary Report - $timestamp" | Out-File $summaryFile
"===================================" | Out-File $summaryFile -Append
"" | Out-File $summaryFile -Append

# Check backend logs
$backendErrors = Select-String -Path "$backendLog.err" -Pattern "error|exception|fail" -CaseSensitive:$false
"Backend Errors: $($backendErrors.Count)" | Out-File $summaryFile -Append
if ($backendErrors.Count -gt 0) {
    "Top 10 backend errors:" | Out-File $summaryFile -Append
    $backendErrors | Select-Object -First 10 | ForEach-Object { $_.Line } | Out-File $summaryFile -Append
}

# Check frontend logs
$frontendErrors = Select-String -Path "$frontendLog.err" -Pattern "error|exception|fail" -CaseSensitive:$false
"Frontend Errors: $($frontendErrors.Count)" | Out-File $summaryFile -Append
if ($frontendErrors.Count -gt 0) {
    "Top 10 frontend errors:" | Out-File $summaryFile -Append
    $frontendErrors | Select-Object -First 10 | ForEach-Object { $_.Line } | Out-File $summaryFile -Append
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

Write-Host "Debug summary saved to: $summaryFile"
