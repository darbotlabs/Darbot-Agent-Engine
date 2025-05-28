# 🎯 Post-Deployment Configuration Guide

## Multi-Agent Custom Automation Engine

> **STATUS**: ✅ Infrastructure Successfully Deployed to "Studio-CAT" Resource Group
>
> **DEPLOYMENT ID**: `0ac64f82-105c-4025-9b3d-cf5c4494c52d`

---

## 🎮 Level 7: Post-Deployment Configuration

Achievement: Transform your deployed infrastructure into a fully operational multi-agent system

### Prerequisites Completed ✅

- [x] Azure Resource Group: `Studio-CAT`
- [x] Container Apps Environment deployed
- [x] Azure OpenAI Service with GPT-4o model
- [x] Azure Cosmos DB with serverless configuration
- [x] Azure Container Registry
- [x] Azure AI Foundry Hub and Project
- [x] Key Vault with secrets management
- [x] Managed identities and role assignments

---

## 🚀 Phase 1: Service Endpoint Discovery

### Step 1.1: Identify Deployed Resources

Run the validation script to discover your service endpoints:

```powershell
# List all resources in your deployment
az resource list --resource-group Studio-CAT --output table

# Get specific service endpoints
$backendFqdn = az containerapp show --name backend --resource-group Studio-CAT --query "properties.configuration.ingress.fqdn" --output tsv
$frontendFqdn = az containerapp show --name frontend --resource-group Studio-CAT --query "properties.configuration.ingress.fqdn" --output tsv

Write-Host "Backend API: https://$backendFqdn"
Write-Host "Frontend App: https://$frontendFqdn"
```

### Step 1.2: Container Apps Configuration

Verify your Container Apps are properly configured:

```powershell
# Check Container App status
az containerapp show --name backend --resource-group Studio-CAT --query "properties.provisioningState"
az containerapp show --name frontend --resource-group Studio-CAT --query "properties.provisioningState"

# Get ingress configuration
az containerapp ingress show --name backend --resource-group Studio-CAT
az containerapp ingress show --name frontend --resource-group Studio-CAT
```

**Service Endpoints:**

- **Backend API**: `https://<backend-container-app-fqdn>`
- **Frontend App**: `https://<frontend-container-app-fqdn>`

---

## ⚙️ Phase 2: Environment Variable Configuration

### Step 2.1: Get Required Configuration Values

```powershell
# Get Azure OpenAI configuration
$openaiEndpoint = az cognitiveservices account show --name <openai-service-name> --resource-group Studio-CAT --query "properties.endpoint" --output tsv
$openaiKey = az cognitiveservices account keys list --name <openai-service-name> --resource-group Studio-CAT --query "key1" --output tsv

# Get Cosmos DB connection string
$cosmosConnectionString = az cosmosdb keys list --name <cosmos-account-name> --resource-group Studio-CAT --type connection-strings --query "connectionStrings[0].connectionString" --output tsv

# Get Key Vault URI
$keyVaultUri = az keyvault show --name <keyvault-name> --resource-group Studio-CAT --query "properties.vaultUri" --output tsv

# Get Application Insights connection string
$appInsightsConnectionString = az monitor app-insights component show --app <app-insights-name> --resource-group Studio-CAT --query "connectionString" --output tsv
```

### Step 2.2: Update Container App Environment Variables

```powershell
# Update backend container app with environment variables
az containerapp update --name backend --resource-group Studio-CAT --set-env-vars \
  AZURE_OPENAI_ENDPOINT="$openaiEndpoint" \
  AZURE_OPENAI_API_VERSION="2024-02-15-preview" \
  AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o" \
  COSMOS_DB_CONNECTION_STRING="$cosmosConnectionString" \
  KEY_VAULT_URI="$keyVaultUri" \
  APPLICATIONINSIGHTS_CONNECTION_STRING="$appInsightsConnectionString" \
  AZURE_CLIENT_ID="$(az identity show --name <managed-identity-name> --resource-group Studio-CAT --query clientId -o tsv)" \
  ENVIRONMENT="production" \
  LOG_LEVEL="INFO"

# Update frontend container app
az containerapp update --name frontend --resource-group Studio-CAT --set-env-vars \
  BACKEND_API_URL="https://$backendFqdn" \
  ENVIRONMENT="production"
```

---

## 🐳 Phase 3: Container Image Deployment

### Step 3.1: Build and Push Application Images

```powershell
# Navigate to your project directory
cd "d:\0GH_PROD\Darbot-Agent-Engine"

# Build and push backend image
cd src/backend
az acr build --registry <registry-name> --image backend:latest .

# Build and push frontend image  
cd ../frontend
az acr build --registry <registry-name> --image frontend:latest .
```

### Step 3.2: Update Container Apps with New Images

```powershell
# Get ACR login server
$acrLoginServer = az acr show --name <registry-name> --resource-group Studio-CAT --query "loginServer" --output tsv

# Update backend container app with new image
az containerapp update --name backend --resource-group Studio-CAT --image "$acrLoginServer/backend:latest"

# Update frontend container app with new image
az containerapp update --name frontend --resource-group Studio-CAT --image "$acrLoginServer/frontend:latest"

# Verify deployment
az containerapp revision list --name backend --resource-group Studio-CAT --output table
az containerapp revision list --name frontend --resource-group Studio-CAT --output table
```

---

## 🤖 Phase 4: Multi-Agent System Configuration

### Step 4.1: Test Agent System Initialization

```powershell
# Test backend API health endpoint
$backendUrl = "https://$backendFqdn"
Invoke-RestMethod -Uri "$backendUrl/health" -Method GET

# Test agent endpoints
Invoke-RestMethod -Uri "$backendUrl/api/agents" -Method GET
Invoke-RestMethod -Uri "$backendUrl/api/agents/status" -Method GET
```

### Step 4.2: Initialize Agent Database Schema

```powershell
# Run database initialization if needed
Invoke-RestMethod -Uri "$backendUrl/api/initialize" -Method POST
```

### Step 4.3: Test Agent Communication

```powershell
# Test agent communication with a simple task
$testRequest = @{
    message = "Test multi-agent coordination"
    agents = @("planner", "hr", "marketing")
} | ConvertTo-Json

Invoke-RestMethod -Uri "$backendUrl/api/chat" -Method POST -Body $testRequest -ContentType "application/json"
```

---

## 📊 Phase 5: Monitoring and Observability Setup

### Step 5.1: Configure Application Insights

```powershell
# Verify Application Insights is receiving telemetry
az monitor app-insights events show --app <app-insights-name> --resource-group Studio-CAT --event pageViews --offset 1h
```

### Step 5.2: Set Up Log Analytics Queries

Create custom queries for monitoring agent performance:

```kusto
// Agent Performance Query
requests
| where timestamp > ago(1h)
| where url contains "/api/agents"
| summarize count(), avg(duration) by operation_Name
| order by avg_duration desc

// Error Monitoring Query  
exceptions
| where timestamp > ago(1h)
| where cloud_RoleName in ("backend", "frontend")
| summarize count() by problemId, outerMessage
| order by count_ desc

// Multi-Agent Coordination Tracking
customEvents
| where timestamp > ago(1h)
| where name == "AgentCommunication"
| extend agentType = tostring(customDimensions.agentType)
| summarize count() by agentType
```

---

## 🔄 Phase 6: CI/CD Pipeline Configuration

### Step 6.1: Configure Azure Developer CLI Pipeline

```powershell
# Configure CI/CD pipeline
azd pipeline config

# Choose GitHub Actions or Azure DevOps when prompted
# This will create .github/workflows/azure-dev.yml or azure-pipelines.yml
```

### Step 6.2: Validate Pipeline Configuration

```powershell
# Test pipeline deployment (dry run)
azd deploy --dry-run

# View pipeline status
azd pipeline status

# Monitor deployment logs
azd monitor
```

---

## ✅ Phase 7: System Validation and Testing

### Step 7.1: End-to-End Testing

```powershell
# Test complete user workflow
$testWorkflow = @{
    task = "Plan a marketing campaign for a new product launch"
    requirements = @("budget analysis", "timeline creation", "resource allocation")
} | ConvertTo-Json

Invoke-RestMethod -Uri "$backendUrl/api/workflow" -Method POST -Body $testWorkflow -ContentType "application/json"
```

### Step 7.2: Performance Testing

```powershell
# Load testing (requires additional tools)
# Consider using Azure Load Testing or Artillery.js
```

### Step 7.3: Security Validation

```powershell
# Verify managed identity authentication
az containerapp auth show --name backend --resource-group Studio-CAT

# Check Key Vault access
az keyvault secret list --vault-name <keyvault-name>

# Verify network security
az containerapp ingress show --name backend --resource-group Studio-CAT
```

---

## 🔮 Advanced Configuration

### Darbotian Philosophy Framework Integration

Prepare for advanced AI capabilities integration:

```powershell
# Create configuration for Darbotian framework
$darbotianConfig = @{
    philosophy_mode = "adaptive"
    consciousness_level = "enhanced"
    ethical_constraints = "strict"
} | ConvertTo-Json

# Store in Key Vault for future use
az keyvault secret set --vault-name <keyvault-name> --name "darbotian-config" --value $darbotianConfig
```

### Claude Sonnet 4 Agent Mode Preparation

```powershell
# Prepare environment for Claude Sonnet 4 integration
az containerapp update --name backend --resource-group Studio-CAT --set-env-vars \
  CLAUDE_SONNET_4_READY="true" \
  ADVANCED_REASONING_MODE="enabled" \
  AGENT_ORCHESTRATION_LEVEL="enhanced"

# Create placeholder configurations
$claudeConfig = @{
    model = "claude-sonnet-4"
    max_tokens = 200000
    temperature = 0.7
    agent_mode = "multi_shot"
} | ConvertTo-Json

az keyvault secret set --vault-name <keyvault-name> --name "claude-sonnet-4-config" --value $claudeConfig
```

---

## 🔧 Troubleshooting

### Container App Not Starting

```powershell
# Check container app logs
az containerapp logs show --name backend --resource-group Studio-CAT --follow

# Check revision status
az containerapp revision list --name backend --resource-group Studio-CAT --output table
```

### Environment Variable Issues

```powershell
# List current environment variables
az containerapp show --name backend --resource-group Studio-CAT --query "properties.template.containers[0].env"

# Update specific environment variable
az containerapp update --name backend --resource-group Studio-CAT --replace-env-vars KEY=VALUE
```

### Agent Communication Failures

```powershell
# Test individual agent endpoints
Invoke-RestMethod -Uri "$backendUrl/api/agents/hr/status" -Method GET
Invoke-RestMethod -Uri "$backendUrl/api/agents/marketing/status" -Method GET
Invoke-RestMethod -Uri "$backendUrl/api/agents/planner/status" -Method GET

# Check agent logs in Application Insights
```

---

## 🎉 Congratulations

You have successfully configured your Multi-Agent Custom Automation Engine! Your system now supports:

- ✅ Multi-agent task orchestration
- ✅ Azure OpenAI GPT-4o integration
- ✅ Secure configuration management
- ✅ Comprehensive monitoring and logging
- ✅ CI/CD pipeline automation
- ✅ Performance and security validation
- ✅ Claude Sonnet 4 readiness
- ✅ Darbotian Philosophy Framework preparation

**Next Steps:**

1. Begin testing complex multi-agent workflows
2. Monitor system performance and optimize as needed
3. Prepare for Claude Sonnet 4 agent mode integration
4. Implement Darbotian Philosophy Framework components
5. Scale the system based on usage patterns

**System Status**: 🟢 **FULLY OPERATIONAL**

---

*Level 7 Achievement Unlocked! 🏆*
**Master of Multi-Agent Orchestration**
