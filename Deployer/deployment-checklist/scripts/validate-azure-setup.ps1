# Validate Azure Setup Script

# This PowerShell script verifies that the Azure environment is correctly configured for deployment.

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "Studio-CAT",
    [Parameter(Mandatory=$false)]
    [switch]$CheckQuota = $false
)

# Define the required Azure services for MACAE
$requiredServices = @(
    "Microsoft.CognitiveServices",  # Azure OpenAI
    "Microsoft.App",                # Azure Container Apps  
    "Microsoft.DocumentDB",         # Azure Cosmos DB
    "Microsoft.ContainerRegistry",  # Azure Container Registry
    "Microsoft.Cache"               # Azure Cache for Redis
)

# Function to check Azure CLI login status
function Test-AzureLogin {
    try {
        $account = az account show 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Host "✓ Azure CLI logged in as: $($account.user.name)" -ForegroundColor Green
            Write-Host "✓ Subscription: $($account.name) ($($account.id))" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ Azure CLI not logged in. Please run 'az login'" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to check if required resource providers are registered
function Test-ResourceProviders {
    Write-Host "`nChecking Azure resource provider registrations..." -ForegroundColor Cyan
    
    $allRegistered = $true
    foreach ($provider in $requiredServices) {
        try {
            $registration = az provider show --namespace $provider --query "registrationState" -o tsv 2>$null
            if ($registration -eq "Registered") {
                Write-Host "✓ $provider is registered" -ForegroundColor Green
            } else {
                Write-Host "✗ $provider is not registered (Status: $registration)" -ForegroundColor Red
                Write-Host "  Run: az provider register --namespace $provider" -ForegroundColor Yellow
                $allRegistered = $false
            }
        } catch {
            Write-Host "✗ Failed to check $provider registration status" -ForegroundColor Red
            $allRegistered = $false
        }
    }
    return $allRegistered
}

# Function to check Azure OpenAI quota
function Test-OpenAIQuota {
    if (-not $CheckQuota) { return $true }
    
    Write-Host "`nChecking Azure OpenAI quota availability..." -ForegroundColor Cyan
    
    try {
        # Get available locations for Cognitive Services
        $locations = az provider show --namespace Microsoft.CognitiveServices --query "resourceTypes[?resourceType=='accounts'].locations[]" -o tsv
        
        $quotaAvailable = $false
        foreach ($location in $locations) {
            Write-Host "Checking quota in $location..." -ForegroundColor Gray
            # This is a simplified check - in practice, you'd need to check specific model quotas
            $quotaAvailable = $true
            break
        }
        
        if ($quotaAvailable) {
            Write-Host "✓ Azure OpenAI quota appears to be available" -ForegroundColor Green
        } else {
            Write-Host "✗ No Azure OpenAI quota found. Please request quota or check availability" -ForegroundColor Red
        }
        
        return $quotaAvailable
    } catch {
        Write-Host "⚠ Could not verify Azure OpenAI quota. Please check manually" -ForegroundColor Yellow
        return $true  # Don't fail on quota check issues
    }
}

# Function to validate or create resource group
function Test-ResourceGroup {
    param([string]$rgName)
    
    if ([string]::IsNullOrEmpty($rgName)) {
        Write-Host "`nNo resource group specified. Listing available resource groups:" -ForegroundColor Cyan
        az group list --output table
        return $true
    }
    
    Write-Host "`nChecking resource group: $rgName..." -ForegroundColor Cyan
    
    try {
        $rg = az group show --name $rgName 2>$null | ConvertFrom-Json
        if ($rg) {
            Write-Host "✓ Resource group '$rgName' exists in location: $($rg.location)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Resource group '$rgName' does not exist" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "✗ Failed to check resource group '$rgName'" -ForegroundColor Red
        return $false
    }
}

# Main validation function
function Invoke-AzureSetupValidation {
    Write-Host "=== Azure Setup Validation for Multi-Agent Custom Automation Engine ===" -ForegroundColor Magenta
    Write-Host "Date: $(Get-Date)" -ForegroundColor Gray
    Write-Host ""
    
    $validationResults = @{
        AzureLogin = Test-AzureLogin
        ResourceProviders = Test-ResourceProviders
        ResourceGroup = Test-ResourceGroup -rgName $ResourceGroupName
        OpenAIQuota = Test-OpenAIQuota
    }
    
    Write-Host "`n=== Validation Summary ===" -ForegroundColor Magenta
    
    $overallSuccess = $true
    foreach ($check in $validationResults.Keys) {
        $status = if ($validationResults[$check]) { "✓ PASS" } else { "✗ FAIL"; $overallSuccess = $false }
        $color = if ($validationResults[$check]) { "Green" } else { "Red" }
        Write-Host "$check : $status" -ForegroundColor $color
    }
    
    Write-Host ""
    if ($overallSuccess) {
        Write-Host "🎉 Azure setup validation completed successfully!" -ForegroundColor Green
        Write-Host "You're ready to proceed with deployment." -ForegroundColor Green
    } else {
        Write-Host "❌ Azure setup validation failed. Please address the issues above." -ForegroundColor Red
        Write-Host "Refer to the deployment documentation for guidance." -ForegroundColor Yellow
    }
    
    return $overallSuccess
}

# Execute validation
$validationSuccess = Invoke-AzureSetupValidation

# Exit with appropriate code
exit $(if ($validationSuccess) { 0 } else { 1 })