# Configure Local Development Environment Variables
# Thought into existence by Darbot

# Authentication and Authorization Settings
$env:AUTH_ENABLED = "false"
$env:CLIENT_PRINCIPAL = "mock-client-principal-id"
$env:CLIENT_PRINCIPAL_ID = "12345678-abcd-efgh-ijkl-9876543210ab"
$env:CLIENT_PRINCIPAL_IDP = "mock-identity-provider" 
$env:CLIENT_PRINCIPAL_NAME = "Local User"

# Host and Network Settings
$env:HOST_NAME = "localhost"
$env:ORIGIN_URL = "http://localhost:3000"
$env:REFERER_URL = "http://localhost:3000/"
$env:APP_SERVICE_PROTO = "http"
$env:CLIENT_IP = "127.0.0.1"
$env:FORWARDED_PROTO = "http"
$env:ORIGINAL_URL = "/api"

# Backend and Frontend Configuration
$env:BACKEND_HOST = "0.0.0.0"
$env:BACKEND_PORT = "8001"  # Default backend port
$env:FRONTEND_PORT = "3000"  # Default frontend port

Write-Host "Local development environment variables configured."
Write-Host "Backend will use environment variables for authentication headers."
Write-Host "- Client Principal ID: $env:CLIENT_PRINCIPAL_ID"
Write-Host "- Client Principal Name: $env:CLIENT_PRINCIPAL_NAME"
Write-Host "- Authentication Provider: $env:CLIENT_PRINCIPAL_IDP"
Write-Host ""
Write-Host "You can customize these values by editing this script or setting environment variables before running."
Write-Host "To run with different user values, modify the environment variables directly."

# Return to previous directory
Write-Host "Environment ready for local development."
