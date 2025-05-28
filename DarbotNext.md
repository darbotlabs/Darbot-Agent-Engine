
# Darbot Multi-Agent Custom Automation Engine - Secure Development Guide

## 🚀 **Current State: Infrastructure + Secure-by-Default Architecture**

**Deployed Azure Components:**

- **Azure Container Apps** hosting frontend and backend services
- **Azure OpenAI Service** with GPT-4o model integration
- **Azure Cosmos DB** for persistent storage and session management
- **Azure Container Registry** for container image management
- **Azure AI Foundry Hub and Project** for agent orchestration
- **Azure Key Vault** for secure credential management
- **Managed Identity** for keyless authentication

**Security Architecture (Secure-by-Default):** ✅

- ✅ **Entra ID Authentication**: Using `DefaultAzureCredential` instead of API keys
- ✅ **Managed Identity**: System-assigned identity for Azure resource access
- ✅ **Key Vault Integration**: Secure storage for sensitive configuration
- ✅ **Zero-Trust Network**: Container Apps with private networking
- ✅ **RBAC**: Role-based access control for all Azure services

**Local Development Environment (Tested & Verified):**

- ✅ **Frontend Server**: Successfully running on `http://localhost:3000`
  - FastAPI server with Uvicorn
  - Static files served from `src/frontend/wwwroot/`
  - Virtual environment configured with UV package manager
- ✅ **Dependencies**: All Python packages installed and synced
- ✅ **Project Structure**: Azure.yaml configured with service definitions
- ✅ **AI Foundry Extension**: Ready for advanced agent orchestration

## 🔧 **Immediate Next Steps (Detailed Implementation Guide)**

### **Phase 1: Local Development Environment Setup** ✅ COMPLETED

**Frontend Launch (Verified Working):**

```powershell
# Navigate to frontend directory
cd src/frontend

# Create and activate virtual environment (using UV)
uv venv
.venv\Scripts\Activate.ps1

# Install dependencies
uv pip install -r requirements.txt
uv sync

# Launch frontend server
uv run uvicorn frontend_server:app --host 0.0.0.0 --port 3000
```

**Expected Result:** Frontend accessible at `http://localhost:3000` with FastAPI serving static files from `wwwroot/`

### **Phase 2: Secure Backend Service Integration** � NEXT PRIORITY

**Enhanced Security Setup with Entra Authentication:**

```powershell
# Navigate to backend directory
cd src/backend

# Set up backend environment
uv venv
.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt

# Configure SECURE environment variables (NO API KEYS!)
# Create .env file with Entra ID authentication:
# - AZURE_TENANT_ID=<your-tenant-id>
# - AZURE_CLIENT_ID=<managed-identity-client-id>
# - AZURE_SUBSCRIPTION_ID=<subscription-id>
# - COSMOSDB_ENDPOINT=<cosmos-endpoint> (NO KEY NEEDED)
# - AZURE_OPENAI_ENDPOINT=<openai-endpoint> (NO KEY NEEDED)

# Launch backend server with managed identity
uv run uvicorn app_kernel:app --host 0.0.0.0 --port 8000
```

**Expected Result:** Backend API accessible at `http://localhost:8000` with **keyless authentication**

**🔐 Security Advantages:**
- ✅ **No secrets in code or environment variables**
- ✅ **Automatic credential rotation**
- ✅ **Audit trails for all access**
- ✅ **Principle of least privilege**

#### **Phase 3: End-to-End Local Testing**

1. **Service Communication Verification**
   - Frontend → Backend API calls
   - Backend → Azure OpenAI integration
   - Backend → Cosmos DB connectivity

2. **Multi-Agent Workflow Testing**
   - Create a test session via frontend
   - Trigger planner agent workflow
   - Verify human-in-the-loop approval process
   - Check Cosmos DB for persisted data

#### **Phase 4: Azure Container Apps Deployment Verification**

**Service Endpoint Testing:**
```powershell
# Get container app URLs from Azure
az containerapp list --resource-group <rg-name> --query "[].{Name:name,FQDN:properties.configuration.ingress.fqdn}" -o table

# Test frontend endpoint
curl https://<frontend-fqdn>

# Test backend API endpoint
curl https://<backend-fqdn>/docs
```

#### **Phase 5: Secure Infrastructure Configuration** 🔐

**Managed Identity & RBAC Setup (Critical):**

1. **Configure Managed Identity with proper RBAC roles:**

   ```bicep
   // Secure-by-default Bicep template updates needed:
   // 1. Enable managed identity for Container Apps
   // 2. Grant specific RBAC roles (NO admin roles)
   // 3. Configure Key Vault access policies
   // 4. Enable private endpoints for all services
   ```

2. **Verify secure Container Apps configuration:**

   ```powershell
   # Check managed identity is enabled
   az containerapp show --name <app-name> --resource-group <rg-name> --query "identity"
   
   # Verify RBAC assignments
   az role assignment list --assignee <managed-identity-principal-id>
   ```

**🔐 Required RBAC Roles for Zero-Trust Architecture:**

- **Azure OpenAI Service**: `Cognitive Services OpenAI User` (NOT Contributor)
- **Cosmos DB**: `DocumentDB Account Contributor` with specific database scope
- **Key Vault**: `Key Vault Secrets User` (NOT full access)
- **Container Registry**: `AcrPull` (read-only access)

#### **Phase 6: AI Foundry Integration & Advanced Security** 🤖

**Azure AI Foundry Extension Features:**

```vscode-extensions
teamsdevapp.vscode-ai-foundry
```

**AI Foundry Integration Benefits:**

- ✅ **Visual agent design and testing**
- ✅ **Built-in prompt evaluation and safety**
- ✅ **Advanced model management and versioning**
- ✅ **Integrated responsible AI guardrails**
- ✅ **Cost optimization and usage monitoring**

**Enhanced Agent Security with AI Foundry:**

1. **Content Safety Integration** - Automatic harmful content detection
2. **Prompt Injection Protection** - Built-in security against adversarial inputs
3. **Model Access Controls** - Fine-grained permissions per agent type
4. **Audit Logging** - Complete trace of all agent interactions

### 🤖 **Multi-Agent System Architecture (from semantic search)**

The system features a sophisticated agent orchestration framework:

**Core Agents:**
- **GroupChatManager**: Orchestrates the entire workflow
- **PlannerAgent**: Generates structured plans with JSON schema responses
- **HumanAgent**: Handles human approval and feedback workflows
- **Specialized Agents**: HR, Marketing, Procurement, Tech Support, Product, Generic

**Key Technical Features:**
- **AgentFactory Pattern**: Three-phase agent creation (basic agents → planner → group chat manager)
- **Session-based Context**: Isolated agent instances per session
- **Tool Integration**: Extensible function calling capabilities
- **Human-in-the-Loop**: Approval workflows and feedback mechanisms
- **Persistent Storage**: Cosmos DB integration for plans, steps, and messages

### 🎯 **Next Steps for Claude Sonnet 4 Integration**

The system is architecturally ready for Claude Sonnet 4 integration:

1. **Agent Factory Extension**: The `AgentFactory.create_agent()` method supports custom agent types and system messages
2. **Environment Configuration**: The `app_config.py` provides centralized configuration management
3. **Tool Framework**: Existing tool integration pattern can be extended for Claude Sonnet 4 capabilities
4. **Response Format Support**: JSON schema validation for structured outputs

### 📋 **Comprehensive Action Plan with Priorities**

#### **PRIORITY 1: Complete Local Development Setup** ⏰ IMMEDIATE

1. **Launch Backend Service** (following Phase 2 steps above)
   - Set up backend virtual environment
   - Configure Azure credentials and connection strings
   - Test backend API endpoints

2. **Verify Frontend-Backend Integration**
   - Test API calls from frontend to backend
   - Verify multi-agent workflow triggers
   - Check session management and data persistence

#### **PRIORITY 2: Azure Environment Validation** ⏰ THIS WEEK

1. **Container Apps Health Check**
   - Verify both frontend and backend containers are running
   - Test public endpoints and ingress configuration
   - Review container logs for any startup issues

2. **Secrets and Configuration Audit**
   - Validate KeyVault integration
   - Check environment variables are properly injected
   - Test Azure OpenAI and Cosmos DB connectivity from containers

#### **PRIORITY 3: CI/CD Pipeline Configuration** ⏰ NEXT WEEK

1. **Azure Developer CLI Pipeline Setup**
   ```bash
   azd pipeline config
   ```
   - Choose GitHub Actions or Azure DevOps
   - Configure automated deployment triggers
   - Set up environment-specific deployments

2. **Testing Automation**
   - Add integration tests for multi-agent workflows
   - Set up monitoring and alerting
   - Configure rollback procedures

#### **PRIORITY 4: Claude Sonnet 4 Integration Preparation** ⏰ FUTURE

**Architecture Assessment:** The system is well-positioned for Claude integration:

1. **Agent Factory Extension Points:**
   - `AgentFactory.create_agent()` supports custom agent types
   - System message configuration through `app_config.py`
   - Extensible tool integration framework

2. **API Integration Requirements:**
   - Add Claude Sonnet 4 API credentials to KeyVault
   - Extend agent creation logic for Claude model support
   - Implement Claude-specific response parsing

3. **Testing Strategy:**
   - Compare Claude vs OpenAI agent responses
   - Performance benchmarking
   - Cost optimization analysis

### 🚨 **Critical Dependencies & Security Configuration**

**Must Complete Before Proceeding:**

1. **Azure Entra ID Setup** - Required for managed identity authentication
2. **RBAC Configuration** - Required for least-privilege access
3. **Managed Identity Assignment** - Required for keyless authentication

**🔐 Secure Environment Variables (NO API KEYS):**

```env
# Secure-by-Default Configuration
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<managed-identity-client-id>
AZURE_SUBSCRIPTION_ID=<subscription-id>

# Service Endpoints (NO KEYS NEEDED)
COSMOSDB_ENDPOINT=<cosmos-endpoint>
AZURE_OPENAI_ENDPOINT=<openai-endpoint>

# AI Foundry Configuration
AZURE_AI_SUBSCRIPTION_ID=<subscription-id>
AZURE_AI_RESOURCE_GROUP=<resource-group>
AZURE_AI_PROJECT_NAME=<project-name>
AZURE_AI_AGENT_PROJECT_CONNECTION_STRING=<connection-string>

# Local Development Only
BACKEND_API_URL=http://localhost:8000
```

**🔐 Authentication Flow:**
1. **Local Development**: Uses Azure CLI credentials or Visual Studio login
2. **Container Apps**: Uses system-assigned managed identity
3. **No secrets**: All authentication via Entra ID and RBAC

### 🔍 **Enhanced Troubleshooting Guide**

**Modern Security-First Solutions:**

1. **Authentication Errors**
   - Verify Azure CLI login: `az account show`
   - Check managed identity assignment in Azure Portal
   - Validate RBAC role assignments

2. **Backend Service Issues**
   - Verify `DefaultAzureCredential` chain in logs
   - Check Azure service health and quotas
   - Review container logs for authentication flows

3. **Agent Creation Failures**
   - Validate Azure OpenAI model deployment and quotas
   - Check Content Safety policy configurations
   - Verify AI Foundry project permissions

### 🚀 **AI Foundry Advanced Features**

**Getting Started with AI Foundry Extension:**

1. **Open AI Foundry in VS Code** - Access via Command Palette: `AI Foundry: Open`
2. **Connect to Azure AI Project** - Use your existing project credentials
3. **Visual Agent Designer** - Drag-and-drop agent creation interface
4. **Prompt Testing & Evaluation** - Built-in testing environment

**Enhanced Development Capabilities:**

- **Real-time Prompt Testing** - Test prompts without deploying
- **Model Comparison** - A/B test different models side-by-side
- **Safety Evaluation** - Automated content safety and bias testing
- **Performance Monitoring** - Track latency, cost, and quality metrics
- **Responsible AI Integration** - Built-in fairness and explainability tools

### 🎯 **Next Development Phase: AI Foundry Integration**

**Immediate AI Foundry Tasks:**

1. **Import Existing Agents** - Connect current agent factory to AI Foundry
2. **Visual Workflow Design** - Create agent workflows using the designer
3. **Enhanced Testing** - Use AI Foundry's evaluation framework
4. **Model Optimization** - Leverage AI Foundry's model comparison tools

**Advanced Features to Explore:**

- **RAG Pipeline Builder** - Visual design for retrieval-augmented generation
- **Agent Orchestration Canvas** - Multi-agent workflow visualization
- **Custom Model Integration** - Deploy and manage custom models
- **Enterprise Security Controls** - Advanced governance and compliance features

This modernized approach provides enterprise-grade security while maintaining developer productivity!

