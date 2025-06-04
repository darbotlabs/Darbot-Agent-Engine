# Thought into existence by Darbot
# Azure CLI Token Cache Refresh Script
# This script will clear the Azure CLI token cache and refresh your login

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "        AZURE CLI TOKEN CACHE REFRESH TOOL          " -ForegroundColor Cyan
Write-Host "=====================================================" -ForegroundColor Cyan

Write-Host "`nProblem: Azure CLI is experiencing decryption errors" -ForegroundColor Yellow
Write-Host "This script will clear your Azure CLI token cache and refresh your login." -ForegroundColor White

# Confirm before proceeding
Write-Host "`nWould you like to clear your Azure CLI token cache and refresh login? (Y/N)" -ForegroundColor Cyan
$confirmation = Read-Host

if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
    # Sign out from Azure CLI
    Write-Host "`nSigning out from Azure CLI..." -ForegroundColor Yellow
    az logout
    
    # Remove token cache file
    $tokenCachePath = "$env:USERPROFILE\.azure\msal_token_cache.bin"
    if (Test-Path $tokenCachePath) {
        Write-Host "Removing Azure CLI token cache..." -ForegroundColor Yellow
        Remove-Item -Path $tokenCachePath -Force
        Write-Host "Token cache removed successfully." -ForegroundColor Green
    } else {
        Write-Host "Token cache file not found at $tokenCachePath." -ForegroundColor Yellow
    }
    
    # Clear other potential problematic files
    Write-Host "Cleaning additional Azure CLI cache files..." -ForegroundColor Yellow
    if (Test-Path "$env:USERPROFILE\.azure\accessTokens.json") {
        Remove-Item -Path "$env:USERPROFILE\.azure\accessTokens.json" -Force
    }
    
    if (Test-Path "$env:USERPROFILE\.azure\azureProfile.json") {
        Write-Host "Backing up Azure profile before clearing..." -ForegroundColor Yellow
        Copy-Item -Path "$env:USERPROFILE\.azure\azureProfile.json" -Destination "$env:USERPROFILE\.azure\azureProfile.json.bak"
        Remove-Item -Path "$env:USERPROFILE\.azure\azureProfile.json" -Force
    }
    
    # Login again
    Write-Host "`nLogging in to Azure CLI again..." -ForegroundColor Yellow
    az login
    
    # Set subscription
    $subscription = "99fc47d1-e510-42d6-bc78-63cac040a902" # FastTrack Azure Commercial Shared POC
    Write-Host "`nSetting subscription to $subscription..." -ForegroundColor Yellow
    az account set --subscription $subscription
    
    # Test if decryption issue is resolved
    Write-Host "`nTesting if decryption issue is resolved..." -ForegroundColor Yellow
    Write-Host "Running: az account show" -ForegroundColor Gray
    az account show
    
    Write-Host "`nNow run the cosmos_rbac_fix_guide.ps1 script again to set up RBAC permissions." -ForegroundColor Cyan
} else {
    Write-Host "`nOperation cancelled. No changes were made." -ForegroundColor Yellow
}

Write-Host "`n=====================================================" -ForegroundColor Cyan
Write-Host "If you continue to experience issues, please follow the manual steps in:" -ForegroundColor White
Write-Host "PORTAL_COSMOS_RBAC_FIX.md" -ForegroundColor White
Write-Host "=====================================================" -ForegroundColor Cyan
