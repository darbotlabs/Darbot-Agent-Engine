PS D:\0GH_PROD\Darbot-Agent-Engine> cat .\validate-deployment.ps1
Get-Content: Cannot find path 'D:\0GH_PROD\Darbot-Agent-Engine\validate-deployment.ps1' because it does not exist.
PS D:\0GH_PROD\Darbot-Agent-Engine> 
PS D:\0GH_PROD\Darbot-Agent-Engine> 
PS D:\0GH_PROD\Darbot-Agent-Engine> cat "D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts\validate-deployment.ps1"
# Validate Deployment Script

# This PowerShell script checks the deployment status and ensures that all components are functioning as expected.

# Script parameters
param(
    [string]$ResourceGroupName = "Studio-CAT",
    [string]$DeploymentName = "macae-deployment"  # Default name, can be overridden when calling the script
)

# Define the function to validate deployment using Azure CLI
function Test-Deployment {
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
PS D:\0GH_PROD\Darbot-Agent-Engine> 
PS D:\0GH_PROD\Darbot-Agent-Engine> 
PS D:\0GH_PROD\Darbot-Agent-Engine> 
PS D:\0GH_PROD\Darbot-Agent-Engine> cd .\Deployer\deployment-checklist\scripts\          
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> cat .\validate-deployment.ps1              
# Validate Deployment Script

# This PowerShell script checks the deployment status and ensures that all components are functioning as expected.

# Script parameters
param(
    [string]$ResourceGroupName = "Studio-CAT",
    [string]$DeploymentName = "macae-deployment"  # Default name, can be overridden when calling the script
)

# Define the function to validate deployment using Azure CLI
function Test-Deployment {
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
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> .\validate-deployment.ps1
=== Deployment Validation for Multi-Agent Custom Automation Engine ===
Resource Group: Studio-CAT
Deployment Name: 0ac64f82-105c-4025-9b3d-cf5c4494c52d

Checking resource group: Studio-CAT...
✓ Resource group 'Studio-CAT' exists.
Checking deployment: 0ac64f82-105c-4025-9b3d-cf5c4494c52d...
✓ Deployment '0ac64f82-105c-4025-9b3d-cf5c4494c52d' in resource group 'Studio-CAT' succeeded.

🎉 All components are functioning as expected.
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> Write-Host "=== Running Prerequisites Validation ===" -ForegroundColor Magenta; .\validate-prerequisites.ps1; Write-Host "`n=== Running Azure Setup Validation ===" -ForegroundColor Magenta; .\validate-azure-setup.ps1; Write-Host "`n=== Running Deployment Validation ===" -ForegroundColor Magenta; .\validate-deployment.ps1
=== Running Prerequisites Validation ===
azure-cli                         2.71.0 *

core                              2.71.0 *
telemetry                          1.1.0

Dependencies:
msal                            1.31.2b1
azure-mgmt-resource               23.1.1

Python location 'C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\python.exe'
Config directory 'C:\Users\dayour\.azure'
Extensions directory 'C:\Users\dayour\.azure\cliextensions'

Python (Windows) 3.12.8 (tags/v3.12.8:2dc476b, Dec  3 2024, 19:07:15) [MSC v.1942 32 bit (Intel)]

Legal docs and information: aka.ms/AzureCliLegal


You have 2 update(s) available. Consider updating your CLI installation with 'az upgrade'
Prerequisite met: Azure CLI is installed.
azd version 1.16.1 (commit ab0f744c38a641e66344dc5dd635b9d074edf5f7)
Prerequisite met: Azure Dev CLI is installed.
Docker version 28.1.1, build 4eba377
Prerequisite met: Docker is installed.
Prerequisite met: PowerShell is installed.
Prerequisite validation completed.

=== Running Azure Setup Validation ===
=== Azure Setup Validation for Multi-Agent Custom Automation Engine ===
Date: 05/27/2025 18:35:09

✓ Azure CLI logged in as: dayour@microsoft.com
✓ Subscription: FastTrack Azure Commercial Shared POC (99fc47d1-e510-42d6-bc78-63cac040a902)

Checking Azure resource provider registrations...
✓ Microsoft.CognitiveServices is registered
✓ Microsoft.App is registered
✓ Microsoft.DocumentDB is registered
✓ Microsoft.ContainerRegistry is registered
✓ Microsoft.Cache is registered

Checking resource group: Studio-CAT...
✓ Resource group 'Studio-CAT' exists in location: eastus

=== Validation Summary ===
AzureLogin : ✓ PASS
ResourceGroup : ✓ PASS
ResourceProviders : ✓ PASS
OpenAIQuota : ✓ PASS

🎉 Azure setup validation completed successfully!
You're ready to proceed with deployment.

=== Running Deployment Validation ===
=== Deployment Validation for Multi-Agent Custom Automation Engine ===
Resource Group: Studio-CAT
Deployment Name: 0ac64f82-105c-4025-9b3d-cf5c4494c52d

Checking resource group: Studio-CAT...
✓ Resource group 'Studio-CAT' exists.
Checking deployment: 0ac64f82-105c-4025-9b3d-cf5c4494c52d...
✓ Deployment '0ac64f82-105c-4025-9b3d-cf5c4494c52d' in resource group 'Studio-CAT' succeeded.

🎉 All components are functioning as expected.
PS D:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts> 