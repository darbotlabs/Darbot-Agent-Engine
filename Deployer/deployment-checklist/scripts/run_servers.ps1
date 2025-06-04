# Thought into existence by Darbot
# Comprehensive Script to Run Frontend and Backend Servers with Azure Integration

param (
    [Parameter(Mandatory = $false)]
    [switch]$UseAzure,
    
    [Parameter(Mandatory = $false)]
    [string]$AzureOpenAIEndpoint,
    
    [Parameter(Mandatory = $false)]
    [string]$AzureOpenAIDeploymentName = "gpt-4o",
    
    [Parameter(Mandatory = $false)]
    [string]$AzureOpenAIApiVersion = "2024-05-01-preview",
    
    [Parameter(Mandatory = $false)]
    [string]$AzureSubscriptionId,
    
    [Parameter(Mandatory = $false)]
    [string]$AzureResourceGroup,
    
    [Parameter(Mandatory = $false)]
    [string]$AzureAIProjectName,
    
    [Parameter(Mandatory = $false)]
    [switch]$EnableAuth = $false
)

Write-Host "Starting Darbot Agent Engine Servers..." -ForegroundColor Green

# Set required environment variables
$rootPath = "d:\0GH_PROD\Darbot-Agent-Engine"
$env:PYTHONPATH = "$rootPath\src"

# Configuration based on mode (local mock or Azure)
if ($UseAzure) {
    Write-Host "Using Azure services for development..." -ForegroundColor Blue
    
    # Check for Azure CLI login
    $azLogin = az account show 2>$null
    if (-not $azLogin) {
        Write-Host "You are not logged in to Azure. Please log in first." -ForegroundColor Red
        Write-Host "Run 'az login' to authenticate with Azure." -ForegroundColor Yellow
        exit 1
    }
    
    # Get current Azure subscription if not provided
    if (-not $AzureSubscriptionId) {
        $subInfo = az account show | ConvertFrom-Json
        $AzureSubscriptionId = $subInfo.id
        Write-Host "Using current Azure subscription: $($subInfo.name) ($AzureSubscriptionId)" -ForegroundColor Yellow
    }
    
    # Validate required parameters for Azure mode
    $missingParams = @()
    if (-not $AzureOpenAIEndpoint) { $missingParams += "AzureOpenAIEndpoint" }
    if (-not $AzureResourceGroup) { $missingParams += "AzureResourceGroup" }
    if (-not $AzureAIProjectName) { $missingParams += "AzureAIProjectName" }
    
    if ($missingParams.Count -gt 0) {
        Write-Host "Missing required parameters for Azure mode: $($missingParams -join ', ')" -ForegroundColor Red
        Write-Host "Please provide the missing parameters or use local mode without -UseAzure switch" -ForegroundColor Yellow
        exit 1
    }
    
    # Set Azure configuration
    $env:USE_LOCAL_MEMORY = "False"
    $env:AZURE_OPENAI_ENDPOINT = $AzureOpenAIEndpoint
    $env:AZURE_OPENAI_DEPLOYMENT_NAME = $AzureOpenAIDeploymentName
    $env:AZURE_OPENAI_API_VERSION = $AzureOpenAIApiVersion
    $env:AZURE_AI_SUBSCRIPTION_ID = $AzureSubscriptionId
    $env:AZURE_AI_RESOURCE_GROUP = $AzureResourceGroup
    $env:AZURE_AI_PROJECT_NAME = $AzureAIProjectName
    
    # Get Azure AI Agent Project Connection String - this needs to be created in the Azure AI Studio
    $env:AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = az cognitiveservices account keys list --name $AzureAIProjectName --resource-group $AzureResourceGroup --query primaryKey -o tsv 2>$null
    if (-not $env:AZURE_AI_AGENT_PROJECT_CONNECTION_STRING) {
        Write-Host "Warning: Could not retrieve the Azure AI Agent Project Connection String" -ForegroundColor Yellow
        Write-Host "You may need to set this manually before running the application" -ForegroundColor Yellow
    }
    
    # Use DefaultAzureCredential for authentication
    Write-Host "Using DefaultAzureCredential for authentication to Azure services" -ForegroundColor Green
    
    # CosmosDB settings - will use DefaultAzureCredential
    $cosmosAccount = az cosmosdb list --resource-group $AzureResourceGroup --query "[0].name" -o tsv 2>$null
    if ($cosmosAccount) {
        $env:COSMOSDB_ENDPOINT = "https://$cosmosAccount.documents.azure.com:443/"
        $env:COSMOSDB_DATABASE = "darbot-agent-db"
        $env:COSMOSDB_CONTAINER = "agent-conversations"
        Write-Host "Using CosmosDB account: $cosmosAccount" -ForegroundColor Green
    } else {
        Write-Host "Warning: No CosmosDB account found in resource group $AzureResourceGroup" -ForegroundColor Yellow
        Write-Host "Falling back to local memory storage" -ForegroundColor Yellow
        $env:USE_LOCAL_MEMORY = "True"
    }
} else {
    Write-Host "Using mock services for local development..." -ForegroundColor Blue
    
    # Mock Azure services for local development
    $env:USE_LOCAL_MEMORY = "True"
    $env:AZURE_OPENAI_ENDPOINT = "https://mockendpoint.openai.azure.com/"
    $env:AZURE_OPENAI_API_KEY = "mock-key-for-testing-only"
    $env:AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4o"
    $env:AZURE_OPENAI_API_VERSION = "2024-05-01-preview"
    $env:AZURE_AI_PROJECT_NAME = "mockproject" 
    $env:AZURE_AI_SUBSCRIPTION_ID = "00000000-0000-0000-0000-000000000000"
    $env:AZURE_AI_RESOURCE_GROUP = "mockgroup"
    $env:AZURE_TENANT_ID = "00000000-0000-0000-0000-000000000000"
    $env:AZURE_CLIENT_ID = "00000000-0000-0000-0000-000000000000"
    $env:AZURE_CLIENT_SECRET = "mock-client-secret"
    
    # Mock CosmosDB settings
    $env:COSMOSDB_ENDPOINT = ""
    $env:COSMOSDB_KEY = ""
    $env:COSMOSDB_DATABASE = "darbot-agent-db"
    $env:COSMOSDB_CONTAINER = "agent-conversations"
}

# Configure frontend and authentication
$env:AUTH_ENABLED = $EnableAuth.ToString()
$env:BACKEND_API_URL = "http://localhost:8001"  # Used by proxy

# Create the debug folder if it doesn't exist
$debugFolder = "$rootPath\debug_logs"
if (-not (Test-Path $debugFolder)) {
    New-Item -ItemType Directory -Path $debugFolder -Force | Out-Null
}

# Generate timestamp for log files
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backendLogFile = "$debugFolder\backend_$timestamp.log"
$frontendLogFile = "$debugFolder\frontend_$timestamp.log"

Write-Host "Starting backend server on port 8001..." -ForegroundColor Yellow
Write-Host "Log file: $backendLogFile" -ForegroundColor Gray

# Ensure backend dependencies are installed
$requirementsFile = "$rootPath\src\backend\requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "Ensuring backend Python dependencies are installed..." -ForegroundColor Yellow
    try {
        uv pip install -q -r $requirementsFile
    } catch {
        Write-Host "Falling back to pip..." -ForegroundColor Yellow
        pip install -q -r $requirementsFile
    }
}

# Prepare environment variables for the backend process
$envVars = @"
`$env:PYTHONPATH = '$env:PYTHONPATH';
`$env:AZURE_OPENAI_ENDPOINT = '$env:AZURE_OPENAI_ENDPOINT';
`$env:AZURE_OPENAI_API_KEY = '$env:AZURE_OPENAI_API_KEY';
`$env:AZURE_OPENAI_DEPLOYMENT_NAME = '$env:AZURE_OPENAI_DEPLOYMENT_NAME';
`$env:AZURE_OPENAI_API_VERSION = '$env:AZURE_OPENAI_API_VERSION';
`$env:AZURE_AI_PROJECT_NAME = '$env:AZURE_AI_PROJECT_NAME';
`$env:AZURE_AI_SUBSCRIPTION_ID = '$env:AZURE_AI_SUBSCRIPTION_ID';
`$env:AZURE_AI_RESOURCE_GROUP = '$env:AZURE_AI_RESOURCE_GROUP';
`$env:AZURE_AI_AGENT_PROJECT_CONNECTION_STRING = '$env:AZURE_AI_AGENT_PROJECT_CONNECTION_STRING';
`$env:AZURE_TENANT_ID = '$env:AZURE_TENANT_ID';
`$env:AZURE_CLIENT_ID = '$env:AZURE_CLIENT_ID';
`$env:AZURE_CLIENT_SECRET = '$env:AZURE_CLIENT_SECRET';
`$env:USE_LOCAL_MEMORY = '$env:USE_LOCAL_MEMORY';
`$env:COSMOSDB_ENDPOINT = '$env:COSMOSDB_ENDPOINT';
`$env:COSMOSDB_KEY = '$env:COSMOSDB_KEY';
`$env:COSMOSDB_DATABASE = '$env:COSMOSDB_DATABASE';
`$env:COSMOSDB_CONTAINER = '$env:COSMOSDB_CONTAINER';
"@

# Start the backend server in a new PowerShell window
$backendCommand = "$envVars
cd $rootPath\src\backend;
Write-Host 'Starting backend server...';
try { 
    uv run uvicorn backend.app_kernel:app --port 8001 | Tee-Object -FilePath '$backendLogFile'
} catch {
    Write-Host 'Error starting backend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$backendLogFile';
    Read-Host 'Press Enter to close this window';
}"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCommand

# Wait for backend to start
Write-Host "Waiting for backend server to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting frontend server on port 3000..." -ForegroundColor Yellow
Write-Host "Log file: $frontendLogFile" -ForegroundColor Gray

# Start the frontend server in a new PowerShell window
$frontendCommand = "
`$env:BACKEND_API_URL = 'http://localhost:8001';
`$env:AUTH_ENABLED = '$env:AUTH_ENABLED';
cd $rootPath\src\frontend;
Write-Host 'Starting frontend server...';
try {
    uvicorn frontend_server:app --port 3000 --reload | Tee-Object -FilePath '$frontendLogFile'
} catch {
    Write-Host 'Error starting frontend: ' `$_.Exception.Message -ForegroundColor Red;
    `$_ | Out-File -Append '$frontendLogFile';
    Read-Host 'Press Enter to close this window';
}"

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCommand

# Wait for frontend to start
Write-Host "Waiting for frontend server to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Open the frontend in the default browser
Write-Host "Opening frontend in default browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

# Determine the configuration mode for display
$configMode = if ($UseAzure) { "Azure Cloud Services" } else { "Local Development (Mock Services)" }
$azureInfo = if ($UseAzure) {
"
  Azure Configuration:
    - OpenAI Endpoint: $env:AZURE_OPENAI_ENDPOINT
    - OpenAI Model Deployment: $env:AZURE_OPENAI_DEPLOYMENT_NAME
    - Azure Resource Group: $env:AZURE_AI_RESOURCE_GROUP
    - Azure AI Project: $env:AZURE_AI_PROJECT_NAME
    - Authentication: Using DefaultAzureCredential
"
} else { "" }

Write-Host "
--------------------------------------------------------------------------------------
                        Darbot Agent Engine - Development Server                       
--------------------------------------------------------------------------------------
  Backend:   http://localhost:8001       OpenAPI Docs: http://localhost:8001/docs
  Frontend:  http://localhost:3000
  
  Log files:
    - Backend:  $backendLogFile
    - Frontend: $frontendLogFile
    
  Environment: $configMode
    - Using local memory store: $env:USE_LOCAL_MEMORY
    - Authentication enabled: $env:AUTH_ENABLED$azureInfo
    
  Tips:
    - Submit a simple task like 'Create a project plan for website redesign'
    - Check the console logs in your browser for API request activity
    - For Azure authentication issues, ensure you're logged in with 'az login'
    - Remember to shut down both server windows when finished testing
    
  Parameters for Azure mode:
    .\run_servers.ps1 -UseAzure -AzureOpenAIEndpoint <endpoint> -AzureResourceGroup <group> -AzureAIProjectName <name>
--------------------------------------------------------------------------------------
" -ForegroundColor Cyan
