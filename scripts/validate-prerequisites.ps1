# Validate Prerequisites Script

# This PowerShell script checks if all necessary prerequisites are met before starting the deployment.

# Define the prerequisites
$prerequisites = @(
    @{ Name = "Azure CLI"; Command = "az"; CheckCommand = { & $Command --version } },
    @{ Name = "Azure Dev CLI"; Command = "azd"; CheckCommand = { & $Command version } },
    @{ Name = "Docker"; Command = "docker"; CheckCommand = { & $Command --version } },
    @{ Name = "PowerShell"; Command = "pwsh"; CheckCommand = { & $Command -Command "exit" } }
)

# Function to check if a command exists
function Check-Command {
    param (
        [string]$command
    )
    $commandPath = Get-Command $command -ErrorAction SilentlyContinue
    return $commandPath -ne $null
}

# Validate prerequisites
foreach ($prerequisite in $prerequisites) {
    $name = $prerequisite.Name
    $command = $prerequisite.Command
    $checkCommand = $prerequisite.CheckCommand

    if (-not (Check-Command $command)) {
        Write-Host "Prerequisite not met: $name is not installed." -ForegroundColor Red
    } else {
        try {
            & $checkCommand
            Write-Host "Prerequisite met: $name is installed." -ForegroundColor Green
        } catch {
            Write-Host "Prerequisite check failed: $name is installed but not functioning correctly." -ForegroundColor Yellow
        }
    }
}

# Final validation message
Write-Host "Prerequisite validation completed." -ForegroundColor Cyan