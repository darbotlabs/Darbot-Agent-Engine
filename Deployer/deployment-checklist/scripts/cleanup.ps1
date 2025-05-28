# Cleanup Script for Deployment

# This script is used to clean up resources after deployment, ensuring that no unnecessary resources remain.

# Script parameters
param(
    [string]$ResourceGroupName = "Studio-CAT",
    [switch]$Force = $false
)

# Function to remove the resource group using Azure CLI
function Remove-AzureResourceGroup {
    param (
        [string]$resourceGroupName,
        [bool]$force
    )
    
    # Check if the resource group exists
    Write-Host "Checking if resource group '$resourceGroupName' exists..." -ForegroundColor Cyan
    $exists = az group exists --name $resourceGroupName 2>$null
    
    if ($exists -eq 'true') {
        # Provide warning and confirmation unless Force is specified
        if (-not $force) {
            Write-Host "`n⚠️ WARNING: You are about to delete resource group '$resourceGroupName' and ALL resources in it!" -ForegroundColor Red -BackgroundColor Yellow
            Write-Host "This action CANNOT be undone and will delete all Azure resources in this group." -ForegroundColor Red
            
            $confirm = Read-Host "Type 'YES' (all caps) to confirm deletion or anything else to cancel"
            
            if ($confirm -ne 'YES') {
                Write-Host "Deletion cancelled." -ForegroundColor Green
                return
            }
        }
        
        # Delete the resource group
        Write-Host "Deleting resource group '$resourceGroupName'..." -ForegroundColor Yellow
        az group delete --name $resourceGroupName --yes --no-wait
        
        Write-Host "Resource group deletion initiated. This may take several minutes to complete." -ForegroundColor Yellow
        Write-Host "You can check the status with: az group show --name $resourceGroupName" -ForegroundColor Gray
    } else {
        Write-Host "Resource group '$resourceGroupName' does not exist." -ForegroundColor Yellow
    }
}

# Main script execution
Write-Host "=== Cleanup for Multi-Agent Custom Automation Engine ===" -ForegroundColor Magenta
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor Cyan
Write-Host "Force Mode: $Force" -ForegroundColor Cyan
Write-Host ""

# Call the function to remove the resource group
Remove-AzureResourceGroup -resourceGroupName $ResourceGroupName -force $Force

# Additional cleanup tasks can be added here as needed
# For example, removing specific resources or cleaning up logs

Write-Host "`nCleanup process completed." -ForegroundColor Green