# filepath: D:\0GH_PROD\Darbot-Agent-Engine\run_fixed_ports.ps1
# Thought into existence by Darbot

Write-Host "Starting Darbot Agent Engine with fixed ports..." -ForegroundColor Cyan
# Kill any processes using the ports we need
Get-Process | Where-Object {$_.MainWindowTitle -match "Python" -or $_.ProcessName -match "python"} | Stop-Process -Force -ErrorAction SilentlyContinue

# Start the frontend server on port 8008
$frontendJob = Start-Job -ScriptBlock {
    cd D:\0GH_PROD\Darbot-Agent-Engine\src\frontend
    python -m uvicorn frontend_server:app --host 127.0.0.1 --port 8008
}

# Start the backend server with Azure integration
$backendJob = Start-Job -ScriptBlock {
    cd D:\0GH_PROD\Darbot-Agent-Engine
    pwsh .\scripts\run_servers.ps1 -UseAzure `
        -AzureOpenAIEndpoint "https://cat-studio-foundry.openai.azure.com/" `
        -AzureResourceGroup "Studio-CAT" `
        -AzureAIProjectName "cat-studio-foundry" `
        -BackendPort 8009 `
        -FrontendPort 8010
}

Write-Host "Jobs started. Press Ctrl+C to stop all jobs and exit."
Write-Host "Frontend available at: http://localhost:8008"
Write-Host "Backend will be available at: http://localhost:8009"

try {
    while ($true) {
        Receive-Job -Job $frontendJob
        Receive-Job -Job $backendJob
        Start-Sleep -Seconds 1
    }
}
finally {
    # Clean up
    Stop-Job -Job $frontendJob, $backendJob
    Remove-Job -Job $frontendJob, $backendJob
    
    Write-Host "Services stopped" -ForegroundColor Yellow
}
