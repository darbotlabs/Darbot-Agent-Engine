# Thought into existence by Darbot
# Test Azure Resource Access and Diagnose RBAC Issues

Write-Host "Darbot Agent Engine - Azure Resource Access Test" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Step 1: Check Azure CLI Authentication
Write-Host "`n1. Checking Azure CLI Authentication..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        Write-Host "✅ Azure CLI Authenticated as: $($account.user.name)" -ForegroundColor Green
        Write-Host "   Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
    } else {
        Write-Host "❌ Not authenticated with Azure CLI" -ForegroundColor Red
        Write-Host "   Run 'az login' to authenticate first" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Azure CLI authentication: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Test CosmosDB Access
Write-Host "`n2. Testing CosmosDB Access..." -ForegroundColor Yellow
$resourceGroup = "Studio-CAT" # From validate_azure_config.ps1
$cosmosAccounts = @("darbot-cosmos-dev", "darbot-cosmos-dev2") # From previous tests

foreach ($cosmosAccount in $cosmosAccounts) {
    Write-Host "`n   Testing access to CosmosDB account: $cosmosAccount" -ForegroundColor White
    try {
        # Test account metadata access
        $accountInfo = az cosmosdb show --name $cosmosAccount --resource-group $resourceGroup 2>$null
        if ($accountInfo) {
            Write-Host "   ✅ Can access CosmosDB account metadata" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Cannot access CosmosDB account metadata" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ Error accessing CosmosDB account: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    try {
        # Test database list access
        $databases = az cosmosdb database list --name $cosmosAccount --resource-group $resourceGroup 2>$null
        if ($databases) {
            Write-Host "   ✅ Can list databases in CosmosDB account" -ForegroundColor Green
        } else {
            Write-Host "   ❌ Cannot list databases in CosmosDB account" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ❌ Error listing databases: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 3: Test Azure OpenAI Access
Write-Host "`n3. Testing Azure OpenAI Access..." -ForegroundColor Yellow
try {
    $openaiService = az cognitiveservices account show --name "cat-studio-foundry" --resource-group "Studio-CAT" 2>$null
    if ($openaiService) {
        Write-Host "   ✅ Can access Azure OpenAI service" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Cannot access Azure OpenAI service" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Error accessing Azure OpenAI service: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 4: Check Current RBAC Role Assignments
Write-Host "`n4. Checking Current RBAC Role Assignments..." -ForegroundColor Yellow
try {
    $principalId = az ad signed-in-user show --query id -o tsv 2>$null
    if ($principalId) {
        Write-Host "   ✅ Current user principal ID: $principalId" -ForegroundColor Green
        
        # Check role assignments
        $roles = az role assignment list --assignee $principalId 2>$null | ConvertFrom-Json
        if ($roles) {
            Write-Host "   ✅ Found $(if ($roles -is [array]) { $roles.Count } else { 1 }) role assignments for current user:" -ForegroundColor Green
            
            $cosmosRolesFound = $false
            foreach ($role in $roles) {
                if ($role.roleDefinitionName -like "*Cosmos*") {
                    Write-Host "      - $($role.roleDefinitionName) on $($role.scope)" -ForegroundColor Green
                    $cosmosRolesFound = $true
                } else {
                    Write-Host "      - $($role.roleDefinitionName) on $($role.scope)" -ForegroundColor White
                }
            }
            
            if (-not $cosmosRolesFound) {
                Write-Host "   ⚠️ No Cosmos DB specific roles found - this might be your issue!" -ForegroundColor Yellow
                Write-Host "      See FIXING_COSMOS_RBAC_PERMISSIONS.md for instructions" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ⚠️ No role assignments found for current user" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ❌ Could not determine current user principal ID" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Error checking role assignments: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Check Environment Configuration
Write-Host "`n5. Checking Environment Configuration..." -ForegroundColor Yellow
$backendEnvPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\.env"
if (Test-Path $backendEnvPath) {
    $envContent = Get-Content $backendEnvPath -Raw
    
    # Check USE_LOCAL_MEMORY
    if ($envContent -match "USE_LOCAL_MEMORY\s*=\s*True") {
        Write-Host "   ⚠️ Application configured to use LOCAL MEMORY (mock mode)" -ForegroundColor Yellow
        Write-Host "      Need to set USE_LOCAL_MEMORY=False to use Azure resources" -ForegroundColor Yellow
    } elseif ($envContent -match "USE_LOCAL_MEMORY\s*=\s*False") {
        Write-Host "   ✅ Application configured to use Azure resources" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ USE_LOCAL_MEMORY setting not found in .env file" -ForegroundColor Yellow
    }
    
    # Check CosmosDB configuration
    if ($envContent -match "COSMOSDB_ENDPOINT\s*=\s*([^\r\n]*)") {
        $endpoint = $matches[1].Trim()
        if ($endpoint -and $endpoint -ne '""' -and $endpoint -ne "''") {
            Write-Host "   ✅ CosmosDB endpoint configured: $endpoint" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ CosmosDB endpoint is empty or not configured" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   ⚠️ CosmosDB endpoint setting not found in .env file" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Backend .env file not found at: $backendEnvPath" -ForegroundColor Red
}

# Final recommendations
Write-Host "`nRecommendations:" -ForegroundColor Cyan
Write-Host "----------------" -ForegroundColor Cyan

Write-Host "1. Follow instructions in FIXING_COSMOS_RBAC_PERMISSIONS.md to set up correct RBAC permissions" -ForegroundColor White
Write-Host "2. Use run_servers.ps1 with -UseAzure switch to start the application with Azure integration" -ForegroundColor White
Write-Host "3. Check CosmosDB in Azure Portal to verify your user has proper role assignments" -ForegroundColor White

Write-Host "`nFor additional troubleshooting, see RUNNING_WITH_AZURE.md" -ForegroundColor White
