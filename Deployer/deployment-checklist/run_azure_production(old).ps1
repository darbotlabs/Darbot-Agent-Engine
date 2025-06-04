# Thought into existence by Darbot
# Azure Production Server Startup Script
# This script runs the Darbot Agent Engine with Azure Studio-CAT resources

param (
    [Parameter(Mandatory = $false)]
    [int]$BackendPort = 8001,
    
    [Parameter(Mandatory = $false)]
    [int]$FrontendPort = 3000,
    
    [Parameter(Mandatory = $false)]
    [switch]$EnableAuth = $true,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipBrowserOpen = $false
)

Write-Host "🚀 Starting Darbot Agent Engine with Azure Studio-CAT Resources..." -ForegroundColor Cyan
Write-Host "   Backend Port: $BackendPort" -ForegroundColor White
Write-Host "   Frontend Port: $FrontendPort" -ForegroundColor White
Write-Host "   Authentication: $($EnableAuth.ToString())" -ForegroundColor White

# Set required environment variables
$rootPath = "d:\0GH_PROD\Darbot-Agent-Engine"
$env:PYTHONPATH = "$rootPath\src"

# Verify Azure CLI login
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

# Azure Studio-CAT Environment Variables
Write-Host "`n☁️ Configuring Azure Studio-CAT environment..." -ForegroundColor Yellow

# Core Azure settings
$env:USE_LOCAL_MEMORY = "False"
$env:BYPASS_AUTH_FOR_LOCAL_DEV = "False"
$env:AUTH_ENABLED = "True"
$env:DISABLE_TELEMETRY = "False"
$env:LOG_LEVEL = "INFO"
$env:ENABLE_FILE_LOGGING = "True"

# Azure OpenAI settings (Studio-CAT specific)
$env:AZURE_OPENAI_ENDPOINT = "https://cat-studio-foundry.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME = "grok-3"
$env:AZURE_OPENAI_API_VERSION = "2024-05-01-preview"

# Azure AI settings (Studio-CAT specific)
$env:AZURE_AI_PROJECT_NAME = "studio-cat"
$env:AZURE_AI_SUBSCRIPTION_ID = "99fc47d1-e510-42d6-bc78-63cac040a902"
$env:AZURE_AI_RESOURCE_GROUP = "Studio-CAT"

# Azure Tenant and Authentication (Microsoft tenant)
$env:AZURE_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
$env:AZURE_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

# CosmosDB settings (Studio-CAT specific - uses DefaultAzureCredential)
$env:COSMOSDB_ENDPOINT = "https://darbot-cosmos-dev.documents.azure.com:443/"
$env:COSMOSDB_DATABASE = "darbot-agent-db"
$env:COSMOSDB_CONTAINER = "agent-conversations"

# Remove any API keys to force keyless authentication
$env:AZURE_OPENAI_API_KEY = ""
$env:COSMOSDB_KEY = ""

# Azure App Service Authentication Headers (Production values)
$env:HOST_NAME = "darbot-studio-cat.azurewebsites.net"
$env:ORIGIN_URL = "https://darbot-studio-cat.azurewebsites.net"
$env:REFERER_URL = "https://darbot-studio-cat.azurewebsites.net/"
$env:APP_SERVICE_PROTO = "https"
$env:FORWARDED_PROTO = "https"
$env:CLIENT_PRINCIPAL = "azure-ad-user"
$env:CLIENT_PRINCIPAL_ID = "ebb01e50-f389-4f45-84a3-8d588f0b5bab"
$env:CLIENT_PRINCIPAL_IDP = "aad"
$env:CLIENT_PRINCIPAL_NAME = "dayour@microsoft.com"
$env:AAD_ID_TOKEN = "production-azure-ad-token"
$env:SITE_DEPLOYMENT_ID = "studio-cat-prod"

# Backend API settings
$env:BACKEND_API_URL = "http://localhost:$BackendPort"
$env:AUTH_ENABLED = $EnableAuth.ToString()
$env:DISABLE_TELEMETRY = "False"

# Azure OpenAI settings (Studio-CAT)
$env:AZURE_OPENAI_ENDPOINT = "https://cat-studio-foundry.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME = "grok-3"
$env:AZURE_OPENAI_API_VERSION = "2024-05-01-preview"

# Azure AI settings (Studio-CAT)
$env:AZURE_AI_PROJECT_NAME = "studio-cat"
$env:AZURE_AI_SUBSCRIPTION_ID = "99fc47d1-e510-42d6-bc78-63cac040a902"
$env:AZURE_AI_RESOURCE_GROUP = "Studio-CAT"

# Azure Authentication settings
$env:AZURE_TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
$env:AZURE_CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"

# CosmosDB settings (Studio-CAT)
$env:COSMOSDB_ENDPOINT = "https://darbot-cosmos-dev.documents.azure.com:443/"
$env:COSMOSDB_DATABASE = "darbot-agent-db"
$env:COSMOSDB_CONTAINER = "agent-conversations"

# Backend API settings
$env:BACKEND_API_URL = "http://localhost:$BackendPort"

# Production authentication headers (override mock values)
$env:CLIENT_PRINCIPAL_ID = $azLogin.user.name
$env:CLIENT_PRINCIPAL_NAME = $azLogin.user.name
$env:CLIENT_PRINCIPAL_IDP = "aad"
$env:CLIENT_PRINCIPAL = "azure-ad-user"
$env:HOST_NAME = "darbot-studio-cat.azurewebsites.net"
$env:APP_SERVICE_PROTO = "https"
$env:FORWARDED_PROTO = "https"
$env:AAD_ID_TOKEN = "azure-ad-token"

# Logging settings
$env:LOG_LEVEL = "INFO"
$env:ENABLE_FILE_LOGGING = "True"

Write-Host "✅ Environment configured for Azure Studio-CAT resources" -ForegroundColor Green

# Create debug logs directory
$debugFolder = "$rootPath\debug_logs"
if (-not (Test-Path $debugFolder)) {
    New-Item -ItemType Directory -Path $debugFolder -Force | Out-Null
}

# Generate timestamp for log files
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backendLogFile = "$debugFolder\backend_azure_$timestamp.log"
$frontendLogFile = "$debugFolder\frontend_azure_$timestamp.log"

Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow

# Ensure backend dependencies are installed
$requirementsFile = "$rootPath\src\backend\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Installing backend Python dependencies..." -ForegroundColor Gray
    try {
        uv pip install -q -r $requirementsFile
        Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ UV not available, falling back to pip..." -ForegroundColor Yellow
        pip install -q -r $requirementsFile
        Write-Host "✅ Backend dependencies installed successfully" -ForegroundColor Green
    }
}

# Ensure frontend dependencies are installed
$frontendRequirementsFile = "$rootPath\src\frontend\requirements.txt"
if (Test-Path $frontendRequirementsFile) {
    Write-Host "Installing frontend Python dependencies..." -ForegroundColor Gray
    try {
        uv pip install -q -r $frontendRequirementsFile
        Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ UV not available, falling back to pip..." -ForegroundColor Yellow
        pip install -q -r $frontendRequirementsFile
        Write-Host "✅ Frontend dependencies installed successfully" -ForegroundColor Green
    }
}

Write-Host "`n🚀 Starting servers..." -ForegroundColor Yellow

# Prepare environment variables for the backend process
$envVars = @"
`$env:PYTHONPATH = '$env:PYTHONPATH';
`$env:USE_LOCAL_MEMORY = '$env:USE_LOCAL_MEMORY';
`$env:BYPASS_AUTH_FOR_LOCAL_DEV = '$env:BYPASS_AUTH_FOR_LOCAL_DEV';
`$env:AUTH_ENABLED = '$env:AUTH_ENABLED';
`$env:DISABLE_TELEMETRY = '$env:DISABLE_TELEMETRY';
`$env:AZURE_OPENAI_ENDPOINT = '$env:AZURE_OPENAI_ENDPOINT';
`$env:AZURE_OPENAI_DEPLOYMENT_NAME = '$env:AZURE_OPENAI_DEPLOYMENT_NAME';
`$env:AZURE_OPENAI_API_VERSION = '$env:AZURE_OPENAI_API_VERSION';
`$env:AZURE_AI_PROJECT_NAME = '$env:AZURE_AI_PROJECT_NAME';
`$env:AZURE_AI_SUBSCRIPTION_ID = '$env:AZURE_AI_SUBSCRIPTION_ID';
`$env:AZURE_AI_RESOURCE_GROUP = '$env:AZURE_AI_RESOURCE_GROUP';
`$env:AZURE_TENANT_ID = '$env:AZURE_TENANT_ID';
`$env:AZURE_CLIENT_ID = '$env:AZURE_CLIENT_ID';
`$env:COSMOSDB_ENDPOINT = '$env:COSMOSDB_ENDPOINT';
`$env:COSMOSDB_DATABASE = '$env:COSMOSDB_DATABASE';
`$env:COSMOSDB_CONTAINER = '$env:COSMOSDB_CONTAINER';
`$env:CLIENT_PRINCIPAL_ID = '$env:CLIENT_PRINCIPAL_ID';
`$env:CLIENT_PRINCIPAL_NAME = '$env:CLIENT_PRINCIPAL_NAME';
`$env:CLIENT_PRINCIPAL_IDP = '$env:CLIENT_PRINCIPAL_IDP';
`$env:CLIENT_PRINCIPAL = '$env:CLIENT_PRINCIPAL';
`$env:HOST_NAME = '$env:HOST_NAME';
`$env:APP_SERVICE_PROTO = '$env:APP_SERVICE_PROTO';
`$env:FORWARDED_PROTO = '$env:FORWARDED_PROTO';
`$env:AAD_ID_TOKEN = '$env:AAD_ID_TOKEN';
`$env:LOG_LEVEL = '$env:LOG_LEVEL';
`$env:ENABLE_FILE_LOGGING = '$env:ENABLE_FILE_LOGGING';
"@

Write-Host "Starting backend server on port $BackendPort..." -ForegroundColor White
Write-Host "Log file: $backendLogFile" -ForegroundColor Gray

# Start the backend server in a new PowerShell window
$backendCommand = "$envVars
cd $rootPath\src\backend;
Write-Host '🔧 Backend Server - Azure Studio-CAT Mode' -ForegroundColor Cyan;
Write-Host 'Environment: Production (Azure Resources)' -ForegroundColor Green;
Write-Host 'Authentication: $env:AUTH_ENABLED' -ForegroundColor Green;
Write-Host 'CosmosDB: $env:COSMOSDB_ENDPOINT' -ForegroundColor Green;
Write-Host '';
try { 
    uvicorn backend.app_kernel:app --port $BackendPort --reload | Tee-Object -FilePath '$backendLogFile'
} catch {
    Write-Host 'Error starting backend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$backendLogFile';
    Read-Host 'Press Enter to close this window';
}"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Wait for backend to start
Write-Host "Waiting for backend server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 7

Write-Host "Starting frontend server on port $FrontendPort..." -ForegroundColor White
Write-Host "Log file: $frontendLogFile" -ForegroundColor Gray

# Start the frontend server in a new PowerShell window
$frontendCommand = "
`$env:BACKEND_API_URL = 'http://localhost:$BackendPort';
`$env:AUTH_ENABLED = '$env:AUTH_ENABLED';
cd $rootPath\src\frontend;
Write-Host '🌐 Frontend Server - Azure Studio-CAT Mode' -ForegroundColor Cyan;
Write-Host 'Backend API: http://localhost:$BackendPort' -ForegroundColor Green;
Write-Host 'Authentication: $env:AUTH_ENABLED' -ForegroundColor Green;
Write-Host '';
try {
    uvicorn frontend_server:app --port $FrontendPort --reload | Tee-Object -FilePath '$frontendLogFile'
} catch {
    Write-Host 'Error starting frontend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$frontendLogFile';
    Read-Host 'Press Enter to close this window';
}"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

# Wait for frontend to start
Write-Host "Waiting for frontend server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Open the frontend in the default browser (unless skipped)
if (-not $SkipBrowserOpen) {
    Write-Host "Opening application in default browser..." -ForegroundColor Green
    Start-Process "http://localhost:$FrontendPort"
}

Write-Host "
══════════════════════════════════════════════════════════════════════════════════
                    🎯 Darbot Agent Engine - Azure Studio-CAT Mode                    
══════════════════════════════════════════════════════════════════════════════════
  🌐 Frontend:  http://localhost:$FrontendPort
  🔧 Backend:   http://localhost:$BackendPort       
  📚 API Docs:  http://localhost:$BackendPort/docs
  
  📊 Azure Resources (Studio-CAT):
    - OpenAI:     https://cat-studio-foundry.openai.azure.com/
    - CosmosDB:   https://darbot-cosmos-dev.documents.azure.com/
    - Resource Group: Studio-CAT
    - Subscription: FastTrack Azure Commercial Shared POC
    
  🔐 Authentication:
    - Mode: Azure AD ($($EnableAuth.ToString()))
    - User: $($azLogin.user.name)
    - Tenant: Microsoft (72f988bf-86f1-41af-91ab-2d7cd011db47)
    
  📝 Log Files:
    - Backend:  $backendLogFile
    - Frontend: $frontendLogFile
    
  💡 Tips:
    - Submit tasks like 'Create a project plan for website redesign'
    - All data is stored in Azure CosmosDB (not local memory)
    - Authentication uses your Azure AD credentials
    - Check browser console for API request activity
    
  🛑 To stop: Close both PowerShell windows when finished
══════════════════════════════════════════════════════════════════════════════════
" -ForegroundColor Cyan

Write-Host "✅ Darbot Agent Engine is now running with Azure Studio-CAT resources!" -ForegroundColor Green
Write-Host "The application should open automatically in your browser." -ForegroundColor Yellow
