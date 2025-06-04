<#
.SYNOPSIS
    Darbot Agent Engine - All-in-One Launcher
    
.DESCRIPTION
    Launches the complete Darbot Agent Engine stack including backend API, 
    frontend server, and web UI with Azure resource integration.
    Can be compiled to executable using PS2EXE.

.PARAMETER ConfigFile
    Path to the .env configuration file (default: searches common locations)
    
.PARAMETER BackendPort
    Port for the backend API server (default: 8001)
    
.PARAMETER FrontendPort
    Port for the frontend web server (default: 3000)
    
.PARAMETER SkipBrowserOpen
    Skip opening the browser automatically
    
.PARAMETER DebugMode
    Enable verbose debug logging

.EXAMPLE
    .\DarbotLauncher.ps1
    .\DarbotLauncher.ps1 -ConfigFile "C:\config\.env" -DebugMode
    
.NOTES
    To compile to EXE: 
    Install-Module ps2exe -Scope CurrentUser
    Invoke-PS2EXE .\DarbotLauncher.ps1 .\DarbotLauncher.exe -noConsole
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $false)]
    [string]$ConfigFile,
    
    [Parameter(Mandatory = $false)]
    [int]$BackendPort = 8001,
    
    [Parameter(Mandatory = $false)]
    [int]$FrontendPort = 3000,
    
    [Parameter(Mandatory = $false)]
    [switch]$SkipBrowserOpen = $false,
    
    [Parameter(Mandatory = $false)]
    [switch]$DebugMode = $false
)

#region Global Variables and Configuration

$script:ProcessList = @()
$script:TempFiles = @()
$script:IsShuttingDown = $false
$script:StartTime = Get-Date

# Application metadata
$AppName = "Darbot Agent Engine"
$AppVersion = "1.0.0"
$AppIcon = "🤖"

# Determine root path
$script:RootPath = if ($PSScriptRoot) { 
    Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))
} else { 
    "g:\Github\darbotlabs\Darbot-Agent-Engine" 
}

# Search paths for .env file
$EnvSearchPaths = @(
    $ConfigFile,
    "$script:RootPath\.env",
    "$script:RootPath\Deployer\deployment-checklist\.env",
    "$PSScriptRoot\.env",
    "$env:USERPROFILE\.darbot\.env"
) | Where-Object { $_ }

#endregion

#region Helper Functions

function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [ConsoleColor]$Color = "White"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    if ($script:LogFile) {
        Add-Content -Path $script:LogFile -Value $logMessage -ErrorAction SilentlyContinue
    }
    
    switch ($Level) {
        "ERROR" { $Color = "Red"; $prefix = "❌" }
        "WARNING" { $Color = "Yellow"; $prefix = "⚠️" }
        "SUCCESS" { $Color = "Green"; $prefix = "✅" }
        "INFO" { $Color = "Cyan"; $prefix = "ℹ️" }
        "DEBUG" { $Color = "Gray"; $prefix = "🔍" }
        default { $prefix = "" }
    }
    
    if ($Level -ne "DEBUG" -or $DebugMode) {
        Write-Host "$prefix $Message" -ForegroundColor $Color
    }
}

function Find-EnvFile {
    foreach ($path in $EnvSearchPaths) {
        if ($path -and (Test-Path $path)) {
            Write-Log "Found configuration file: $path" "SUCCESS"
            return $path
        }
    }
    
    Write-Log "No .env configuration file found in search paths" "ERROR"
    return $null
}

function Load-DotEnv {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        Write-Log "Configuration file not found: $Path" "ERROR"
        return $false
    }
    
    try {
        $lineNumber = 0
        Get-Content $Path | ForEach-Object {
            $lineNumber++
            if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
            
            if ($_ -match '^\s*([^=]+)\s*=\s*(.*)\s*$') {
                $key = $matches[1].Trim()
                $val = $matches[2].Trim()
                $val = $val -replace '^"|"$', ''
                
                [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
                Write-Log "Loaded: $key" "DEBUG"
            } else {
                Write-Log "Invalid line $lineNumber in config: $_" "WARNING"
            }
        }
        return $true
    } catch {
        Write-Log "Error loading configuration: $_" "ERROR"
        return $false
    }
}

function Test-AzureCliInstalled {
    try {
        $azVersion = az version --query '\"azure-cli\"' -o tsv 2>$null
        if ($azVersion) {
            Write-Log "Azure CLI version $azVersion detected" "DEBUG"
            return $true
        }
    } catch {}
    return $false
}

function Test-AzureLogin {
    try {
        $account = az account show 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Log "Logged in as: $($account.user.name)" "SUCCESS"
            Write-Log "Subscription: $($account.name) ($($account.id))" "INFO"
            return $true
        }
    } catch {}
    return $false
}

function Test-PythonEnvironment {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python (\d+\.\d+)") {
            $version = [version]$matches[1]
            if ($version -ge [version]"3.8") {
                Write-Log "Python $version detected" "SUCCESS"
                return $true
            } else {
                Write-Log "Python $version is too old (requires 3.8+)" "ERROR"
                return $false
            }
        }
    } catch {}
    Write-Log "Python not found or not in PATH" "ERROR"
    return $false
}

function Install-Dependencies {
    param(
        [string]$RequirementsFile,
        [string]$Name
    )
    
    if (-not (Test-Path $RequirementsFile)) {
        Write-Log "$Name requirements file not found: $RequirementsFile" "WARNING"
        return $true
    }
    
    Write-Log "Installing $Name dependencies..." "INFO"
    
    # Try UV first, then pip
    $uvAvailable = Get-Command uv -ErrorAction SilentlyContinue
      try {        if ($uvAvailable) {
            Write-Log "Using UV package manager with system flag..." "INFO"
            # Try UV with system flag first, then fallback to pip
            $output = uv pip install -r $RequirementsFile --prerelease=allow --system 2>&1
            $success = $LASTEXITCODE -eq 0
            
            if (-not $success) {
                Write-Log "UV installation failed (exit code: $LASTEXITCODE), falling back to pip..." "WARNING"
                Write-Log "UV output: $output" "DEBUG"
                $output = pip install -r $RequirementsFile --pre 2>&1
                $success = $LASTEXITCODE -eq 0
            } else {
                Write-Log "UV installation completed successfully" "SUCCESS"
            }
        } else {
            Write-Log "UV not available, using pip..." "INFO"
            $output = pip install -r $RequirementsFile --pre 2>&1
            $success = $LASTEXITCODE -eq 0
        }
        
        if ($success) {
            Write-Log "$Name dependencies installed successfully" "SUCCESS"
            return $true
        } else {
            Write-Log "Failed to install $Name dependencies: $output" "ERROR"
            return $false
        }
    } catch {
        Write-Log "Exception installing $Name dependencies: $_" "ERROR"
        return $false
    }
}

function Start-ServerProcess {
    param(
        [string]$Name,
        [string]$WorkingDirectory,
        [string]$Command,
        [int]$Port,
        [hashtable]$AdditionalEnv = @{}
    )
    
    Write-Log "Starting $Name server on port $Port..." "INFO"
    
    # Create process start info
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "python"
    $psi.Arguments = "-u -m $Command"
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    
    # Set environment variables
    $psi.EnvironmentVariables["PYTHONPATH"] = "$script:RootPath\src"
    $psi.EnvironmentVariables["PYTHONUNBUFFERED"] = "1"
    
    foreach ($key in $AdditionalEnv.Keys) {
        $psi.EnvironmentVariables[$key] = $AdditionalEnv[$key]
    }
    
    # Copy current environment
    foreach ($envVar in [System.Environment]::GetEnvironmentVariables("Process").GetEnumerator()) {
        if (-not $psi.EnvironmentVariables.ContainsKey($envVar.Key)) {
            $psi.EnvironmentVariables[$envVar.Key] = $envVar.Value
        }
    }
    
    try {
        $process = [System.Diagnostics.Process]::Start($psi)
        
        if ($process) {
            $script:ProcessList += @{
                Name = $Name
                Process = $process
                Port = $Port
                StartTime = Get-Date
            }            # Start async output readers for both stdout and stderr
            Start-Job -ScriptBlock {
                param($process, $name, $logFile)
                while (-not $process.StandardOutput.EndOfStream) {
                    $line = $process.StandardOutput.ReadLine()
                    if ($line) {
                        Add-Content -Path $logFile -Value "[$name] $line" -ErrorAction SilentlyContinue
                    }
                }
            } -ArgumentList $process, $Name, $script:LogFile
            
            Start-Job -ScriptBlock {
                param($process, $name, $logFile)
                while (-not $process.StandardError.EndOfStream) {
                    $line = $process.StandardError.ReadLine()
                    if ($line) {
                        Add-Content -Path $logFile -Value "[$name ERROR] $line" -ErrorAction SilentlyContinue
                    }
                }
            } -ArgumentList $process, $Name, $script:LogFile
            
            Write-Log "$Name server started (PID: $($process.Id))" "SUCCESS"
            return $process
        }
    } catch {
        Write-Log "Failed to start $Name server: $_" "ERROR"
        return $null
    }
}

function Test-ServerHealth {
    param(
        [string]$Name,
        [string]$Url,
        [int]$MaxRetries = 60,
        [int]$RetryDelay = 2000
    )
    
    Write-Log "Checking $Name health at $Url..." "INFO"
    
    for ($i = 1; $i -le $MaxRetries; $i++) {
        try {
            # First check if process is still running
            $process = ($script:ProcessList | Where-Object { $_.Name -eq $Name }).Process
            if ($process -and $process.HasExited) {
                Write-Log "$Name process has exited unexpectedly" "ERROR"
                
                # Try to read the log file for error details
                if ($script:LogFile -and (Test-Path $script:LogFile)) {
                    $recentLogs = Get-Content $script:LogFile -Tail 20 | Where-Object { $_ -match $Name }
                    if ($recentLogs) {
                        Write-Log "Recent $Name logs:" "ERROR"
                        $recentLogs | ForEach-Object { Write-Log $_ "ERROR" }
                    }
                }
                return $false
            }
            
            $response = Invoke-WebRequest -Uri $Url -Method Get -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Log "$Name is healthy" "SUCCESS"
                return $true
            }
        } catch {
            if ($i % 10 -eq 0) {  # Log every 10th attempt
                Write-Log "Health check attempt $i/$MaxRetries - $Name not ready yet..." "INFO"
            } else {
                Write-Log "Health check attempt $i/$MaxRetries failed: $($_.Exception.Message)" "DEBUG"
            }
        }
        
        if ($i -lt $MaxRetries) {
            Start-Sleep -Milliseconds $RetryDelay
        }
    }
    
    Write-Log "$Name health check failed after $MaxRetries attempts" "WARNING"
    return $false
}

function Show-SplashScreen {
    $splash = @"

    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║         $AppIcon  D A R B O T   A G E N T   E N G I N E      ║
    ║                                                              ║
    ║                      Version $AppVersion                     ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝

"@
    Write-Host $splash -ForegroundColor Cyan
}

function Stop-DarbotServices {
    if ($script:IsShuttingDown) { return }
    $script:IsShuttingDown = $true
    
    Write-Log "`nShutting down Darbot services..." "INFO"
    
    # Stop all processes
    foreach ($proc in $script:ProcessList) {
        if ($proc.Process -and -not $proc.Process.HasExited) {
            Write-Log "Stopping $($proc.Name) (PID: $($proc.Process.Id))..." "INFO"
            try {
                $proc.Process.Kill()
                $proc.Process.WaitForExit(5000)
            } catch {
                Write-Log "Error stopping $($proc.Name): $_" "WARNING"
            }
        }
    }
    
    # Clean up temp files
    foreach ($file in $script:TempFiles) {
        if (Test-Path $file) {
            Remove-Item $file -Force -ErrorAction SilentlyContinue
        }
    }
    
    $runtime = (Get-Date) - $script:StartTime
    Write-Log "Darbot services stopped. Total runtime: $($runtime.ToString('hh\:mm\:ss'))" "INFO"
}

#endregion

#region Main Execution

# Set up clean exit handling
$null = Register-ObjectEvent -InputObject ([System.Console]) -EventName CancelKeyPress -Action { Stop-DarbotServices }
trap { Stop-DarbotServices; exit 1 }

# Show splash screen
Clear-Host
Show-SplashScreen

# Set up logging
$script:LogDir = "$script:RootPath\logs"
if (-not (Test-Path $script:LogDir)) {
    New-Item -ItemType Directory -Path $script:LogDir -Force | Out-Null
}
$script:LogFile = Join-Path $script:LogDir "darbot_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

Write-Log "Starting Darbot Agent Engine launcher..." "INFO"
Write-Log "Root path: $script:RootPath" "DEBUG"

# Find and load configuration
$envPath = Find-EnvFile
if (-not $envPath) {
    Write-Log "Please create a .env configuration file" "ERROR"
    Write-Log "Expected locations: $($EnvSearchPaths -join ', ')" "INFO"
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Load-DotEnv -Path $envPath)) {
    Read-Host "Press Enter to exit"
    exit 1
}

# Override with command line parameters
[System.Environment]::SetEnvironmentVariable("BACKEND_PORT", "$BackendPort", "Process")
[System.Environment]::SetEnvironmentVariable("FRONTEND_PORT", "$FrontendPort", "Process")
[System.Environment]::SetEnvironmentVariable("BACKEND_API_URL", "http://localhost:$BackendPort", "Process")

# Validate critical Azure resources
Write-Log "`nValidating Azure configuration..." "INFO"

$requiredVars = @(
    "COSMOSDB_ENDPOINT",
    "COSMOSDB_DATABASE", 
    "COSMOSDB_CONTAINER",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_MODEL_NAME"
)

$missingVars = @()
foreach ($var in $requiredVars) {
    if (-not [System.Environment]::GetEnvironmentVariable($var, "Process")) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Log "Missing required configuration variables:" "ERROR"
    $missingVars | ForEach-Object { Write-Log "  - $_" "ERROR" }
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Log "Azure configuration validated" "SUCCESS"

# Check prerequisites
Write-Log "`nChecking prerequisites..." "INFO"

# Python check
if (-not (Test-PythonEnvironment)) {
    Write-Log "Please install Python 3.8 or later from https://python.org" "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}

# Azure CLI check
if (-not (Test-AzureCliInstalled)) {
    Write-Log "Azure CLI not found - Azure authentication may fail" "WARNING"
    Write-Log "Install from: https://aka.ms/installazurecliwindows" "INFO"
} elseif (-not (Test-AzureLogin)) {
    Write-Log "Not logged in to Azure CLI" "WARNING"
    Write-Log "Run 'az login' to authenticate" "INFO"
}

# Set Python path
[System.Environment]::SetEnvironmentVariable("PYTHONPATH", "$script:RootPath\src", "Process")

# Install dependencies
$backendReqs = "$script:RootPath\src\backend\requirements.txt"
$frontendReqs = "$script:RootPath\src\frontend\requirements.txt"

if (-not (Install-Dependencies -RequirementsFile $backendReqs -Name "Backend")) {
    Read-Host "Press Enter to exit"
    exit 1
}

if (-not (Install-Dependencies -RequirementsFile $frontendReqs -Name "Frontend")) {
    Read-Host "Press Enter to exit"
    exit 1
}

# Start backend server
Write-Log "`nStarting services..." "INFO"

$backendProc = Start-ServerProcess `
    -Name "Backend API" `
    -WorkingDirectory "$script:RootPath\src" `
    -Command "backend_launcher --port $BackendPort" `
    -Port $BackendPort

if (-not $backendProc) {
    Write-Log "Failed to start backend server" "ERROR"
    Stop-DarbotServices
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait for backend to be ready
if (-not (Test-ServerHealth -Name "Backend" -Url "http://localhost:$BackendPort/health")) {
    Write-Log "Backend server failed to start properly" "ERROR"
    Stop-DarbotServices
    Read-Host "Press Enter to exit"
    exit 1
}

# Start frontend server
$frontendProc = Start-ServerProcess `
    -Name "Frontend Server" `
    -WorkingDirectory "$script:RootPath\src\frontend" `
    -Command "uvicorn frontend_server:app --host 0.0.0.0 --port $FrontendPort" `
    -Port $FrontendPort `
    -AdditionalEnv @{
        "BACKEND_API_URL" = "http://localhost:$BackendPort"
    }

if (-not $frontendProc) {
    Write-Log "Failed to start frontend server" "ERROR"
    Stop-DarbotServices
    Read-Host "Press Enter to exit"
    exit 1
}

# Wait for frontend to be ready
if (-not (Test-ServerHealth -Name "Frontend" -Url "http://localhost:$FrontendPort")) {
    Write-Log "Frontend server failed to start properly" "ERROR"
    Stop-DarbotServices
    Read-Host "Press Enter to exit"
    exit 1
}

# Open browser
if (-not $SkipBrowserOpen) {
    Write-Log "Opening application in browser..." "INFO"
    Start-Process "http://localhost:$FrontendPort"
}

# Display running status
Write-Host "`n" -NoNewline
Write-Log "═══════════════════════════════════════════════════════════════" "SUCCESS"
Write-Log "       $AppIcon  Darbot Agent Engine is running!                " "SUCCESS"
Write-Log "═══════════════════════════════════════════════════════════════" "SUCCESS"
Write-Host ""
Write-Log "  🌐 Frontend:  http://localhost:$FrontendPort" "INFO"
Write-Log "  🔧 Backend:   http://localhost:$BackendPort" "INFO"
Write-Log "  📚 API Docs:  http://localhost:$BackendPort/docs" "INFO"
Write-Host ""
Write-Log "  💾 Data:      Azure CosmosDB" "INFO"
Write-Log "  🧠 AI Model:  $($env:AZURE_OPENAI_MODEL_NAME)" "INFO"
Write-Log "  🔐 Auth:      $($env:AUTH_ENABLED)" "INFO"
Write-Host ""
Write-Log "  Press Ctrl+C to stop all services" "WARNING"
Write-Log "═══════════════════════════════════════════════════════════════" "SUCCESS"

# Keep running and monitor processes
try {
    while ($true) {
        # Check if any critical process has exited
        $exitedProcess = $null
        foreach ($proc in $script:ProcessList) {
            if ($proc.Process.HasExited) {
                $exitedProcess = $proc
                break
            }
        }
        
        if ($exitedProcess) {
            Write-Log "$($exitedProcess.Name) has stopped unexpectedly" "ERROR"
            Stop-DarbotServices
            Read-Host "Press Enter to exit"
            exit 1
        }
        
        Start-Sleep -Seconds 1
    }
} finally {
    Stop-DarbotServices
}

#endregion