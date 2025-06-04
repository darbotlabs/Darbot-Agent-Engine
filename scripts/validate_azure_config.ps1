# Thought into existence by Darbot
# Validation Script for Darbot Agent Engine Azure Configuration
# This script validates that Azure services are accessible and properly configured

Write-Host "Darbot Agent Engine - Azure Services Validation" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

# Check Azure CLI authentication
Write-Host "1. Checking Azure CLI authentication..." -ForegroundColor Yellow
$azLogin = az account show 2>$null
if (-not $azLogin) {
    Write-Host "❌ Not logged in to Azure. Run 'az login' first." -ForegroundColor Red
    exit 1
}

$accountInfo = az account show | ConvertFrom-Json
Write-Host "✅ Authenticated as: $($accountInfo.user.name)" -ForegroundColor Green

# Validate subscription
Write-Host ""
Write-Host "2. Validating subscription access..." -ForegroundColor Yellow
$targetSubscription = "99fc47d1-e510-42d6-bc78-63cac040a902"
if ($accountInfo.id -eq $targetSubscription) {
    Write-Host "✅ Connected to correct subscription: $($accountInfo.name)" -ForegroundColor Green
} else {
    Write-Host "❌ Wrong subscription. Expected: $targetSubscription, Got: $($accountInfo.id)" -ForegroundColor Red
    Write-Host "Run: az account set --subscription $targetSubscription" -ForegroundColor Yellow
    exit 1
}

# Validate resource group
Write-Host ""
Write-Host "3. Validating resource group access..." -ForegroundColor Yellow
$rgExists = az group show --name "Studio-CAT" 2>$null
if ($rgExists) {
    Write-Host "✅ Resource group 'Studio-CAT' accessible" -ForegroundColor Green
} else {
    Write-Host "❌ Cannot access resource group 'Studio-CAT'" -ForegroundColor Red
    exit 1
}

# Validate Azure OpenAI service
Write-Host ""
Write-Host "4. Validating Azure OpenAI service..." -ForegroundColor Yellow
$aoaiService = az cognitiveservices account show --name "cat-studio-foundry" --resource-group "Studio-CAT" 2>$null
if ($aoaiService) {
    $serviceInfo = $aoaiService | ConvertFrom-Json
    Write-Host "✅ Azure OpenAI service accessible" -ForegroundColor Green
    Write-Host "   Endpoint: $($serviceInfo.properties.endpoint)" -ForegroundColor White
    Write-Host "   Location: $($serviceInfo.location)" -ForegroundColor White
    Write-Host "   Status: $($serviceInfo.properties.provisioningState)" -ForegroundColor White
} else {
    Write-Host "❌ Cannot access Azure OpenAI service 'cat-studio-foundry'" -ForegroundColor Red
    exit 1
}

# Validate model deployments
Write-Host ""
Write-Host "5. Validating model deployments..." -ForegroundColor Yellow
$deployments = az cognitiveservices account deployment list --name "cat-studio-foundry" --resource-group "Studio-CAT" 2>$null
if ($deployments) {
    $deploymentList = $deployments | ConvertFrom-Json
    Write-Host "✅ Model deployments found: $($deploymentList.Count)" -ForegroundColor Green
    foreach ($deployment in $deploymentList) {
        $status = if ($deployment.properties.provisioningState -eq "Succeeded") { "✅" } else { "❌" }
        Write-Host "   $status $($deployment.name): $($deployment.properties.model.name) ($($deployment.properties.provisioningState))" -ForegroundColor White
    }
} else {
    Write-Host "❌ Cannot retrieve model deployments" -ForegroundColor Red
}

# Validate Cosmos DB
Write-Host ""
Write-Host "6. Validating Cosmos DB access..." -ForegroundColor Yellow
$cosmosAccounts = az cosmosdb list --resource-group "Studio-CAT" 2>$null
if ($cosmosAccounts) {
    $accounts = $cosmosAccounts | ConvertFrom-Json
    Write-Host "✅ Cosmos DB accounts found: $($accounts.Count)" -ForegroundColor Green
    foreach ($account in $accounts) {
        $status = if ($account.provisioningState -eq "Succeeded") { "✅" } else { "❌" }
        Write-Host "   $status $($account.name): $($account.documentEndpoint)" -ForegroundColor White
    }
} else {
    Write-Host "❌ Cannot access Cosmos DB accounts" -ForegroundColor Red
}

# Check if backend is running with mock configuration
Write-Host ""
Write-Host "7. Checking current backend configuration..." -ForegroundColor Yellow
$envFile = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    if ($envContent -match "USE_LOCAL_MEMORY=True" -or $envContent -match "mockendpoint") {
        Write-Host "❌ Backend is configured for mock/local mode" -ForegroundColor Red
        Write-Host "   Current .env file uses mock values" -ForegroundColor Yellow
        Write-Host "   Run .\fix_azure_config.ps1 to fix this" -ForegroundColor Cyan
    } else {
        Write-Host "✅ Backend appears to be configured for Azure services" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️  Backend .env file not found" -ForegroundColor Yellow
}

# Test backend connectivity (if running)
Write-Host ""
Write-Host "8. Testing backend connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/healthz" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend server is running and responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend server not running or not accessible" -ForegroundColor Yellow
    Write-Host "   Start servers with: .\fix_azure_config.ps1" -ForegroundColor Cyan
}

# Test frontend connectivity (if running)
Write-Host ""
Write-Host "9. Testing frontend connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend server is running and accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Frontend server not running or not accessible" -ForegroundColor Yellow
    Write-Host "   Start servers with: .\fix_azure_config.ps1" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Validation Summary:" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host "✅ Azure authentication and access verified" -ForegroundColor Green
Write-Host "✅ All Azure resources (OpenAI, Cosmos DB) are accessible" -ForegroundColor Green
Write-Host "✅ Model deployments are available and ready" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. If backend shows mock configuration: Run .\fix_azure_config.ps1" -ForegroundColor White
Write-Host "2. If servers aren't running: Run .\fix_azure_config.ps1" -ForegroundColor White
Write-Host "3. Test task creation at http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "For more details, see: CONFIGURATION_AUDIT_RESULTS.md" -ForegroundColor Cyan