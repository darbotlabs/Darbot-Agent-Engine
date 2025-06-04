# Thought into existence by Darbot
# Quick Fix Script for Darbot Agent Engine Azure Configuration
# This script automatically configures and runs the servers with the correct Azure settings

param (
    [Parameter(Mandatory = $false)]
    [string]$ModelDeployment = "grok-3",  # Options: grok-3, Phi-4-reasoning, Phi-4-mini-reasoning
    
    [Parameter(Mandatory = $false)]
    [switch]$UpdateEnvFile = $false  # Set to true to update .env file instead of using parameters
)

Write-Host "Darbot Agent Engine - Azure Configuration Fix" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Validate Azure CLI login
Write-Host "Checking Azure CLI authentication..." -ForegroundColor Yellow
$azLogin = az account show 2>$null
if (-not $azLogin) {
    Write-Host "❌ You are not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

$accountInfo = az account show | ConvertFrom-Json
Write-Host "✅ Authenticated as: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host "✅ Subscription: $($accountInfo.name)" -ForegroundColor Green

# Define Azure configuration
$azureConfig = @{
    OpenAIEndpoint = "https://cat-studio-foundry.openai.azure.com/"
    OpenAIDeploymentName = $ModelDeployment
    OpenAIApiVersion = "2024-05-01-preview"
    SubscriptionId = "99fc47d1-e510-42d6-bc78-63cac040a902"
    ResourceGroup = "Studio-CAT"
    AIProjectName = "studio-cat"
    CosmosEndpoint = "https://darbot-cosmos-dev.documents.azure.com:443/"
    CosmosDatabase = "darbot-agent-db"
    CosmosContainer = "agent-conversations"
}

Write-Host ""
Write-Host "Azure Configuration:" -ForegroundColor Cyan
Write-Host "  OpenAI Endpoint: $($azureConfig.OpenAIEndpoint)" -ForegroundColor White
Write-Host "  Model Deployment: $($azureConfig.OpenAIDeploymentName)" -ForegroundColor White
Write-Host "  Resource Group: $($azureConfig.ResourceGroup)" -ForegroundColor White
Write-Host "  AI Project: $($azureConfig.AIProjectName)" -ForegroundColor White
Write-Host "  Cosmos DB: $($azureConfig.CosmosEndpoint)" -ForegroundColor White

if ($UpdateEnvFile) {
    Write-Host ""
    Write-Host "Updating backend .env file with Azure configuration..." -ForegroundColor Yellow
    
    $envFile = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\.env"
    $envContent = @"
# Thought into existence by Darbot
# Azure production environment variables (Updated: $(Get-Date))
PYTHONPATH=d:\0GH_PROD\Darbot-Agent-Engine\src

# Azure OpenAI settings (Real Azure Services)
AZURE_OPENAI_ENDPOINT=$($azureConfig.OpenAIEndpoint)
AZURE_OPENAI_DEPLOYMENT_NAME=$($azureConfig.OpenAIDeploymentName)
AZURE_OPENAI_API_VERSION=$($azureConfig.OpenAIApiVersion)

# Azure AI settings
AZURE_AI_PROJECT_NAME=$($azureConfig.AIProjectName)
AZURE_AI_SUBSCRIPTION_ID=$($azureConfig.SubscriptionId)
AZURE_AI_RESOURCE_GROUP=$($azureConfig.ResourceGroup)

# Azure production mode - Connect to real services
USE_LOCAL_MEMORY=False
BYPASS_AUTH_FOR_LOCAL_DEV=False
DISABLE_TELEMETRY=False

# CosmosDB settings (Real Azure Cosmos DB)
COSMOSDB_ENDPOINT=$($azureConfig.CosmosEndpoint)
COSMOSDB_DATABASE=$($azureConfig.CosmosDatabase)
COSMOSDB_CONTAINER=$($azureConfig.CosmosContainer)

# Frontend settings
BACKEND_API_URL=http://localhost:8001
AUTH_ENABLED=False
"@

    $envContent | Out-File -FilePath $envFile -Encoding UTF8
    Write-Host "✅ Updated $envFile" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Starting servers with updated .env configuration..." -ForegroundColor Yellow
    & "D:\0GH_PROD\Darbot-Agent-Engine\run_servers.ps1"
    
} else {
    Write-Host ""
    Write-Host "Starting servers with Azure configuration..." -ForegroundColor Yellow
    
    # Run the main script with Azure parameters
    & "D:\0GH_PROD\Darbot-Agent-Engine\run_servers.ps1" `
        -UseAzure `
        -AzureOpenAIEndpoint $azureConfig.OpenAIEndpoint `
        -AzureOpenAIDeploymentName $azureConfig.OpenAIDeploymentName `
        -AzureOpenAIApiVersion $azureConfig.OpenAIApiVersion `
        -AzureSubscriptionId $azureConfig.SubscriptionId `
        -AzureResourceGroup $azureConfig.ResourceGroup `
        -AzureAIProjectName $azureConfig.AIProjectName
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Wait for both servers to start (about 10 seconds)" -ForegroundColor White
Write-Host "2. Frontend will automatically open at http://localhost:3000" -ForegroundColor White
Write-Host "3. Try creating a task: 'Create a project plan for website redesign'" -ForegroundColor White
Write-Host "4. Backend API docs available at: http://localhost:8001/docs" -ForegroundColor White
Write-Host ""
Write-Host "If task creation still fails, check the backend console for detailed error messages." -ForegroundColor Yellow
Write-Host ""
Write-Host "Available model deployments:" -ForegroundColor Cyan
Write-Host "  - grok-3 (default - best for complex reasoning)" -ForegroundColor White
Write-Host "  - Phi-4-reasoning (balanced performance)" -ForegroundColor White  
Write-Host "  - Phi-4-mini-reasoning (fastest response)" -ForegroundColor White
Write-Host ""
Write-Host "To use a different model:" -ForegroundColor Cyan
Write-Host "  .\fix_azure_config.ps1 -ModelDeployment 'Phi-4-reasoning'" -ForegroundColor White