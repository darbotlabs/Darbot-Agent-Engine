# Darbot Agent Engine - Azure Resource Launcher (from .env)
param (
    [Parameter(Mandatory = $false)]
    [int]$BackendPort = 8001,
    [Parameter(Mandatory = $false)]
    [int]$FrontendPort = 3000,
    [Parameter(Mandatory = $false)]
    [switch]$EnableAuth = $true,
    [Parameter(Mandatory = $false)]
    [switch]$SkipBrowserOpen = $false,
    [Parameter(Mandatory = $false)]
    # Default to production .env
    [string]$EnvFile = "g:\Github\darbotlabs\Darbot-Agent-Engine\src\backend\.env"
)

function Load-DotEnv {
    param([string]$Path)
    if (Test-Path $Path) {
        Get-Content $Path | ForEach-Object {
            if ($_ -match '^\s*#') { return }
            if ($_ -match '^\s*$') { return }
            if ($_ -match '^\s*([^=]+)\s*=\s*(.*)\s*$') {
                $key = $matches[1].Trim()
                $val = $matches[2].Trim()
                $val = $val -replace '^"|"$', '' # Remove quotes
                [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
            }
        }
    } else {
        Write-Host "❌ .env file not found at $Path" -ForegroundColor Red
        exit 1
    }
}

function Check-RequiredEnvVars {
    param([string[]]$RequiredVars)
    $missing = @()
    foreach ($var in $RequiredVars) {
        if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
            $missing += $var
        }
    }
    if ($missing.Count -gt 0) {
        Write-Host "❌ Missing required production environment variables:" -ForegroundColor Red
        $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
        exit 1
    }
}

# Warn if using local dev .env
if ($EnvFile -eq "g:\Github\darbotlabs\Darbot-Agent-Engine\.env") {
    Write-Host "⚠️  WARNING: You are using the local development .env file. For production, use src/backend/.env or a secure production config!" -ForegroundColor Yellow
}

Write-Host "🚀 Starting Darbot Agent Engine with Azure Resources from .env..." -ForegroundColor Cyan

# Load .env variables
Load-DotEnv -Path $EnvFile

# Check for required production variables
$requiredVars = @(
    "COSMOSDB_ENDPOINT",
    "COSMOSDB_DATABASE",
    "COSMOSDB_CONTAINER",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_MODEL_NAME",
    "AZURE_AI_SUBSCRIPTION_ID",
    "AZURE_AI_RESOURCE_GROUP",
    "AZURE_AI_RESOURCE_NAME"
)
Check-RequiredEnvVars -RequiredVars $requiredVars

# Override ports and auth if specified
[System.Environment]::SetEnvironmentVariable("BACKEND_PORT", "$BackendPort", "Process")
[System.Environment]::SetEnvironmentVariable("FRONTEND_PORT", "$FrontendPort", "Process")
[System.Environment]::SetEnvironmentVariable("AUTH_ENABLED", $EnableAuth.ToString(), "Process")
[System.Environment]::SetEnvironmentVariable("BACKEND_API_URL", "http://localhost:$BackendPort", "Process")

# Set PYTHONPATH
$rootPath = "g:\Github\darbotlabs\Darbot-Agent-Engine"
[System.Environment]::SetEnvironmentVariable("PYTHONPATH", "$rootPath\src", "Process")

# Azure CLI login check
Write-Host "`n🔐 Checking Azure CLI authentication..." -ForegroundColor Yellow
try {
    $azLogin = az account show 2>$null | ConvertFrom-Json
    if (-not $azLogin) {
        Write-Host "❌ You are not logged in to Azure CLI." -ForegroundColor Red
        Write-Host "Please run 'az login' first." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Logged in as: $($azLogin.user.name)" -ForegroundColor Green
    Write-Host "   Subscription: $($azLogin.name)" -ForegroundColor Green
    Write-Host "   Tenant: $($azLogin.tenantId)" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not available or not logged in." -ForegroundColor Red
    Write-Host "Please install Azure CLI and run 'az login'." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n☁️ Environment variables loaded from .env" -ForegroundColor Green

# Create debug logs directory
$debugFolder = "$rootPath\debug_logs"
if (-not (Test-Path $debugFolder)) {
    New-Item -ItemType Directory -Path $debugFolder -Force | Out-Null
}
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backendLogFile = "$debugFolder\backend_azure_$timestamp.log"
$frontendLogFile = "$debugFolder\frontend_azure_$timestamp.log"

Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow

# Backend dependencies
$requirementsFile = "$rootPath\src\backend\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing backend Python dependencies..." -ForegroundColor Gray
    try {
        uv pip install -q -r $requirementsFile --prerelease=allow
        Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ UV not available, falling back to pip..." -ForegroundColor Yellow
        pip install -q -r $requirementsFile --pre
        Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
    }
}

# Frontend dependencies
$frontendRequirementsFile = "$rootPath\src\frontend\requirements.txt"
if (Test-Path $frontendRequirementsFile) {
    Write-Host "Installing frontend Python dependencies..." -ForegroundColor Gray
    try {
        uv pip install -q -r $frontendRequirementsFile --prerelease=allow
        Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green    } catch {
        Write-Host "⚠️ UV not available, falling back to pip..." -ForegroundColor Yellow
        pip install -q -r $frontendRequirementsFile --pre
        Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green
    }
}

Write-Host "`n🚀 Starting servers..." -ForegroundColor Yellow

# Start backend server
$backendCommand = @"
cd $rootPath\src\backend;
Write-Host '🔧 Backend Server - Azure Resource Mode' -ForegroundColor Cyan;
Write-Host 'Environment: .env (Azure Resources)' -ForegroundColor Green;
Write-Host 'Authentication: $env:AUTH_ENABLED' -ForegroundColor Green;
Write-Host 'CosmosDB: $env:COSMOSDB_ENDPOINT' -ForegroundColor Green;
Write-Host '';
try { 
    uvicorn backend.app_kernel:app --port $BackendPort --reload | Tee-Object -FilePath '$backendLogFile'
} catch {
    Write-Host 'Error starting backend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$backendLogFile';
    Read-Host 'Press Enter to close this window';
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

Write-Host "Waiting for backend server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 7

# Start frontend server
$frontendCommand = @"
`$env:BACKEND_API_URL = 'http://localhost:$BackendPort';
`$env:AUTH_ENABLED = '$env:AUTH_ENABLED';
cd $rootPath\src\frontend;
Write-Host '🌐 Frontend Server - Azure Resource Mode' -ForegroundColor Cyan;
Write-Host 'Backend API: http://localhost:$BackendPort' -ForegroundColor Green;
Write-Host 'Authentication: $env:AUTH_ENABLED' -ForegroundColor Green;
Write-Host '';
try {
    uvicorn frontend_server:app --port $FrontendPort --reload | Tee-Object -FilePath '$frontendLogFile'
} catch {
    Write-Host 'Error starting frontend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$frontendLogFile';
    Read-Host 'Press Enter to close this window';
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

Write-Host "Waiting for frontend server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

if (-not $SkipBrowserOpen) {
    Write-Host "Opening application in default browser..." -ForegroundColor Green
    Start-Process "http://localhost:$FrontendPort"
}

Write-Host "
══════════════════════════════════════════════════════════════════════════════════
                    🎯 Darbot Agent Engine - Azure Resource Mode                    
══════════════════════════════════════════════════════════════════════════════════
  🌐 Frontend:  http://localhost:$FrontendPort
  🔧 Backend:   http://localhost:$BackendPort       
  📚 API Docs:  http://localhost:$BackendPort/docs

  💡 Tips:
    - All data is stored in Azure CosmosDB (not local memory)
    - Authentication uses your Azure AD credentials
    - Check browser console for API request activity

  🛑 To stop: Close both PowerShell windows when finished
══════════════════════════════════════════════════════════════════════════════════
" -ForegroundColor Cyan

Write-Host "✅ Darbot Agent Engine is now running with Azure resources from .env!" -ForegroundColor Green
Write-Host "The application should open automatically in your browser." -ForegroundColor Yellow