# Thought into existence by Darbot
# Script to validate each step in the next-steps.md document

Write-Host "Starting validation of Darbot Agent Engine steps..." -ForegroundColor Cyan

# Create backlog file if it doesn't exist
$backlogPath = "D:\0GH_PROD\Darbot-Agent-Engine\backlog.md"
if (-not (Test-Path $backlogPath)) {
    @"
# Darbot Agent Engine - Backlog

This file contains issues discovered during the validation process.

## Import Issues

"@ | Set-Content $backlogPath
    Write-Host "Created backlog.md file to document issues" -ForegroundColor Green
}

# Step 1: Validate backend server
Write-Host "`n[Step 1] Validating backend server..." -ForegroundColor Yellow

# Set PYTHONPATH correctly for PowerShell
Write-Host "Setting PYTHONPATH environment variable..." -ForegroundColor Cyan
$env:PYTHONPATH = "D:\0GH_PROD\Darbot-Agent-Engine\src"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Green

# Check if we have the ResponseFormat import issue
$agentFactoryPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\kernel_agents\agent_factory.py"
if (Test-Path $agentFactoryPath) {
    $content = Get-Content $agentFactoryPath -Raw
    if ($content -match "from azure.ai.projects.models import ResponseFormat") {
        Write-Host "Detected ResponseFormat import issue in agent_factory.py" -ForegroundColor Red
        
        # Add to backlog
        @"
### ResponseFormat Import Issue
- **File**: src/backend/kernel_agents/agent_factory.py
- **Issue**: Cannot import ResponseFormat from azure.ai.projects.models
- **Solution**: Need to create custom ResponseFormat class or update the imports
"@ | Add-Content $backlogPath
        
        Write-Host "Issue added to backlog" -ForegroundColor Yellow
    }
}

# Try to start the backend server
Write-Host "Attempting to start backend server. Press Ctrl+C to stop after testing..." -ForegroundColor Yellow
try {
    Write-Host "Changing directory to backend folder" -ForegroundColor Cyan
    Push-Location "D:\0GH_PROD\Darbot-Agent-Engine\src\backend"
    
    # Run with a timeout to allow for testing but not get stuck
    Write-Host "Starting backend server for 30 seconds to test functionality..." -ForegroundColor Yellow
    
    # Using the Start-Process with -Wait parameter and job to timeout
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        $env:PYTHONPATH = "D:\0GH_PROD\Darbot-Agent-Engine\src"
        uv run uvicorn backend.app_kernel:app --host 0.0.0.0 --port 8001
    }
    
    # Wait for 10 seconds to let the server start
    Write-Host "Waiting for server to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    # Check if the server is running by testing the health endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend server is running successfully! Health check endpoint responded with status code: $($response.StatusCode)" -ForegroundColor Green
            
            # Try to access the API docs
            try {
                $docsResponse = Invoke-WebRequest -Uri "http://localhost:8001/docs" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
                if ($docsResponse.StatusCode -eq 200) {
                    Write-Host "API documentation is accessible at http://localhost:8001/docs" -ForegroundColor Green
                }
            } catch {
                Write-Host "Could not access API docs: $_" -ForegroundColor Red
                @"
### API Documentation Issue
- **Endpoint**: http://localhost:8001/docs
- **Issue**: Failed to access API documentation
- **Error**: $_
"@ | Add-Content $backlogPath
            }
        } else {
            Write-Host "Backend server health check returned status code: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "Could not reach health check endpoint: $_" -ForegroundColor Red
        @"
### Backend Server Issue
- **Issue**: Failed to start backend server or health check endpoint not responding
- **Error**: $_
"@ | Add-Content $backlogPath
    }
    
    # Stop the job after testing
    Stop-Job -Job $job
    Remove-Job -Job $job -Force
    
    Pop-Location
} catch {
    Write-Host "Error while starting backend server: $_" -ForegroundColor Red
    @"
### Server Startup Issue
- **Issue**: Failed to start backend server
- **Error**: $_
"@ | Add-Content $backlogPath
}

# Step 2: Check for .env file and Azure configuration
Write-Host "`n[Step 2] Checking .env file and Azure configuration..." -ForegroundColor Yellow
$envFilePath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\.env"
if (Test-Path $envFilePath) {
    Write-Host ".env file exists at $envFilePath" -ForegroundColor Green
    
    # Check if placeholders are still in the file
    $envContent = Get-Content $envFilePath -Raw
    if ($envContent -match "your-openai-resource" -or $envContent -match "your-actual-api-key") {
        Write-Host "WARNING: .env file contains placeholder values that need to be replaced with actual Azure service endpoints" -ForegroundColor Yellow
        @"
### Azure Configuration Issue
- **File**: src/backend/.env
- **Issue**: .env file contains placeholder values
- **Action Required**: Replace placeholders with actual Azure service endpoints
"@ | Add-Content $backlogPath
    } else {
        Write-Host ".env file appears to have real values (not placeholders)" -ForegroundColor Green
    }
} else {
    Write-Host ".env file not found at $envFilePath" -ForegroundColor Red
    @"
### Missing .env File
- **Issue**: .env file does not exist at src/backend/.env
- **Action Required**: Create .env file with Azure service endpoints
"@ | Add-Content $backlogPath
}

# Step 3: Check for frontend folder and application
Write-Host "`n[Step 3] Checking frontend application..." -ForegroundColor Yellow
$frontendPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\frontend"
if (Test-Path $frontendPath) {
    Write-Host "Frontend folder exists at $frontendPath" -ForegroundColor Green
    
    # Check for package.json to confirm it's a JavaScript/TypeScript frontend
    if (Test-Path "$frontendPath\package.json") {
        Write-Host "Frontend package.json found, this appears to be a JavaScript/TypeScript frontend" -ForegroundColor Green
    } else {
        Write-Host "No package.json found in frontend folder, might not be a JavaScript/TypeScript frontend" -ForegroundColor Yellow
    }
} else {
    Write-Host "Frontend folder not found at $frontendPath" -ForegroundColor Red
    @"
### Missing Frontend
- **Issue**: Frontend folder does not exist at src/frontend
- **Action Required**: Create or restore frontend application
"@ | Add-Content $backlogPath
}

# Step 4: Check for test files
Write-Host "`n[Step 4] Checking for test files..." -ForegroundColor Yellow
$testPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\tests"
if (Test-Path $testPath) {
    $testFiles = Get-ChildItem -Path $testPath -Recurse -Filter "test_*.py"
    if ($testFiles.Count -gt 0) {
        Write-Host "Found $($testFiles.Count) test files in $testPath" -ForegroundColor Green
    } else {
        Write-Host "No test files found in $testPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "Tests folder not found at $testPath" -ForegroundColor Red
}

# Step 5: Check Azure deployment configuration
Write-Host "`n[Step 5] Checking Azure deployment configuration..." -ForegroundColor Yellow
$azdYamlPath = "D:\0GH_PROD\Darbot-Agent-Engine\azure.yaml"
if (Test-Path $azdYamlPath) {
    Write-Host "Azure Developer CLI (azd) configuration found at $azdYamlPath" -ForegroundColor Green
} else {
    Write-Host "Azure Developer CLI configuration not found at $azdYamlPath" -ForegroundColor Red
    @"
### Missing Azure Deployment Configuration
- **Issue**: azure.yaml file not found
- **Action Required**: Create Azure Developer CLI configuration
"@ | Add-Content $backlogPath
}

# Check for infrastructure files
$infraPath = "D:\0GH_PROD\Darbot-Agent-Engine\infra"
if (Test-Path $infraPath) {
    $bicepFiles = Get-ChildItem -Path $infraPath -Recurse -Filter "*.bicep"
    if ($bicepFiles.Count -gt 0) {
        Write-Host "Found $($bicepFiles.Count) Bicep files in $infraPath" -ForegroundColor Green
    } else {
        Write-Host "No Bicep files found in $infraPath" -ForegroundColor Yellow
    }
} else {
    Write-Host "Infra folder not found at $infraPath" -ForegroundColor Red
}

# Summary of validation
Write-Host "`n[Summary] Validation complete!" -ForegroundColor Green
Write-Host "Check backlog.md for any issues that need to be addressed." -ForegroundColor Cyan
Write-Host "Next steps according to next-steps.md:"
Write-Host "1. Update Azure Resource Configuration in the .env file (HIGH PRIORITY)" -ForegroundColor Yellow
Write-Host "2. Start and test frontend integration" -ForegroundColor Yellow
Write-Host "3. Test multi-agent workflow with sample requests" -ForegroundColor Yellow
Write-Host "4. Verify database connectivity" -ForegroundColor Yellow
Write-Host "5. Deploy to Azure using 'azd up'" -ForegroundColor Yellow

# Wait as requested
Write-Host "`nWaiting 5 seconds before returning to prompt..." -ForegroundColor Magenta
Start-Sleep -Seconds 5
return
