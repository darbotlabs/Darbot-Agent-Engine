# Darbot Agent Engine - All-in-One Launcher

## 🤖 Overview

The **Darbot Agent Engine Launcher** is a comprehensive PowerShell application that provides a single-click solution for launching the complete Darbot Agent Engine stack. This launcher handles all aspects of startup, monitoring, and shutdown of the multi-component system with Azure integration.

## 📋 Table of Contents

1. [System Architecture](#system-architecture)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Components](#components)
7. [Features](#features)
8. [Troubleshooting](#troubleshooting)
9. [Building Executable](#building-executable)
10. [Advanced Options](#advanced-options)

## 🏗️ System Architecture

The Darbot Agent Engine consists of multiple integrated components:

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────────────────────────────────────────────────┤
│  🌐 Web Browser (http://localhost:3000)                    │
│     ├── React Frontend                                     │
│     ├── Authentication UI                                  │
│     └── Agent Interaction Interface                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Server Layer                     │
├─────────────────────────────────────────────────────────────┤
│  🚀 FastAPI Frontend Server (Port 3000)                   │
│     ├── Static File Serving                               │
│     ├── API Proxy to Backend                              │
│     └── Session Management                                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ⚙️ FastAPI Backend Server (Port 8001)                    │
│     ├── Agent Orchestration                               │
│     ├── Task Management                                    │
│     ├── Azure AI Integration                              │
│     └── Data Persistence                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Azure Services Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ☁️ Azure Integration                                      │
│     ├── 🗄️ CosmosDB (Data Storage)                        │
│     ├── 🧠 Azure OpenAI (AI Models)                       │
│     ├── 🔐 Azure AD (Authentication)                      │
│     └── 📊 Application Insights (Monitoring)              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 or Windows Server 2019+
- **PowerShell**: 5.1 or PowerShell Core 7.0+
- **Python**: 3.8 or later
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space
- **Network**: Internet connection for Azure services

### Required Software
1. **Python 3.8+**
   ```powershell
   # Check Python version
   python --version
   ```

2. **Azure CLI** (Optional but recommended)
   ```powershell
   # Install Azure CLI
   winget install Microsoft.AzureCLI
   # Or download from: https://aka.ms/installazurecliwindows
   ```

3. **UV Package Manager** (Optional - for faster dependency installation)
   ```powershell
   # Install UV
   pip install uv
   ```

### Azure Resources Required
- **Azure Subscription** with appropriate permissions
- **CosmosDB Account** with database and container
- **Azure OpenAI Service** with deployed model
- **Azure AD Authentication** configured

## 🚀 Installation & Setup

### Quick Start
1. **Clone or Download** the Darbot Agent Engine repository
2. **Navigate** to the launcher directory:
   ```powershell
   cd "g:\Github\darbotlabs\Darbot-Agent-Engine\Deployer\deployment-checklist\scripts"
   ```
3. **Run** the launcher:
   ```powershell
   .\Launcher.ps1
   ```

### Environment Configuration
The launcher automatically searches for configuration files in these locations:
1. Specified `-ConfigFile` parameter
2. `<RootPath>\.env`
3. `<RootPath>\Deployer\deployment-checklist\.env`
4. `<ScriptPath>\.env`
5. `$env:USERPROFILE\.darbot\.env`

## ⚙️ Configuration

### .env File Structure
```ini
# Darbot Agent Engine Configuration

# CosmosDB Configuration
COSMOSDB_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
COSMOSDB_DATABASE=darbot
COSMOSDB_CONTAINER=plans

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.cognitiveservices.azure.com/
AZURE_OPENAI_MODEL_NAME=gpt-4
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-deployment
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Azure AI Project Configuration
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-project.cognitiveservices.azure.com/
AZURE_AI_SUBSCRIPTION_ID=your-subscription-id
AZURE_AI_RESOURCE_GROUP=your-resource-group
AZURE_AI_RESOURCE_NAME=your-ai-resource
AZURE_AI_PROJECT_NAME=your-project-name

# Server Configuration
BACKEND_API_URL=http://localhost:8001
FRONTEND_SITE_NAME=http://127.0.0.1:3000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8001
FRONTEND_PORT=3000

# Authentication
AUTH_ENABLED=true

# Optional - Azure Authentication Override
# AZURE_TENANT_ID=your-tenant-id
# AZURE_CLIENT_ID=your-client-id
# AZURE_CLIENT_SECRET=your-client-secret
```

### Required Environment Variables
The launcher validates these critical variables:
- `COSMOSDB_ENDPOINT`
- `COSMOSDB_DATABASE`
- `COSMOSDB_CONTAINER`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_MODEL_NAME`

## 🎯 Usage

### Command Line Syntax
```powershell
.\Launcher.ps1 [OPTIONS]
```

### Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `-ConfigFile` | String | Auto-detect | Path to .env configuration file |
| `-BackendPort` | Integer | 8001 | Port for backend API server |
| `-FrontendPort` | Integer | 3000 | Port for frontend web server |
| `-SkipBrowserOpen` | Switch | False | Skip automatic browser opening |
| `-DebugMode` | Switch | False | Enable verbose debug logging |

### Usage Examples
```powershell
# Basic usage (auto-detects configuration)
.\Launcher.ps1

# Custom configuration file
.\Launcher.ps1 -ConfigFile "C:\custom\config\.env"

# Custom ports with debug mode
.\Launcher.ps1 -BackendPort 8002 -FrontendPort 3001 -DebugMode

# Silent mode (no browser opening)
.\Launcher.ps1 -SkipBrowserOpen

# Full customization
.\Launcher.ps1 -ConfigFile ".\custom.env" -BackendPort 9000 -FrontendPort 4000 -DebugMode -SkipBrowserOpen
```

## 🔧 Components

### 1. Configuration Manager
**Purpose**: Loads and validates environment configuration
**Features**:
- Multi-location .env file search
- Variable validation and type checking
- Configuration override capabilities
- Error reporting and suggestions

### 2. Prerequisite Checker
**Purpose**: Validates system requirements before startup
**Validates**:
- Python version (3.8+ required)
- Azure CLI installation and login status
- Required Python packages availability
- Network connectivity

### 3. Dependency Manager
**Purpose**: Installs and manages Python dependencies
**Features**:
- UV package manager support (fast installation)
- Automatic fallback to pip
- Separate frontend/backend dependency handling
- Pre-release package support

### 4. Process Manager
**Purpose**: Manages backend and frontend server processes
**Features**:
- Cross-platform process creation
- Environment variable inheritance
- Output redirection and logging
- Process lifecycle management
- Graceful shutdown handling

### 5. Health Monitor
**Purpose**: Monitors service health and availability
**Features**:
- HTTP health endpoint monitoring
- Retry logic with exponential backoff
- Service availability verification
- Process crash detection and reporting

### 6. Logging System
**Purpose**: Comprehensive logging and debugging
**Features**:
- Timestamped log entries
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, SUCCESS)
- File and console output
- Debug mode for verbose logging
- Log rotation and cleanup

## ✨ Features

### 🔒 Security Features
- **Azure AD Integration**: Secure authentication via Azure Active Directory
- **RBAC Validation**: Checks for required Azure permissions
- **Credential Management**: Uses DefaultAzureCredential for secure access
- **Environment Isolation**: Process-level environment variable isolation

### 🚀 Performance Features
- **Fast Dependency Installation**: UV package manager support
- **Parallel Service Startup**: Concurrent backend/frontend initialization
- **Health Monitoring**: Real-time service availability checking
- **Resource Optimization**: Efficient process and memory management

### 🛠️ Developer Features
- **Debug Mode**: Verbose logging for troubleshooting
- **Hot Reload**: Development server auto-restart on changes
- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Error Reporting**: Detailed error messages and suggestions

### 🎨 User Experience Features
- **Professional UI**: Modern splash screen and status displays
- **Progress Indicators**: Real-time startup progress
- **Automatic Browser Launch**: Opens application automatically
- **Graceful Shutdown**: Clean process termination on Ctrl+C

## 🐛 Troubleshooting

### Common Issues

#### 1. "Configuration file not found"
**Cause**: No .env file in expected locations
**Solution**:
```powershell
# Create .env file in project root
New-Item -Path "g:\Github\darbotlabs\Darbot-Agent-Engine\.env" -ItemType File
# Copy configuration from template or existing file
```

#### 2. "Python not found or not in PATH"
**Cause**: Python not installed or not in system PATH
**Solution**:
```powershell
# Install Python from Microsoft Store
winget install Python.Python.3.11
# Or download from https://python.org
```

#### 3. "Azure CLI not found"
**Cause**: Azure CLI not installed
**Solution**:
```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI
# Login to Azure
az login
```

#### 4. "Missing required configuration variables"
**Cause**: Required environment variables not set in .env
**Solution**: Verify all required variables are present in .env file

#### 5. "Backend server failed to start"
**Possible Causes**:
- Port already in use
- Missing Python dependencies
- Azure authentication issues
- CosmosDB connection problems

**Solutions**:
```powershell
# Check port availability
netstat -an | findstr :8001

# Manual dependency installation
pip install -r src\backend\requirements.txt

# Azure login
az login

# Test CosmosDB connectivity
python test_cosmos_connectivity.py
```

#### 6. "Frontend server failed to start"
**Possible Causes**:
- Port conflict
- Backend not responding
- Missing frontend dependencies

**Solutions**:
```powershell
# Use different port
.\Launcher.ps1 -FrontendPort 3001

# Check backend health
curl http://localhost:8001/health
```

### Debug Mode
Enable detailed logging for troubleshooting:
```powershell
.\Launcher.ps1 -DebugMode
```

Debug mode provides:
- Detailed startup sequence logging
- Environment variable values
- Process creation details
- Health check progress
- Error stack traces

### Log Files
Logs are stored in: `<RootPath>\logs\darbot_YYYYMMDD_HHMMSS.log`

Example log structure:
```
[2025-06-04 10:30:15] [INFO] Starting Darbot Agent Engine launcher...
[2025-06-04 10:30:15] [SUCCESS] Found configuration file: .env
[2025-06-04 10:30:16] [DEBUG] Loaded: COSMOSDB_ENDPOINT
[2025-06-04 10:30:16] [SUCCESS] Azure configuration validated
[2025-06-04 10:30:17] [INFO] Starting Backend API server on port 8001...
[2025-06-04 10:30:18] [SUCCESS] Backend API server started (PID: 12345)
```

## 📦 Building Executable

### Prerequisites for Building
```powershell
# Install PS2EXE module
Install-Module ps2exe -Scope CurrentUser -Force
Import-Module ps2exe
```

### Build Script
Create a build script (`Build-Launcher.ps1`):
```powershell
# Build configuration
$ScriptPath = ".\Launcher.ps1"
$ExePath = ".\DarbotLauncher.exe"
$IconPath = ".\assets\darbot-icon.ico"  # Optional

# Compile parameters
$BuildParams = @{
    InputFile = $ScriptPath
    OutputFile = $ExePath
    NoConsole = $false  # Keep console for output
    RequireAdmin = $false
    Title = "Darbot Agent Engine Launcher"
    Description = "All-in-one launcher for Darbot Agent Engine"
    Company = "Darbot Labs"
    Product = "Darbot Agent Engine"
    Copyright = "(c) 2025 Darbot Labs"
    Version = "1.0.0.0"
}

# Add icon if available
if (Test-Path $IconPath) {
    $BuildParams.IconFile = $IconPath
}

# Build executable
Invoke-PS2EXE @BuildParams

if (Test-Path $ExePath) {
    Write-Host "✅ Executable built successfully: $ExePath" -ForegroundColor Green
    
    # Get file size
    $Size = (Get-Item $ExePath).Length / 1MB
    Write-Host "📦 Size: $([math]::Round($Size, 2)) MB" -ForegroundColor Cyan
} else {
    Write-Host "❌ Build failed" -ForegroundColor Red
}
```

### Build Process
```powershell
# Run the build
.\Build-Launcher.ps1
```

### Executable Features
- **Standalone**: No PowerShell installation required on target machine
- **Self-contained**: All scripts embedded in executable
- **Silent Installation**: Can run without user interaction
- **Digital Signing**: Can be signed for enterprise deployment

## 🔧 Advanced Options

### Custom Installation Locations
```powershell
# Override root path detection
$env:DARBOT_ROOT_PATH = "C:\CustomPath\DarbotEngine"
.\Launcher.ps1
```

### Enterprise Deployment
For enterprise environments:

1. **Silent Configuration**:
   ```powershell
   # Create machine-wide config
   New-Item -Path "$env:ProgramData\Darbot" -ItemType Directory -Force
   Copy-Item ".env" "$env:ProgramData\Darbot\.env"
   ```

2. **Service Installation**:
   ```powershell
   # Install as Windows Service (requires additional service wrapper)
   sc create "DarbotEngine" binPath="C:\Path\To\DarbotLauncher.exe"
   ```

3. **Automated Updates**:
   ```powershell
   # Version checking and update mechanism
   $UpdateUrl = "https://releases.darbot.com/latest"
   # Implementation for automatic updates
   ```

### Performance Tuning
```powershell
# High-performance mode
$env:UVICORN_WORKERS = "4"
$env:UVICORN_LOG_LEVEL = "warning"
.\Launcher.ps1
```

### Development Mode
```powershell
# Development with hot reload
$env:DARBOT_DEV_MODE = "true"
.\Launcher.ps1 -DebugMode
```

## 📊 Monitoring and Maintenance

### Health Endpoints
- **Backend Health**: `http://localhost:8001/health`
- **Frontend Health**: `http://localhost:3000/health`
- **API Documentation**: `http://localhost:8001/docs`

### Process Monitoring
The launcher provides real-time process monitoring:
- Process status checking every second
- Automatic restart on unexpected exits
- Resource usage tracking
- Performance metrics logging

### Maintenance Tasks
Regular maintenance recommendations:
1. **Log Cleanup**: Remove old log files periodically
2. **Dependency Updates**: Update Python packages regularly
3. **Configuration Review**: Verify Azure credentials and permissions
4. **Performance Monitoring**: Check resource usage and response times

## 📚 Additional Resources

- **Azure Documentation**: [Azure OpenAI Service](https://docs.microsoft.com/azure/cognitive-services/openai/)
- **CosmosDB Documentation**: [Azure Cosmos DB](https://docs.microsoft.com/azure/cosmos-db/)
- **FastAPI Documentation**: [FastAPI](https://fastapi.tiangolo.com/)
- **Python Documentation**: [Python.org](https://python.org/doc/)

## 🤝 Support

For issues and support:
1. **Check Logs**: Review launcher logs for error details
2. **Debug Mode**: Run with `-DebugMode` for verbose output
3. **GitHub Issues**: Report issues on the project repository
4. **Documentation**: Reference this README and project documentation

---

**Version**: 1.0.0  
**Last Updated**: June 4, 2025  
**Compatibility**: Windows 10/11, PowerShell 5.1+, Python 3.8+
