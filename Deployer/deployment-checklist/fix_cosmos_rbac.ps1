# Thought into existence by Darbot
# Script to fix CosmosDB RBAC permissions for Darbot Agent Engine

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "Studio-CAT",  # Default from validate_azure_config.ps1
    [Parameter(Mandatory=$false)]
    [string]$CosmosAccountName = "",
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId = "99fc47d1-e510-42d6-bc78-63cac040a902",  # From COSMOS_RBAC_SETUP.md
    [Parameter(Mandatory=$false)]
    [string]$PrincipalId = "",
    [Parameter(Mandatory=$false)]
    [switch]$WriteAccess = $false
)

Write-Host "🔐 Darbot Agent Engine - CosmosDB RBAC Permission Fix" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# Step 1: Verify Azure CLI login and subscription
Write-Host "`n📋 Step 1: Verifying Azure authentication..." -ForegroundColor Yellow
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "✅ Authenticated as: $($account.user.name)" -ForegroundColor Green
    
    # Set subscription if different from current
    if ($account.id -ne $SubscriptionId) {
        Write-Host "Setting subscription to: $SubscriptionId" -ForegroundColor Yellow
        az account set --subscription $SubscriptionId
        $account = az account show --output json | ConvertFrom-Json
        Write-Host "✅ Now using subscription: $($account.name) ($($account.id))" -ForegroundColor Green
    } else {
        Write-Host "✅ Using subscription: $($account.name) ($($account.id))" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Azure CLI authentication failed. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

# Step 2: Get current user's principal ID if not provided
if (-not $PrincipalId) {
    Write-Host "`n👤 Step 2: Getting current user's principal ID..." -ForegroundColor Yellow
    try {
        $PrincipalId = az ad signed-in-user show --query id -o tsv
        if (-not $PrincipalId) {
            throw "Failed to retrieve principal ID"
        }
        Write-Host "✅ Current user principal ID: $PrincipalId" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to get principal ID: $_" -ForegroundColor Red
        Write-Host "Please provide the principal ID using the -PrincipalId parameter" -ForegroundColor Yellow
        exit 1
    }
}

# Step 3: Find CosmosDB accounts if not specified
if (-not $CosmosAccountName) {
    Write-Host "`n🔍 Step 3: Finding CosmosDB accounts in resource group..." -ForegroundColor Yellow
    try {
        $cosmosAccounts = az cosmosdb list --resource-group $ResourceGroup --query "[].name" -o tsv
        
        if (-not $cosmosAccounts) {
            Write-Host "❌ No CosmosDB accounts found in resource group: $ResourceGroup" -ForegroundColor Red
            exit 1
        }
        
        # Convert single string to array if there's just one account
        if ($cosmosAccounts -is [string]) {
            $cosmosAccountsArray = @($cosmosAccounts)
        } else {
            $cosmosAccountsArray = $cosmosAccounts
        }
        
        Write-Host "Found CosmosDB account(s):" -ForegroundColor Green
        for ($i = 0; $i -lt $cosmosAccountsArray.Count; $i++) {
            Write-Host "  $($i+1). $($cosmosAccountsArray[$i])" -ForegroundColor White
        }
        
        # If multiple accounts found, let user select
        if ($cosmosAccountsArray.Count -gt 1) {
            $selection = Read-Host "Enter the number of the CosmosDB account to configure (1-$($cosmosAccountsArray.Count))"
            $index = [int]$selection - 1
            
            if ($index -lt 0 -or $index -ge $cosmosAccountsArray.Count) {
                Write-Host "❌ Invalid selection" -ForegroundColor Red
                exit 1
            }
            
            $CosmosAccountName = $cosmosAccountsArray[$index]
        } else {
            $CosmosAccountName = $cosmosAccountsArray[0]
        }
        
        Write-Host "✅ Selected CosmosDB account: $CosmosAccountName" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error finding CosmosDB accounts: $_" -ForegroundColor Red
        Write-Host "Please provide the CosmosDB account name using the -CosmosAccountName parameter" -ForegroundColor Yellow
        exit 1
    }
}

# Step 4: Determine role to assign
$roleName = if ($WriteAccess) { "Cosmos DB Operator" } else { "Cosmos DB Account Reader Role" }

Write-Host "`n👑 Step 4: Assigning $roleName to principal..." -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "  CosmosDB Account: $CosmosAccountName" -ForegroundColor White
Write-Host "  Principal ID: $PrincipalId" -ForegroundColor White
Write-Host "  Role: $roleName" -ForegroundColor White

try {
    # Construct the resource scope URI
    $scope = "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$CosmosAccountName"
    
    # Check if role assignment already exists
    $existing = az role assignment list --assignee $PrincipalId --scope $scope --query "[?roleDefinitionName=='$roleName']" -o json | ConvertFrom-Json
    
    if ($existing) {
        Write-Host "✅ Role assignment already exists" -ForegroundColor Green
    } else {
        # Create role assignment
        $result = az role assignment create --assignee $PrincipalId --role "$roleName" --scope $scope --output json | ConvertFrom-Json
        
        if ($result) {
            Write-Host "✅ Role '$roleName' successfully assigned" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Role assignment may have failed, please check in Azure Portal" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "❌ Failed to assign role: $_" -ForegroundColor Red
    Write-Host "You may need elevated permissions to assign roles. Try using Azure Portal instead:" -ForegroundColor Yellow
    Write-Host "1. Navigate to Azure Portal → CosmosDB → $CosmosAccountName" -ForegroundColor White
    Write-Host "2. Go to Access control (IAM)" -ForegroundColor White
    Write-Host "3. Click + Add → Add role assignment" -ForegroundColor White
    Write-Host "4. Select role: $roleName" -ForegroundColor White
    Write-Host "5. Assign access to: User, group, or service principal" -ForegroundColor White
    Write-Host "6. Select the user account you're using for development" -ForegroundColor White
    Write-Host "7. Click Save" -ForegroundColor White
    exit 1
}

# Step 5: Test connection
Write-Host "`n🧪 Step 5: Testing connection to CosmosDB..." -ForegroundColor Yellow
Write-Host "Testing connection may take a minute as Azure propagates RBAC permissions" -ForegroundColor White
Write-Host "Please wait..." -ForegroundColor White

# Wait for RBAC propagation
Start-Sleep -Seconds 10

try {
    # Use Azure CLI to test basic access
    $testResult = az cosmosdb database list --name $CosmosAccountName --resource-group $ResourceGroup --output json 2>$null | ConvertFrom-Json
    
    if ($testResult) {
        Write-Host "✅ Successfully connected to CosmosDB and listed databases!" -ForegroundColor Green
        Write-Host "Found databases:" -ForegroundColor White
        $testResult | ForEach-Object { Write-Host "  - $($_.id)" -ForegroundColor White }
    } else {
        throw "No databases found or access denied"
    }
} catch {
    Write-Host "⚠️ CosmosDB access test failed: $_" -ForegroundColor Yellow
    Write-Host "RBAC permissions may take a few minutes to propagate. Please wait and try again." -ForegroundColor Yellow
    Write-Host "If the issue persists, verify your permissions in the Azure Portal." -ForegroundColor Yellow
    exit 1
}

# Step 6: Update environment configuration
Write-Host "`n⚙️ Step 6: Updating environment configuration..." -ForegroundColor Yellow

$backendEnvPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\.env"

if (Test-Path $backendEnvPath) {
    # Read existing .env file
    $envContent = Get-Content $backendEnvPath -Raw
    
    # Check if we need to update the configuration
    $useLocalMemory = if ($envContent -match "USE_LOCAL_MEMORY\s*=\s*True") { $true } else { $false }
    
    if ($useLocalMemory) {
        Write-Host "⚠️ Found USE_LOCAL_MEMORY=True in .env file" -ForegroundColor Yellow
        $updateConfig = Read-Host "Would you like to update the configuration to use Azure resources? (y/n)"
        
        if ($updateConfig -eq "y") {
            # Get the CosmosDB endpoint
            $cosmosEndpoint = az cosmosdb show --name $CosmosAccountName --resource-group $ResourceGroup --query "documentEndpoint" -o tsv
            
            # Update the .env file
            $envContent = $envContent -replace "USE_LOCAL_MEMORY\s*=\s*True", "USE_LOCAL_MEMORY=False"
            $envContent = $envContent -replace "COSMOSDB_ENDPOINT\s*=.*", "COSMOSDB_ENDPOINT=$cosmosEndpoint"
            $envContent = $envContent -replace "COSMOSDB_DATABASE\s*=.*", "COSMOSDB_DATABASE=DarbotMemory"
            $envContent = $envContent -replace "COSMOSDB_CONTAINER\s*=.*", "COSMOSDB_CONTAINER=agent-conversations"
            
            # Save the updated .env file
            $envContent | Out-File -FilePath $backendEnvPath -Encoding UTF8
            Write-Host "✅ Updated .env file to use Azure CosmosDB" -ForegroundColor Green
        }
    } else {
        Write-Host "✅ Backend already configured to use Azure resources" -ForegroundColor Green
    }
} else {
    Write-Host "⚠️ Backend .env file not found at: $backendEnvPath" -ForegroundColor Yellow
    Write-Host "You'll need to configure your environment variables manually" -ForegroundColor Yellow
}

# Final instructions
Write-Host "`n🎉 CosmosDB RBAC setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Run the Darbot Agent Engine with Azure integration:" -ForegroundColor White
Write-Host "   .\scripts\run_servers.ps1 -UseAzure" -ForegroundColor White
Write-Host "      -AzureOpenAIEndpoint 'https://your-openai-service.openai.azure.com/'" -ForegroundColor White
Write-Host "      -AzureResourceGroup '$ResourceGroup'" -ForegroundColor White
Write-Host "      -AzureAIProjectName 'your-ai-project'" -ForegroundColor White
Write-Host "`n2. Verify the application is using CosmosDB by checking:" -ForegroundColor White
Write-Host "   - Backend logs for successful CosmosDB connections" -ForegroundColor White
Write-Host "   - Data being stored in the CosmosDB container" -ForegroundColor White
Write-Host "`n3. If using App Service for production, don't forget to:" -ForegroundColor White
Write-Host "   - Enable Managed Identity on the App Service" -ForegroundColor White
Write-Host "   - Assign the same RBAC role to the App Service's Managed Identity" -ForegroundColor White
Write-Host "`nFor more details, see: COSMOS_RBAC_SETUP.md" -ForegroundColor Cyan
