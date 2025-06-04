# Azure RBAC Setup for Darbot Agent Engine
# Thought into existence by Darbot

# Variables for the script
$principalId = "ebb01e50-f389-4f45-84a3-8d588f0b5bab"
$subscription = "99fc47d1-e510-42d6-bc78-63cac040a902" # FastTrack Azure Commercial Shared POC
$resourceGroup = "Studio-CAT"
$cosmosAccount1 = "darbot-cosmos-dev"
$cosmosAccount2 = "darbot-cosmos-dev2"
$userPrincipal = "dayour@microsoft.com"

# Summary of RBAC Issue
Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "         FIX COSMOS DB RBAC PERMISSIONS             " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

Write-Host "`nProblem: Missing RBAC permissions for CosmosDB access" -ForegroundColor Yellow
Write-Host "The system is successfully authenticating with Azure AD, but RBAC permissions are missing." -ForegroundColor White
Write-Host "Error message: 'Request blocked because principal does not have required RBAC permissions'" -ForegroundColor White

# Print Principal and Resource details
Write-Host "`nDetails:" -ForegroundColor Yellow
Write-Host "- Principal ID: $principalId" -ForegroundColor White
Write-Host "- Missing Action: Microsoft.DocumentDB/databaseAccounts/readMetadata" -ForegroundColor White
Write-Host "- Resource: CosmosDB accounts ($cosmosAccount1 and $cosmosAccount2)" -ForegroundColor White
Write-Host "- Current user: $userPrincipal" -ForegroundColor White
Write-Host "- Subscription: $subscription (FastTrack Azure Commercial Shared POC)" -ForegroundColor White
Write-Host "- Resource Group: $resourceGroup" -ForegroundColor White

# Check if Azure CLI is logged in
Write-Host "`nChecking Azure CLI login status..." -ForegroundColor Yellow
try {
    $loginStatus = az account show --query name -o tsv 2>$null
    if ($null -eq $loginStatus) {
        Write-Host "You are not logged in to Azure CLI. Please login first." -ForegroundColor Red
        Write-Host "Running: az login" -ForegroundColor White
        az login
    } else {
        Write-Host "Currently logged in as: $loginStatus" -ForegroundColor Green
    }
} catch {
    Write-Host "You are not logged in to Azure CLI. Please login first." -ForegroundColor Red
    Write-Host "Running: az login" -ForegroundColor White
    az login
}

# Set subscription
Write-Host "`nSetting subscription context to '$subscription'..." -ForegroundColor Yellow
az account set --subscription $subscription

# Execute Azure CLI commands to add RBAC role assignments
Write-Host "`nExecuting Azure CLI commands to add RBAC role assignments..." -ForegroundColor Yellow
Write-Host "Would you like to automatically add the required RBAC role assignments? (Y/N)" -ForegroundColor Cyan
$confirmation = Read-Host

if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
    # Add role assignments for the first Cosmos DB account
    Write-Host "`nAdding RBAC role assignments for $cosmosAccount1..." -ForegroundColor White
    
    Write-Host "Adding 'Cosmos DB Operator' role..." -ForegroundColor Gray
    az role assignment create --assignee "$principalId" --role "Cosmos DB Operator" --scope "/subscriptions/$subscription/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccount1"
    
    Write-Host "Adding 'Cosmos DB Account Reader Role' role..." -ForegroundColor Gray
    az role assignment create --assignee "$principalId" --role "Cosmos DB Account Reader Role" --scope "/subscriptions/$subscription/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccount1"
    
    # Add role assignments for the second Cosmos DB account
    Write-Host "`nAdding RBAC role assignments for $cosmosAccount2..." -ForegroundColor White
    
    Write-Host "Adding 'Cosmos DB Operator' role..." -ForegroundColor Gray
    az role assignment create --assignee "$principalId" --role "Cosmos DB Operator" --scope "/subscriptions/$subscription/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccount2"
    
    Write-Host "Adding 'Cosmos DB Account Reader Role' role..." -ForegroundColor Gray
    az role assignment create --assignee "$principalId" --role "Cosmos DB Account Reader Role" --scope "/subscriptions/$subscription/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccount2"
    
    Write-Host "`nRole assignments completed successfully." -ForegroundColor Green
} else {
    Write-Host "`nSkipping automatic role assignment. You can manually add roles using these commands:" -ForegroundColor Yellow
    Write-Host "# Assign Cosmos DB Operator Role (for write access)" -ForegroundColor Gray
    Write-Host "az role assignment create --assignee `"$principalId`" --role `"Cosmos DB Operator`" --scope `"/subscriptions/$subscription/resourceGroups/$resourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$cosmosAccount1`"" -ForegroundColor Gray
}

# Note about waiting for propagation
Write-Host "`nNote: After assigning roles, it may take a few minutes (up to 30) for permissions to propagate." -ForegroundColor Yellow

# Verification steps
Write-Host "`nVerification Steps:" -ForegroundColor Yellow
Write-Host "Would you like to verify if permissions were properly set? (Y/N)" -ForegroundColor Cyan
$verifyConfirmation = Read-Host

if ($verifyConfirmation -eq 'Y' -or $verifyConfirmation -eq 'y') {
    Write-Host "`nVerifying permissions for $cosmosAccount1..." -ForegroundColor White
    Write-Host "Running: az cosmosdb database list --name $cosmosAccount1 --resource-group $resourceGroup" -ForegroundColor Gray
    az cosmosdb database list --name $cosmosAccount1 --resource-group $resourceGroup
    
    Write-Host "`nVerifying permissions for $cosmosAccount2..." -ForegroundColor White
    Write-Host "Running: az cosmosdb database list --name $cosmosAccount2 --resource-group $resourceGroup" -ForegroundColor Gray
    az cosmosdb database list --name $cosmosAccount2 --resource-group $resourceGroup
} else {
    Write-Host "`nSkipping verification. You can verify permissions manually by running:" -ForegroundColor Yellow
    Write-Host "az cosmosdb database list --name $cosmosAccount1 --resource-group $resourceGroup" -ForegroundColor Gray
}

# Next steps after fixing permissions
Write-Host "`nAfter fixing permissions, run the Darbot Agent Engine with Azure integration:" -ForegroundColor Yellow
Write-Host ".\scripts\run_servers.ps1 -UseAzure ``" -ForegroundColor White
Write-Host "    -AzureOpenAIEndpoint 'https://cat-studio-foundry.openai.azure.com/' ``" -ForegroundColor White
Write-Host "    -AzureResourceGroup 'Studio-CAT' ``" -ForegroundColor White
Write-Host "    -AzureAIProjectName 'cat-studio-foundry'" -ForegroundColor White

Write-Host "`nThis will set up the Darbot Agent Engine to use real Azure services instead of mock data." -ForegroundColor White
Write-Host "For more details, see: COSMOS_RBAC_SETUP.md and RUNNING_WITH_AZURE.md" -ForegroundColor Cyan

# Final check with Azure MCP CLI (optional)
Write-Host "`nAlternatively, you can check the CosmosDB permissions using Azure MCP CLI:" -ForegroundColor Yellow
Write-Host "1. Wait for permissions to propagate (up to 30 minutes)" -ForegroundColor White
Write-Host "2. Run the following MCP command:" -ForegroundColor White
Write-Host "   azmcp cosmos database list --subscription $subscription --account-name $cosmosAccount1" -ForegroundColor Gray
