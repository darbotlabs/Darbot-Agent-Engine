# Running Darbot Agent Engine with Azure Services

This guide explains how to run the Darbot Agent Engine using real Azure services instead of mock data.

## Prerequisites

1. **Azure CLI Installed** - Install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Azure Subscription** - You need an active Azure subscription
3. **Required Azure Resources** - The following Azure resources should be deployed:
   - Azure OpenAI Service
   - Azure AI Project/Azure AI Studio
   - Azure CosmosDB (optional, will fallback to local memory if not available)
4. **UV Package Manager** - Make sure you have the UV package manager installed

## Authentication

The application uses `DefaultAzureCredential` for authentication to Azure services, which means:

1. For local development, you need to be signed into the Azure CLI with `az login`
2. The account you use must have appropriate permissions to:
   - Access Azure OpenAI Service
   - Access Azure AI Studio projects
   - Access CosmosDB (if used)

## Running With Azure Integration

To run the application with real Azure services, use the `run_servers.ps1` script with the `-UseAzure` switch and the required parameters:

```powershell
# Basic usage with required parameters
.\run_servers.ps1 -UseAzure `
    -AzureOpenAIEndpoint "https://your-openai.openai.azure.com/" `
    -AzureResourceGroup "your-resource-group" `
    -AzureAIProjectName "your-ai-project"

# Advanced usage with all parameters
.\run_servers.ps1 -UseAzure `
    -AzureOpenAIEndpoint "https://your-openai.openai.azure.com/" `
    -AzureOpenAIDeploymentName "gpt-4o" `
    -AzureOpenAIApiVersion "2024-05-01-preview" `
    -AzureSubscriptionId "your-subscription-id" `
    -AzureResourceGroup "your-resource-group" `
    -AzureAIProjectName "your-ai-project" `
    -EnableAuth
```

## Parameter Details

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `-UseAzure` | Switch to enable Azure integration | Yes | N/A |
| `-AzureOpenAIEndpoint` | URL of your Azure OpenAI service | Yes | None |
| `-AzureOpenAIDeploymentName` | Name of your OpenAI model deployment | No | "gpt-4o" |
| `-AzureOpenAIApiVersion` | API version for Azure OpenAI | No | "2024-05-01-preview" |
| `-AzureSubscriptionId` | Your Azure Subscription ID | No | Current Az CLI subscription |
| `-AzureResourceGroup` | Resource group containing your Azure resources | Yes | None |
| `-AzureAIProjectName` | Name of your Azure AI Project | Yes | None |
| `-EnableAuth` | Enable authentication | No | False |

## Local Development Mode

If you want to run with mock services for development (no Azure required), simply run without the `-UseAzure` switch:

```powershell
.\run_servers.ps1
```

This will use mock data and local memory storage, suitable for development and testing without Azure dependencies.

## Troubleshooting

1. **Authentication Issues**:
   - Ensure you're logged in with `az login`
   - Check that your account has appropriate permissions
   - For managed identity errors, make sure you're using an account with proper RBAC

2. **Azure OpenAI Service Errors**:
   - Verify your deployment name matches the actual deployment in Azure
   - Check API version compatibility
   - Ensure your subscription has quota for the model you're using

3. **Azure AI Project Errors**:
   - Verify the project name and that it exists in the specified resource group
   - Ensure connection strings are valid
   - Check that your agent projects are properly set up in Azure AI Studio

4. **CosmosDB Issues**:
   - If CosmosDB connection fails, the app will fall back to local memory
   - Check the resource exists and your credential has access

## Development Tips

1. **Switching between cloud and local**: The script makes it easy to switch between Azure and local development. Use local development for basic testing and Azure for full integration testing.

2. **Logging**: Log files are created in the `debug_logs` directory with timestamps. Check these for detailed error information.

3. **Multiple configurations**: You can create small wrapper scripts with different Azure configurations for easy switching.

4. **Auth testing**: Use the `-EnableAuth` parameter when testing authentication features.

## Project Structure

The Darbot Agent Engine consists of:

- **Backend**: Python FastAPI service handling AI agents and Azure AI integration
- **Frontend**: Python FastAPI server serving the web interface
- **Scripts**: PowerShell scripts for running and managing the application
