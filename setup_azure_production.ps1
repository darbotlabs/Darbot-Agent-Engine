# Thought into existence by Darbot
# Azure Configuration and Production Deployment Script
# This script sets up the Darbot Agent Engine with real Azure services

param(
    [switch]$Production = $false,
    [string]$SubscriptionId = "",
    [string]$ResourceGroup = "darbot-agent-engine-rg",
    [string]$Location = "eastus2"
)

Write-Host "🚀 Starting Darbot Agent Engine Azure Production Setup..." -ForegroundColor Cyan

# Step 1: Azure Authentication
Write-Host "`n🔐 Step 1: Azure Authentication" -ForegroundColor Yellow
try {
    # Check if Azure CLI is installed
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    if ($azVersion) {
        Write-Host "✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
    } else {
        throw "Azure CLI not found"
    }
    
    # Login to Azure
    Write-Host "🔑 Logging into Azure..." -ForegroundColor White
    $loginResult = az login --output json | ConvertFrom-Json
    
    if ($loginResult) {
        Write-Host "✅ Successfully logged into Azure" -ForegroundColor Green
        $currentSub = az account show --output json | ConvertFrom-Json
        Write-Host "📋 Current subscription: $($currentSub.name) ($($currentSub.id))" -ForegroundColor White
        
        # Set subscription if provided
        if ($SubscriptionId) {
            az account set --subscription $SubscriptionId
            Write-Host "✅ Switched to subscription: $SubscriptionId" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "❌ Azure authentication failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Step 2: Resource Group Setup
Write-Host "`n🏗️ Step 2: Resource Group Setup" -ForegroundColor Yellow
try {
    $rgExists = az group exists --name $ResourceGroup --output tsv
    if ($rgExists -eq "true") {
        Write-Host "✅ Resource group '$ResourceGroup' already exists" -ForegroundColor Green
    } else {
        Write-Host "📦 Creating resource group '$ResourceGroup' in '$Location'..." -ForegroundColor White
        az group create --name $ResourceGroup --location $Location --output table
        Write-Host "✅ Resource group created successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Resource group setup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Azure Services Provisioning
Write-Host "`n☁️ Step 3: Azure Services Provisioning" -ForegroundColor Yellow

# Generate unique names
$timestamp = Get-Date -Format "yyyyMMddHHmm"
$uniqueId = $timestamp.Substring($timestamp.Length - 6)

$cosmosAccountName = "darbot-cosmos-$uniqueId"
$aiProjectName = "darbot-ai-project-$uniqueId" 
$storageAccountName = "darbotst$uniqueId"
$appServicePlanName = "darbot-plan-$uniqueId"
$webAppName = "darbot-app-$uniqueId"

Write-Host "🆔 Using unique identifier: $uniqueId" -ForegroundColor White

# Cosmos DB
Write-Host "`n📊 Creating Cosmos DB..." -ForegroundColor White
try {
    $cosmosResult = az cosmosdb create `
        --name $cosmosAccountName `
        --resource-group $ResourceGroup `
        --locations regionName=$Location `
        --output json | ConvertFrom-Json
    
    if ($cosmosResult) {
        Write-Host "✅ Cosmos DB created: $($cosmosResult.name)" -ForegroundColor Green
        
        # Create database and container
        az cosmosdb sql database create `
            --account-name $cosmosAccountName `
            --resource-group $ResourceGroup `
            --name "DarbotMemory" `
            --output table
        
        az cosmosdb sql container create `
            --account-name $cosmosAccountName `
            --resource-group $ResourceGroup `
            --database-name "DarbotMemory" `
            --name "Sessions" `
            --partition-key-path "/session_id" `
            --throughput 400 `
            --output table
        
        Write-Host "✅ Cosmos DB database and container created" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Cosmos DB creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Storage Account
Write-Host "`n💾 Creating Storage Account..." -ForegroundColor White
try {
    $storageResult = az storage account create `
        --name $storageAccountName `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku Standard_LRS `
        --output json | ConvertFrom-Json
    
    if ($storageResult) {
        Write-Host "✅ Storage Account created: $($storageResult.name)" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Storage Account creation failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Azure AI Services
Write-Host "`n🤖 Creating Azure AI Services..." -ForegroundColor White
try {
    # Create Azure OpenAI resource
    $openaiResult = az cognitiveservices account create `
        --name "darbot-openai-$uniqueId" `
        --resource-group $ResourceGroup `
        --location $Location `
        --kind OpenAI `
        --sku S0 `
        --output json | ConvertFrom-Json
    
    if ($openaiResult) {
        Write-Host "✅ Azure OpenAI resource created: $($openaiResult.name)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Azure OpenAI creation may require approval: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 4: Get Connection Strings and Keys
Write-Host "`n🔑 Step 4: Retrieving Connection Strings and Keys" -ForegroundColor Yellow

# Cosmos DB connection string
$cosmosConnString = az cosmosdb keys list --name $cosmosAccountName --resource-group $ResourceGroup --type connection-strings --query "connectionStrings[0].connectionString" --output tsv

# Storage account connection string  
$storageConnString = az storage account show-connection-string --name $storageAccountName --resource-group $ResourceGroup --query connectionString --output tsv

# Azure OpenAI endpoint and key
$openaiEndpoint = az cognitiveservices account show --name "darbot-openai-$uniqueId" --resource-group $ResourceGroup --query properties.endpoint --output tsv
$openaiKey = az cognitiveservices account keys list --name "darbot-openai-$uniqueId" --resource-group $ResourceGroup --query key1 --output tsv

# Step 5: Update Environment Configuration
Write-Host "`n⚙️ Step 5: Updating Environment Configuration" -ForegroundColor Yellow

$envContent = @"
# Thought into existence by Darbot
# Azure Production Configuration - Generated $(Get-Date)

# Azure Authentication
AZURE_TENANT_ID=$((az account show --query tenantId --output tsv))
AZURE_SUBSCRIPTION_ID=$((az account show --query id --output tsv))

# Cosmos DB Configuration
COSMOS_DB_CONNECTION_STRING=$cosmosConnString
COSMOS_DB_DATABASE_NAME=DarbotMemory
COSMOS_DB_CONTAINER_NAME=Sessions

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=$storageConnString

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=$openaiEndpoint
AZURE_OPENAI_API_KEY=$openaiKey
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Project (if available)
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING=$cosmosConnString

# Application Configuration
USE_LOCAL_MEMORY=False
BYPASS_AUTH_FOR_LOCAL_DEV=False
DISABLE_TELEMETRY=False
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
ENABLE_FILE_LOGGING=True

# Security
ALLOWED_ORIGINS=https://$webAppName.azurewebsites.net,http://localhost:3000
"@

# Write to .env file
$envContent | Out-File -FilePath "src\backend\.env" -Encoding UTF8
Write-Host "✅ Environment configuration updated in src\backend\.env" -ForegroundColor Green

# Step 6: Deploy Application (if in Production mode)
if ($Production) {
    Write-Host "`n🚀 Step 6: Production Deployment" -ForegroundColor Yellow
    
    # Create App Service Plan
    az appservice plan create `
        --name $appServicePlanName `
        --resource-group $ResourceGroup `
        --location $Location `
        --sku B1 `
        --is-linux `
        --output table
    
    # Create Web App
    az webapp create `
        --name $webAppName `
        --resource-group $ResourceGroup `
        --plan $appServicePlanName `
        --runtime "PYTHON|3.9" `
        --output table
    
    # Set environment variables in Web App
    az webapp config appsettings set `
        --name $webAppName `
        --resource-group $ResourceGroup `
        --settings $($envContent.Split("`n") | Where-Object { $_ -match "^[A-Z]" } | ForEach-Object { $_.Replace("=", " ") }) `
        --output table
    
    Write-Host "✅ Web App created and configured: https://$webAppName.azurewebsites.net" -ForegroundColor Green
}

# Step 7: Start Local Services for Testing
Write-Host "`n🧪 Step 7: Starting Local Services for Testing" -ForegroundColor Yellow

# Start backend with production configuration
Start-Process powershell -ArgumentList "-Command", "cd 'src\backend'; python -m uvicorn app_kernel:app --host 127.0.0.1 --port 8001 --reload" -WindowStyle Minimized

# Start frontend
Start-Process powershell -ArgumentList "-Command", "cd 'src\frontend'; npm start" -WindowStyle Minimized

Start-Sleep -Seconds 10

Write-Host "`n🎉 Darbot Agent Engine Azure Setup Complete!" -ForegroundColor Green
Write-Host "📊 Resource Summary:" -ForegroundColor Cyan
Write-Host "  • Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "  • Cosmos DB: $cosmosAccountName" -ForegroundColor White
Write-Host "  • Storage Account: $storageAccountName" -ForegroundColor White
Write-Host "  • Azure OpenAI: darbot-openai-$uniqueId" -ForegroundColor White

if ($Production) {
    Write-Host "  • Web App: https://$webAppName.azurewebsites.net" -ForegroundColor White
}

Write-Host "`n🌐 Local URLs:" -ForegroundColor Cyan
Write-Host "  • Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  • Backend API: http://localhost:8001" -ForegroundColor White
Write-Host "  • API Docs: http://localhost:8001/docs" -ForegroundColor White

Write-Host "`n🔧 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Test the application at http://localhost:3000" -ForegroundColor White
Write-Host "2. Create a task through the UI to verify end-to-end functionality" -ForegroundColor White
Write-Host "3. Monitor Azure resources in the Azure Portal" -ForegroundColor White

if (-not $Production) {
    Write-Host "4. Run with -Production flag to deploy to Azure App Service" -ForegroundColor White
}
