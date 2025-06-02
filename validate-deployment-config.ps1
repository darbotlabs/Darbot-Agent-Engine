# Validation Script for Azure Deployment Tasks
# Thought into existence by Darbot

# Script to validate Azure deployment configuration
Write-Host "Starting Darbot Agent Engine Deployment Configuration Validation..." -ForegroundColor Cyan

# Check if VS Code is installed
try {
    $vsCodePath = Get-Command code -ErrorAction SilentlyContinue
    Write-Host "✓ VS Code is installed at: $($vsCodePath.Source)" -ForegroundColor Green
} catch {
    Write-Host "❌ VS Code is not found in PATH. Please install VS Code." -ForegroundColor Red
}

# Check if .vscode directory exists
$vscodeDirPath = "d:\0GH_PROD\Darbot-Agent-Engine\.vscode"
if (Test-Path $vscodeDirPath) {
    Write-Host "✓ .vscode directory exists at: $vscodeDirPath" -ForegroundColor Green
} else {
    Write-Host "❌ .vscode directory not found at: $vscodeDirPath" -ForegroundColor Red
}

# Check if tasks.json exists
$tasksFilePath = "d:\0GH_PROD\Darbot-Agent-Engine\.vscode\tasks.json"
if (Test-Path $tasksFilePath) {
    Write-Host "✓ tasks.json exists at: $tasksFilePath" -ForegroundColor Green
    
    # Validate tasks.json content
    try {
        $tasksContent = Get-Content $tasksFilePath -Raw | ConvertFrom-Json
        $tasksCount = $tasksContent.tasks.Count
        Write-Host "✓ tasks.json is valid JSON with $tasksCount tasks defined" -ForegroundColor Green
        
        # List all defined tasks
        Write-Host "`nDefined tasks:" -ForegroundColor Cyan
        foreach ($task in $tasksContent.tasks) {
            Write-Host "  - $($task.label)" -ForegroundColor White
        }
    } catch {
        Write-Host "❌ tasks.json is not valid JSON: $_" -ForegroundColor Red
    }
} else {
    Write-Host "❌ tasks.json not found at: $tasksFilePath" -ForegroundColor Red
}

# Check if Azure CLI is installed
try {
    $azVersion = az --version | Select-Object -First 1
    Write-Host "✓ Azure CLI is installed: $azVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed or not in PATH" -ForegroundColor Red
}

# Check if Azure Dev CLI (azd) is installed
try {
    $azdVersion = azd version
    Write-Host "✓ Azure Dev CLI is installed: $azdVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure Dev CLI is not installed or not in PATH" -ForegroundColor Red
}

# Check Azure login status
try {
    $accountInfo = az account show | ConvertFrom-Json
    Write-Host "✓ Logged in to Azure as: $($accountInfo.user.name)" -ForegroundColor Green
    Write-Host "  Subscription: $($accountInfo.name) ($($accountInfo.id))" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to Azure or error retrieving account info" -ForegroundColor Red
}

# Check azd environment
try {
    $azdEnv = azd env list
    Write-Host "✓ azd environment(s) configured: $azdEnv" -ForegroundColor Green
} catch {
    Write-Host "❌ Error retrieving azd environments" -ForegroundColor Red
}

# Check for required files for Azure deployment
$infraFiles = @(
    "d:\0GH_PROD\Darbot-Agent-Engine\azure.yaml",
    "d:\0GH_PROD\Darbot-Agent-Engine\infra\main.bicep",
    "d:\0GH_PROD\Darbot-Agent-Engine\infra\resources.bicep"
)

Write-Host "`nChecking infrastructure files:" -ForegroundColor Cyan
foreach ($file in $infraFiles) {
    if (Test-Path $file) {
        Write-Host "✓ File exists: $file" -ForegroundColor Green
    } else {
        Write-Host "❌ File not found: $file" -ForegroundColor Red
    }
}

# Check for validation scripts
$validationScripts = @(
    "d:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts\validate-deployment.ps1",
    "d:\0GH_PROD\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts\cleanup.ps1"
)

Write-Host "`nChecking validation scripts:" -ForegroundColor Cyan
foreach ($script in $validationScripts) {
    if (Test-Path $script) {
        Write-Host "✓ Script exists: $script" -ForegroundColor Green
    } else {
        Write-Host "❌ Script not found: $script" -ForegroundColor Red
    }
}

Write-Host "`nDeployment Configuration Validation Complete!" -ForegroundColor Cyan
Write-Host "If all checks passed, your VS Code tasks should now be available." -ForegroundColor Yellow
Write-Host "Access them via the Command Palette (Ctrl+Shift+P) and type 'Tasks: Run Task'" -ForegroundColor Yellow
