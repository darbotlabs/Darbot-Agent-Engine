# Thought into existence by Darbot
# Script to fix test import issues

Write-Host "Starting test import fix script..." -ForegroundColor Cyan
$scriptStartTime = Get-Date

# Set PYTHONPATH correctly for PowerShell
$env:PYTHONPATH = "D:\0GH_PROD\Darbot-Agent-Engine\src"
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Green

# Check if we're in the correct directory
$currentDir = Get-Location
if ($currentDir.Path -ne "D:\0GH_PROD\Darbot-Agent-Engine") {
    Write-Host "Navigating to project directory..." -ForegroundColor Cyan
    Set-Location "D:\0GH_PROD\Darbot-Agent-Engine"
}

# Fix 1: Create __init__.py in tests directory if needed
$testsInitPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\tests\__init__.py"
if (-not (Test-Path $testsInitPath)) {
    Write-Host "Creating __init__.py in tests directory..." -ForegroundColor Cyan
    @"
# Thought into existence by Darbot
# This file marks tests as a Python package
"@ | Set-Content $testsInitPath
    Write-Host "Created __init__.py in tests directory" -ForegroundColor Green
}

# Fix 2: Check and update import in test_app.py
$testAppPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\tests\test_app.py"
if (Test-Path $testAppPath) {
    Write-Host "Checking imports in test_app.py..." -ForegroundColor Cyan
    $content = Get-Content $testAppPath -Raw
    
    # Fix direct import of app_kernel
    if ($content -match "from app_kernel import") {
        Write-Host "Fixing app_kernel import in test_app.py..." -ForegroundColor Cyan
        $content = $content -replace "from app_kernel import", "from backend.app_kernel import"
        $modified = $true
    }
    
    # Fix direct import of app_config
    if ($content -match "import app_config") {
        Write-Host "Fixing app_config import in test_app.py..." -ForegroundColor Cyan
        $content = $content -replace "import app_config", "import backend.app_config as app_config  # Thought into existence by Darbot"
        $modified = $true
    }
    
    if ($modified) {
        $content | Set-Content $testAppPath
        Write-Host "Fixed imports in test_app.py" -ForegroundColor Green
    } else {
        Write-Host "No import issues found in test_app.py" -ForegroundColor Yellow
    }
}

# Fix 3: Check and update imports in all test files
$testFiles = Get-ChildItem -Path "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\tests" -Recurse -Filter "test_*.py"
$fixedCount = 0

foreach ($testFile in $testFiles) {
    if ($testFile.Name -eq "test_app.py") {
        continue  # Already handled this file
    }
    
    Write-Host "Checking imports in $($testFile.Name)..." -ForegroundColor Cyan
    $content = Get-Content $testFile.FullName -Raw
    $modified = $false
    
    # Look for common import patterns that might need to be fixed
    $importPatterns = @(
        @{Pattern = "from app_kernel import"; Replacement = "from backend.app_kernel import"},
        @{Pattern = "from app_config import"; Replacement = "from backend.app_config import"},
        @{Pattern = "from utils_kernel import"; Replacement = "from backend.utils_kernel import"},
        @{Pattern = "from config_kernel import"; Replacement = "from backend.config_kernel import"},
        @{Pattern = "from models"; Replacement = "from backend.models"},
        @{Pattern = "from kernel_agents"; Replacement = "from backend.kernel_agents"},
        @{Pattern = "from kernel_tools"; Replacement = "from backend.kernel_tools"},
        @{Pattern = "from context"; Replacement = "from backend.context"}
    )
    
    foreach ($pattern in $importPatterns) {
        if ($content -match $pattern.Pattern) {
            Write-Host "  - Fixing $($pattern.Pattern) in $($testFile.Name)..." -ForegroundColor Yellow
            $content = $content -replace $pattern.Pattern, $pattern.Replacement
            $modified = $true
        }
    }
    
    if ($modified) {
        $content | Set-Content $testFile.FullName
        $fixedCount++
        Write-Host "  ✓ Fixed imports in $($testFile.Name)" -ForegroundColor Green
    }
}

Write-Host "Fixed imports in $fixedCount additional test files" -ForegroundColor Green

# Fix 4: Fix the health endpoint route if needed
$appKernelPath = "D:\0GH_PROD\Darbot-Agent-Engine\src\backend\app_kernel.py"
if (Test-Path $appKernelPath) {
    Write-Host "Checking health endpoint in app_kernel.py..." -ForegroundColor Cyan
    $content = Get-Content $appKernelPath -Raw
      # Check if there's a health endpoint route
    if (-not ($content -match "@app\.(get|route)\s*\(\s*['""`"]/health")) {
        Write-Host "Adding health endpoint route to app_kernel.py..." -ForegroundColor Yellow
        
        # Look for FastAPI app definition
        if ($content -match "(app\s*=\s*FastAPI\(.*?\))") {
            $appDefinition = $matches[1]
            
            # Find a good spot to insert the health endpoint route
            if ($content -match "(@app\.(?:get|post|put|delete)\s*\()") {
                $firstEndpoint = $matches[1]
                $insertPosition = $content.IndexOf($firstEndpoint)
                
                # Insert the health endpoint route before the first existing endpoint
                $healthEndpoint = @"

@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy"}

"@
                $content = $content.Insert($insertPosition, $healthEndpoint)
                $content | Set-Content $appKernelPath
                Write-Host "Added health endpoint route to app_kernel.py" -ForegroundColor Green
            } else {
                Write-Host "Could not find a suitable location to insert health endpoint" -ForegroundColor Red
            }
        } else {
            Write-Host "Could not find FastAPI app definition" -ForegroundColor Red
        }
    } else {
        Write-Host "Health endpoint route already exists in app_kernel.py" -ForegroundColor Green
    }
}

# Run a quick test to see if our fixes worked
Write-Host "`nRunning a quick test to check if our fixes worked..." -ForegroundColor Yellow
Push-Location "D:\0GH_PROD\Darbot-Agent-Engine\src\backend"

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
        Write-Host "`n✅ SUCCESS! Backend server is running correctly!" -ForegroundColor Green
        Write-Host "Health check endpoint is now working: $($response.Content)" -ForegroundColor Green
        
        # Update validation_results.md
        $validationPath = "D:\0GH_PROD\Darbot-Agent-Engine\validation_results.md"
        if (Test-Path $validationPath) {
            $content = Get-Content $validationPath -Raw
            if ($content -match "❌ \*\*Health Endpoint\*\*: Error response") {
                $content = $content -replace "❌ \*\*Health Endpoint\*\*: Error response.*", "✅ **Health Endpoint**: Successfully fixed and working at http://localhost:8001/health"
                $content | Set-Content $validationPath
                Write-Host "Updated validation_results.md with success status" -ForegroundColor Green
            }
        }
    } else {
        Write-Host "Backend server health check returned status code: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`n⚠️ Health endpoint still not working: $_" -ForegroundColor Red
}

# Stop the job after testing
Stop-Job -Job $job
Remove-Job -Job $job -Force

Pop-Location

# Try running tests to see if import issues are fixed
Write-Host "`nTrying to run a single test to check if import issues are fixed..." -ForegroundColor Yellow
Push-Location "D:\0GH_PROD\Darbot-Agent-Engine\src\backend"
$testResult = Invoke-Expression "uv run pytest tests/test_app.py -v 2>&1"
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ SUCCESS! Tests are running without import errors!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Test still has issues:" -ForegroundColor Red
    Write-Host $testResult -ForegroundColor Red
}
Pop-Location

# Script completion summary
$scriptEndTime = Get-Date
$duration = $scriptEndTime - $scriptStartTime
Write-Host "`nScript completed in $($duration.TotalSeconds.ToString("0.00")) seconds" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Check if backend server now runs with health endpoint" -ForegroundColor Yellow
Write-Host "2. Verify tests are running correctly" -ForegroundColor Yellow
Write-Host "3. Start frontend server and test integration" -ForegroundColor Yellow
Write-Host "4. Test multi-agent workflows" -ForegroundColor Yellow
Write-Host "5. Deploy to Azure" -ForegroundColor Yellow

# Wait as requested
Write-Host "`nWaiting 5 seconds before returning to prompt..." -ForegroundColor Magenta
Start-Sleep -Seconds 5
return
