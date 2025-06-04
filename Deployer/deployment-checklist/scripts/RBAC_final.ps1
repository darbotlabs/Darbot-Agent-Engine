<#
.SYNOPSIS
    Comprehensive CosmosDB RBAC fixer and validator for Darbot Agent Engine.

.DESCRIPTION
    This script applies necessary RBAC permissions to CosmosDB accounts,
    handles permission propagation delays, and validates the configuration
    by testing actual connectivity from the application context.

.PARAMETER PrincipalId
    The Azure AD principal ID (service principal or user) that needs access.

.PARAMETER MaxRetries
    Maximum number of verification attempts (default: 10).

.PARAMETER RetryIntervalSeconds
    Time to wait between retries in seconds (default: 30).

.PARAMETER TestDatabaseName
    Name of the database to create/use for testing permissions.

.PARAMETER TestContainerName
    Name of the container to create/use for testing permissions.

.EXAMPLE
    .\fix_cosmos_rbac.ps1 -PrincipalId "ebb01e50-f389-4f45-84a3-8d588f0b5bab"

.NOTES
    Requires: Az PowerShell modules, Azure CLI
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$PrincipalId = "ebb01e50-f389-4f45-84a3-8d588f0b5bab",
    
    [Parameter(Mandatory = $false)]
    [string]$Subscription = "99fc47d1-e510-42d6-bc78-63cac040a902",
    
    [Parameter(Mandatory = $false)]
    [string]$ResourceGroup = "Studio-CAT",
    
    [Parameter(Mandatory = $false)]
    [string[]]$CosmosAccounts = @("darbot-cosmos-dev", "darbot-cosmos-dev2"),
    
    [Parameter(Mandatory = $false)]
    [int]$MaxRetries = 10,
    
    [Parameter(Mandatory = $false)]
    [int]$RetryIntervalSeconds = 30,
    
    [Parameter(Mandatory = $false)]
    [string]$TestDatabaseName = "darbot",
    
    [Parameter(Mandatory = $false)]
    [string]$TestContainerName = "plans",
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipVerification = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$ForceReassign = $false
)

#region Functions

function Write-StatusMessage {
    param (
        [string]$Message,
        [string]$Type = "Info" # Info, Success, Warning, Error
    )
    
    $colors = @{
        "Info" = "Cyan"
        "Success" = "Green"
        "Warning" = "Yellow"
        "Error" = "Red"
        "Emphasis" = "Magenta"
    }
    
    $prefix = switch ($Type) {
        "Info" { "ℹ️ " }
        "Success" { "✅ " }
        "Warning" { "⚠️ " }
        "Error" { "❌ " }
        "Emphasis" { "🔍 " }
        default { "" }
    }
    
    Write-Host "$prefix$Message" -ForegroundColor $colors[$Type]
}

function Test-AzureCliLogin {
    try {
        $loginStatus = az account show --query name -o tsv 2>$null
        return ($null -ne $loginStatus)
    }
    catch {
        return $false
    }
}

function Test-CosmosDBAccess {
    param (
        [string]$AccountName
    )
    
    try {
        Write-StatusMessage "Testing read access to Cosmos DB account '$AccountName'..." -Type "Info"
        $result = az cosmosdb database list --name $AccountName --resource-group $ResourceGroup 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "Failed to list databases on '$AccountName'. Error: $result" -Type "Error"
            return $false
        }
        
        Write-StatusMessage "Successfully listed databases on '$AccountName'" -Type "Success"
        
        # Try to create a database (if it doesn't exist) to validate write permission
        Write-StatusMessage "Testing write access by ensuring test database exists..." -Type "Info"
        $dbExists = az cosmosdb database exists --name $AccountName --resource-group $ResourceGroup --db-name $TestDatabaseName --query "exists" -o tsv
        
        if ($dbExists -ne "true") {
            Write-StatusMessage "Creating test database '$TestDatabaseName'..." -Type "Info"
            az cosmosdb database create --name $AccountName --resource-group $ResourceGroup --db-name $TestDatabaseName 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-StatusMessage "Failed to create test database. This suggests incomplete write permissions." -Type "Warning"
                return $false
            }
        }
        
        # Try to create or access a container
        Write-StatusMessage "Testing container access..." -Type "Info"
        $containerExists = az cosmosdb sql container exists --account-name $AccountName --resource-group $ResourceGroup --database-name $TestDatabaseName --name $TestContainerName --query "exists" -o tsv
        
        if ($containerExists -ne "true") {
            Write-StatusMessage "Creating test container '$TestContainerName'..." -Type "Info"
            az cosmosdb sql container create --account-name $AccountName --resource-group $ResourceGroup --database-name $TestDatabaseName --name $TestContainerName --partition-key-path "/id" --throughput 400 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-StatusMessage "Failed to create test container. This suggests incomplete container management permissions." -Type "Warning"
                return $false
            }
        }
        
        # Try to read a container to verify data plane access
        Write-StatusMessage "Testing data plane access..." -Type "Info"
        $containerDetails = az cosmosdb sql container show --account-name $AccountName --resource-group $ResourceGroup --database-name $TestDatabaseName --name $TestContainerName 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "Failed to read container details. This suggests incomplete data plane permissions." -Type "Warning"
            return $false
        }
        
        Write-StatusMessage "Successfully verified full access to Cosmos DB account '$AccountName'" -Type "Success"
        return $true
    }
    catch {
        Write-StatusMessage "Exception during Cosmos DB access test: $_" -Type "Error"
        return $false
    }
}

function Apply-CosmosRBAC {
    param (
        [string]$AccountName,
        [string]$PrincipalToAssign
    )
    
    $requiredRoles = @(
        "Cosmos DB Built-in Data Contributor",
        "DocumentDB Account Contributor",
        "Cosmos DB Operator"
    )
    
    $accountScope = "/subscriptions/$Subscription/resourceGroups/$ResourceGroup/providers/Microsoft.DocumentDB/databaseAccounts/$AccountName"
    
    Write-StatusMessage "Applying RBAC permissions for account: $AccountName" -Type "Emphasis"
    
    # Check existing role assignments
    $existingAssignments = az role assignment list --assignee $PrincipalToAssign --scope $accountScope --query "[].roleDefinitionName" -o tsv
    
    foreach ($role in $requiredRoles) {
        $hasRole = $existingAssignments -contains $role
        
        if ($hasRole -and -not $ForceReassign) {
            Write-StatusMessage "Role '$role' is already assigned to principal" -Type "Info"
        }
        else {
            if ($ForceReassign -and $hasRole) {
                Write-StatusMessage "Removing existing role assignment for '$role' before reassigning..." -Type "Info"
                az role assignment delete --assignee $PrincipalToAssign --role $role --scope $accountScope
            }
            
            Write-StatusMessage "Assigning role: $role" -Type "Info"
            $result = az role assignment create --assignee $PrincipalToAssign --role $role --scope $accountScope 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-StatusMessage "Failed to assign role '$role'. Error: $result" -Type "Error"
            }
            else {
                Write-StatusMessage "Successfully assigned role: $role" -Type "Success"
            }
        }
    }
}

function Test-ApplicationAccess {
    param (
        [string]$AccountName
    )
    
    $appTestScript = @"
using Microsoft.Azure.Cosmos;
using Azure.Identity;
using System;
using System.Threading.Tasks;

namespace CosmosTest
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Use DefaultAzureCredential - same as the application
            var credential = new DefaultAzureCredential();
            
            // Variables from command line
            string endpoint = args[0];
            string databaseName = args[1];
            string containerName = args[2];
            
            Console.WriteLine($"Testing connection to {endpoint} with DefaultAzureCredential");
            
            try
            {
                // Create a new CosmosClient instance with AAD auth
                using CosmosClient client = new CosmosClient(endpoint, credential);
                
                // Try to get a reference to the database
                Console.WriteLine($"Getting database: {databaseName}");
                Database database = client.GetDatabase(databaseName);
                
                // Try to get a reference to the container
                Console.WriteLine($"Getting container: {containerName}");
                Container container = database.GetContainer(containerName);
                
                // Try to query the container (this will verify permissions)
                Console.WriteLine("Executing query...");
                var query = new QueryDefinition("SELECT TOP 1 * FROM c");
                var iterator = container.GetItemQueryIterator<dynamic>(query);
                
                // Execute the query
                var response = await iterator.ReadNextAsync();
                
                Console.WriteLine($"Query executed successfully. Request charge: {response.RequestCharge} RU");
                Console.WriteLine("COSMOS_ACCESS_TEST: SUCCESS");
                return;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"COSMOS_ACCESS_TEST: FAILED");
                Console.WriteLine($"Error: {ex.Message}");
                Console.WriteLine($"Full error: {ex}");
                return;
            }
        }
    }
}
"@
    
    $tempDir = Join-Path $env:TEMP "CosmosTest"
    if (-not (Test-Path $tempDir)) {
        New-Item -ItemType Directory -Path $tempDir | Out-Null
    }
    
    $projectFile = @"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.Azure.Cosmos" Version="3.37.0" />
    <PackageReference Include="Azure.Identity" Version="1.10.4" />
  </ItemGroup>
</Project>
"@
    
    $programPath = Join-Path $tempDir "Program.cs"
    $projectPath = Join-Path $tempDir "CosmosTest.csproj"
    
    Write-StatusMessage "Creating test application to verify access using DefaultAzureCredential..." -Type "Info"
    Set-Content -Path $programPath -Value $appTestScript
    Set-Content -Path $projectPath -Value $projectFile
    
    try {
        Push-Location $tempDir
        Write-StatusMessage "Building test application..." -Type "Info"
        dotnet build -c Release -o ./bin | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "Failed to build test application" -Type "Error"
            return $false
        }
        
        $endpoint = "https://$AccountName.documents.azure.com:443/"
        Write-StatusMessage "Running test with DefaultAzureCredential against $endpoint..." -Type "Emphasis"
        $output = dotnet run --no-build -- $endpoint $TestDatabaseName $TestContainerName
        
        if ($output -contains "COSMOS_ACCESS_TEST: SUCCESS") {
            Write-StatusMessage "Application successfully connected to Cosmos DB using DefaultAzureCredential!" -Type "Success"
            return $true
        }
        else {
            $errorMsg = $output -join "`n"
            Write-StatusMessage "Application test failed: $errorMsg" -Type "Error"
            return $false
        }
    }
    catch {
        Write-StatusMessage "Exception running application test: $_" -Type "Error"
        return $false
    }
    finally {
        Pop-Location
    }
}

#endregion

#region Main Script

Write-StatusMessage "=======================================================" -Type "Emphasis"
Write-StatusMessage "      COSMOS DB RBAC PERMISSIONS FIXER & VALIDATOR     " -Type "Emphasis"
Write-StatusMessage "=======================================================" -Type "Emphasis"

Write-StatusMessage "This script will apply and validate RBAC permissions for CosmosDB accounts" -Type "Info"
Write-StatusMessage "Parameters:" -Type "Info"
Write-StatusMessage "- Principal ID: $PrincipalId" -Type "Info"
Write-StatusMessage "- Subscription: $Subscription" -Type "Info"
Write-StatusMessage "- Resource Group: $ResourceGroup" -Type "Info"
Write-StatusMessage "- Cosmos Accounts: $($CosmosAccounts -join ', ')" -Type "Info"
Write-StatusMessage "- Test Database: $TestDatabaseName" -Type "Info"
Write-StatusMessage "- Test Container: $TestContainerName" -Type "Info"

# Check if Azure CLI is installed
if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    Write-StatusMessage "Azure CLI is not installed or not in PATH" -Type "Error"
    Write-StatusMessage "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -Type "Info"
    exit 1
}

# Check if logged in to Azure CLI
if (-not (Test-AzureCliLogin)) {
    Write-StatusMessage "Not logged in to Azure CLI. Initiating login..." -Type "Warning"
    az login
    
    if (-not (Test-AzureCliLogin)) {
        Write-StatusMessage "Failed to login to Azure CLI" -Type "Error"
        exit 1
    }
}

# Set the subscription context
Write-StatusMessage "Setting subscription context to '$Subscription'..." -Type "Info"
az account set --subscription $Subscription

if ($LASTEXITCODE -ne 0) {
    Write-StatusMessage "Failed to set subscription context" -Type "Error"
    exit 1
}

# Validate principal exists
Write-StatusMessage "Validating principal ID '$PrincipalId'..." -Type "Info"
$principalExists = az ad sp show --id $PrincipalId 2>$null

if ($LASTEXITCODE -ne 0) {
    # Try as a user
    $principalExists = az ad user show --id $PrincipalId 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Principal ID does not exist or you don't have permission to view it" -Type "Warning"
        $confirmContinue = Read-Host "Continue anyway? (Y/N)"
        
        if ($confirmContinue -ne 'Y' -and $confirmContinue -ne 'y') {
            Write-StatusMessage "Operation canceled by user" -Type "Warning"
            exit 0
        }
    }
}

# Process each Cosmos DB account
$allAccountsSuccess = $true

foreach ($account in $CosmosAccounts) {
    Write-StatusMessage "=======================================================" -Type "Info"
    Write-StatusMessage "Processing Cosmos DB account: $account" -Type "Emphasis"
    
    # Check if account exists
    $accountExists = az cosmosdb show --name $account --resource-group $ResourceGroup --query id -o tsv 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Cosmos DB account '$account' does not exist in resource group '$ResourceGroup'" -Type "Error"
        $allAccountsSuccess = $false
        continue
    }
    
    # Apply RBAC roles
    Apply-CosmosRBAC -AccountName $account -PrincipalToAssign $PrincipalId
    
    if (-not $SkipVerification) {
        # Wait and verify permissions with retry logic
        $retryCount = 0
        $success = $false
        
        Write-StatusMessage "Starting verification with up to $MaxRetries attempts ($RetryIntervalSeconds seconds between attempts)..." -Type "Info"
        
        while (-not $success -and $retryCount -lt $MaxRetries) {
            $retryCount++
            Write-StatusMessage "Verification attempt $retryCount of $MaxRetries..." -Type "Info"
            
            # Test CLI access
            $success = Test-CosmosDBAccess -AccountName $account
            
            if (-not $success) {
                if ($retryCount -lt $MaxRetries) {
                    Write-StatusMessage "Waiting $RetryIntervalSeconds seconds for permissions to propagate..." -Type "Warning"
                    Start-Sleep -Seconds $RetryIntervalSeconds
                }
                else {
                    Write-StatusMessage "Maximum retries reached. Unable to verify permissions." -Type "Error"
                    $allAccountsSuccess = $false
                }
            }
        }
        
        # Test access using the application authentication method
        if ($success) {
            Write-StatusMessage "Testing access with DefaultAzureCredential (same as the application)..." -Type "Emphasis"
            $appSuccess = Test-ApplicationAccess -AccountName $account
            
            if (-not $appSuccess) {
                Write-StatusMessage "Application access test failed. The Darbot Agent Engine may still encounter permission issues." -Type "Error"
                $allAccountsSuccess = $false
            }
        }
    }
    else {
        Write-StatusMessage "Verification skipped as requested" -Type "Warning"
    }
}

Write-StatusMessage "=======================================================" -Type "Emphasis"
if ($allAccountsSuccess) {
    Write-StatusMessage "ALL COSMOS DB ACCOUNTS PROCESSED SUCCESSFULLY!" -Type "Success"
    
    if (-not $SkipVerification) {
        Write-StatusMessage "Permissions have been verified and are working correctly" -Type "Success"
    }
    else {
        Write-StatusMessage "Permissions have been applied but not verified" -Type "Warning"
    }
    
    Write-StatusMessage "You can now run Darbot Agent Engine with Azure resources:" -Type "Info"
    Write-StatusMessage ".\scripts\run_servers.ps1 -UseAzure" -Type "Info"
}
else {
    Write-StatusMessage "SOME COSMOS DB ACCOUNTS FAILED PROCESSING OR VERIFICATION" -Type "Error"
    Write-StatusMessage "Review the logs above for specific issues" -Type "Warning"
    
    Write-StatusMessage "Common solutions:" -Type "Info"
    Write-StatusMessage "1. Wait longer for permission propagation (up to 30 minutes)" -Type "Info"
    Write-StatusMessage "2. Ensure the principal has the Owner role on the resource group" -Type "Info"
    Write-StatusMessage "3. Try running with -ForceReassign to remove and recreate role assignments" -Type "Info"
    Write-StatusMessage "4. Check if the principal is still valid and active" -Type "Info"
}

Write-StatusMessage "=======================================================" -Type "Emphasis"

#endregion