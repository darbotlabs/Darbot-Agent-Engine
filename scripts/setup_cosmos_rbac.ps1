# Thought into existence by Darbot
# Script to set up CosmosDB RBAC permissions for the Darbot Agent Engine

# Configuration variables
$cosmosAccountName = "darbot-cosmos-dev2"  # From the error message
$principalId = "ebb01e50-f389-4f45-84a3-8d588f0b5bab"  # From the error message
$subscriptionId = "99fc47d1-e510-42d6-bc78-63cac040a902"  # From our output
$role = "Cosmos DB Account Reader Role"  # As recommended in the doc

# Step 1: Check Azure CLI Authentication
Write-Host "Checking Azure CLI login..." -ForegroundColor Cyan
try {
    $account = az account show | ConvertFrom-Json
    Write-Host "✅ Logged in as: $($account.user.name)" -ForegroundColor Green
    Write-Host "   Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
}
catch {
    Write-Host "❌ Not logged in to Azure or authentication error" -ForegroundColor Red
    Write-Host "   Please run 'az login' in a separate terminal and try again" -ForegroundColor Yellow
    exit 1
}

# Step 2: Find the resource group for the CosmosDB account
Write-Host "`nFinding resource group for CosmosDB account '$cosmosAccountName'..." -ForegroundColor Cyan
try {
    $resourceGroups = az group list | ConvertFrom-Json
    
    # Try to find all cosmos db accounts in all resource groups
    Write-Host "Searching for CosmosDB account in resource groups..." -ForegroundColor Yellow
    $found = $false
    
    foreach ($rg in $resourceGroups) {
        Write-Host "  Checking resource group: $($rg.name)..." -ForegroundColor Gray
        $cosmosAccounts = az cosmosdb list --resource-group $rg.name --query "[?name=='$cosmosAccountName']" | ConvertFrom-Json
        
        if ($cosmosAccounts.Length -gt 0) {
            $resourceGroup = $rg.name
            Write-Host "✅ Found CosmosDB account '$cosmosAccountName' in resource group '$resourceGroup'" -ForegroundColor Green
            $found = $true
            break
        }
    }
    
    if (-not $found) {
        Write-Host "❌ Could not find CosmosDB account '$cosmosAccountName' in any resource group" -ForegroundColor Red
        Write-Host "   Please check the account name or try manually finding it in the Azure portal" -ForegroundColor Yellow
        
        # List all available cosmos db accounts
        Write-Host "`nAvailable CosmosDB accounts:" -ForegroundColor Cyan
        az cosmosdb list --output table
        exit 1
    }
}
catch {
    Write-Host "❌ Error finding resource group: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Create RBAC role assignment
Write-Host "`nSetting up RBAC permissions..." -ForegroundColor Cyan
$scope = "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccountName"

Write-Host "Role: $role" -ForegroundColor Yellow
Write-Host "Assignee Principal ID: $principalId" -ForegroundColor Yellow
Write-Host "Scope: $scope" -ForegroundColor Yellow

try {
    # Check if role assignment already exists
    $existingAssignment = az role assignment list --assignee $principalId --scope $scope --query "[?roleDefinitionName=='$role']" | ConvertFrom-Json
    
    if ($existingAssignment.Length -gt 0) {
        Write-Host "✅ RBAC role assignment already exists" -ForegroundColor Green
    }
    else {
        Write-Host "Creating new RBAC role assignment..." -ForegroundColor Yellow
        $result = az role assignment create --assignee $principalId --role "$role" --scope $scope | ConvertFrom-Json
        
        if ($result) {
            Write-Host "✅ RBAC role assignment created successfully" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to create RBAC role assignment" -ForegroundColor Red
        }
    }
}
catch {
    Write-Host "❌ Error setting up RBAC permissions: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   You may need to create the role assignment manually in the Azure Portal" -ForegroundColor Yellow
    Write-Host "   Portal steps are described in COSMOS_RBAC_SETUP.md" -ForegroundColor Yellow
    exit 1
}

# Step 4: Add Write permissions if needed
Write-Host "`nDo you want to add write permissions (Cosmos DB Operator role) as well? (y/n)" -ForegroundColor Cyan
$addWrite = Read-Host
if ($addWrite -eq "y") {
    $writeRole = "Cosmos DB Operator"
    
    try {
        Write-Host "Adding Cosmos DB Operator role for write permissions..." -ForegroundColor Yellow
        $result = az role assignment create --assignee $principalId --role "$writeRole" --scope $scope | ConvertFrom-Json
        
        if ($result) {
            Write-Host "✅ Write access RBAC role assignment created successfully" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to create write access RBAC role assignment" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Error setting up write access RBAC permissions: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Step 5: Instructions for testing
Write-Host "`n🔍 Next Steps to Test Configuration:" -ForegroundColor Cyan
Write-Host "1. Run the backend with Azure integration:" -ForegroundColor White
Write-Host "   ./scripts/run_servers.ps1 -UseAzure -AzureOpenAIEndpoint 'https://your-openai.openai.azure.com/' -AzureResourceGroup '$resourceGroup' -AzureAIProjectName 'your-ai-project'" -ForegroundColor Yellow
Write-Host "2. Update the Verification Checklist in COSMOS_RBAC_SETUP.md" -ForegroundColor White
Write-Host "3. Check for errors in the backend logs" -ForegroundColor White

Write-Host "`n✅ RBAC Setup Script Complete!" -ForegroundColor Green
