# DEPLOYMENT_TASKS.md

## 🚀 Deployment Tasks Checklist

Welcome to the gamified deployment process for the Multi-Agent Custom Automation Engine Solution Accelerator! Complete each level to successfully deploy your AI agent framework.

### 🎮 Level 1: Prerequisites Collection

**Objective**: Gather all necessary tools and permissions before embarking on your deployment journey.

- [ ] Ensure you have an active Azure subscription
- [ ] Verify you have permission to create resource groups and resources
- [ ] Install Azure CLI on your local machine
- [ ] Install Azure Developer CLI (`azd`) on your local machine
- [ ] Install Docker and ensure it's running
- [ ] Install PowerShell 7.0 or higher

**VALIDATION CHECKPOINT**:

- [ ] Complete prerequisites validation by running:

```powershell
.\scripts\validate-prerequisites.ps1
```

✅ Achievement: "Tool Collector" - All the required tools are installed!

### 🎮 Level 2: Azure Realm Preparation

**Objective**: Set up your Azure environment to host the AI agent framework.

- [ ] Log in to your Azure account with `az login`
- [ ] Select the appropriate subscription with `az account set --subscription <subscription-id>`
- [ ] Register required Azure resource providers:
  - [ ] Microsoft.CognitiveServices (for Azure OpenAI)
  - [ ] Microsoft.App (for Container Apps)
  - [ ] Microsoft.DocumentDB (for Cosmos DB)
  - [ ] Microsoft.ContainerRegistry

**VALIDATION CHECKPOINT**:

- [ ] Complete Azure setup validation:

```powershell
.\scripts\validate-azure-setup.ps1
```

✅ Achievement: "Azure Pathfinder" - Your Azure environment is ready!

### 🎮 Level 3: Project Configuration

**Objective**: Configure the project settings for deployment.

- [ ] Set the target resource group for deployment:

```bash
azd env set AZURE_RESOURCE_GROUP "Studio-CAT"
```

- [ ] Set the Azure region for deployment:

```bash
azd env set AZURE_LOCATION "eastus"
```

- [ ] Review the infrastructure files in the `infra` folder
- [ ] Customize any required parameters in the `infra/main.bicepparam` file

✅ Achievement: "Configuration Master" - Your project is properly configured!

### 🎮 Level 4: Deployment Quest

**Objective**: Deploy the Multi-Agent Custom Automation Engine to Azure.

- [ ] Start the deployment with a single command:

```bash
azd up
```

- [ ] Or deploy in stages if you prefer more control:

```bash
# First provision the infrastructure
azd provision

# Then deploy the application code
azd deploy
```
**VALIDATION CHECKPOINT**:

- [ ] Verify your deployment is successful:

```powershell
.\scripts\validate-deployment.ps1
```

✅ Achievement: "Deployment Champion" - Your AI agent framework is live!

### 🎮 Level 5: Final Verification

**Objective**: Test the deployed application and make sure everything works correctly.

- [ ] Access the service endpoints from the deployment output
- [ ] Verify the web interface is loading correctly
- [ ] Test the agent functionality with sample queries
- [ ] Check the logs for any errors or issues
- [ ] Review the metrics in Azure Monitor (if configured)

✅ Achievement: "Quality Assurance Expert" - Your system is fully verified!

### 🎮 Level 6: Cleanup (Optional Side Quest)

**Objective**: Clean up resources when they're no longer needed.

- [ ] Run the cleanup script with caution (only if you want to remove all resources):

```powershell
.\scripts\cleanup.ps1
```

- [ ] Confirm when prompted to avoid accidental deletion
- [ ] Verify resources have been removed in the Azure Portal

✅ Achievement: "Tidy Traveler" - Your Azure environment is clean!

### 🏆 Victory

**Congratulations!** You have successfully deployed the Multi-Agent Custom Automation Engine. Your AI agents are now ready to help automate complex tasks in your organization.

- [ ] Review the README.md for additional information and resources
- [ ] Explore the documentation in the `documentation` folder
- [ ] Check out sample questions in `documentation/SampleQuestions.md`
- [ ] Customize the solution as needed using `documentation/CustomizeSolution.md`

By completing all these levels, you have transformed from a deployment novice to an AI automation expert!
