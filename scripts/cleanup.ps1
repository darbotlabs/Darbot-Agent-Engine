# Cleanup Script for Deployment

# This script is used to clean up resources after deployment, ensuring that no unnecessary resources remain.

# Define the Azure resource group and other parameters
$resourceGroupName = "Studio-CAT"  # Using Studio-CAT resource group
$location = "eastus"  # East US location

# Function to remove the resource group
function Remove-ResourceGroup {
    param (
        [string]$resourceGroupName
    )
    
    # Check if the resource group exists
    if (Get-AzResourceGroup -Name $resourceGroupName -ErrorAction SilentlyContinue) {
        # Remove the resource group and all its resources
        Remove-AzResourceGroup -Name $resourceGroupName -Force
        Write-Host "Resource group '$resourceGroupName' and all its resources have been deleted."
    } else {
        Write-Host "Resource group '$resourceGroupName' does not exist."
    }
}

# Call the function to remove the resource group
Remove-ResourceGroup -resourceGroupName $resourceGroupName

# Additional cleanup tasks can be added here as needed
# For example, removing specific resources or cleaning up logs

# End of cleanup script