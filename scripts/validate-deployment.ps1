# Validate Deployment Script

# This PowerShell script checks the deployment status and ensures that all components are functioning as expected.

# Define the function to validate deployment using Azure CLI
function Validate-Deployment {
    param (
        [string]$resourceGroupName,
        [string]$deploymentName
    )

    # Check if the resource group exists using Azure CLI
    Write-Host "Checking resource group: $resourceGroupName..." -ForegroundColor Cyan
    $resourceGroupExists = az group exists --name $resourceGroupName 2>$null
    if ($resourceGroupExists -eq "false") {
        Write-Host "Resource group '$resourceGroupName' does not exist." -ForegroundColor Red
        return $false
    }
    Write-Host "✓ Resource group '$resourceGroupName' exists." -ForegroundColor Green

    # Check the deployment status using Azure CLI
    Write-Host "Checking deployment: $deploymentName..." -ForegroundColor Cyan
    try {
        $deploymentJson = az deployment group show --resource-group $resourceGroupName --name $deploymentName 2>$null | ConvertFrom-Json
        if (-not $deploymentJson) {
            Write-Host "Deployment '$deploymentName' does not exist in resource group '$resourceGroupName'." -ForegroundColor Red
            
            # List available deployments for reference
            Write-Host "`nAvailable deployments in resource group '$resourceGroupName':" -ForegroundColor Yellow
            az deployment group list --resource-group $resourceGroupName --query "[].name" -o tsv
            
            return $false
        }

        # Validate the deployment state
        if ($deploymentJson.properties.provisioningState -eq 'Succeeded') {
            Write-Host "✓ Deployment '$deploymentName' in resource group '$resourceGroupName' succeeded." -ForegroundColor Green
            return $true
        } else {
            Write-Host "✗ Deployment '$deploymentName' in resource group '$resourceGroupName' failed with state: $($deploymentJson.properties.provisioningState)." -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "Error checking deployment status: $_" -ForegroundColor Red
        return $false
    }
}

# Script parameters
param(
    [string]$ResourceGroupName = "Studio-CAT",
    [string]$DeploymentName = "0ac64f82-105c-4025-9b3d-cf5c4494c52d"
)

# Main script execution

# Display validation information
Write-Host "=== Deployment Validation for Multi-Agent Custom Automation Engine ===" -ForegroundColor Magenta
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "Deployment Name: $DeploymentName" -ForegroundColor Cyan
Write-Host ""

# Call the validation function
$validationResult = Validate-Deployment -resourceGroupName $ResourceGroupName -deploymentName $DeploymentName

if ($validationResult) {
    Write-Host "`n🎉 All components are functioning as expected." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n❌ Deployment validation failed. Please check the errors above." -ForegroundColor Red
    exit 1
}