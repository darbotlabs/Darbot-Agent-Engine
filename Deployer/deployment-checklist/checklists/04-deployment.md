# Deployment Checklist for Azure Deployment

## Step-by-Step Deployment Process

### 1. Provision Infrastructure
- Run the command: `azd up`
- Alternatively, run the commands separately:
  - `azd provision`
  - `azd deploy`
- Validate that the service endpoints are accessible.

### 2. Configure Environment Variables
- Open the file: `resources.bicep`
- Modify the `env` settings to configure necessary environment variables.
- For secrets, ensure to add them as `secretRef` pointing to a `secrets` entry or a stored KeyVault secret.

### 3. Set Up CI/CD Pipeline
- Run the command: `azd pipeline config`
- Choose the appropriate provider:
  - For GitHub Actions, select `GitHub` and follow prompts to create `azure-dev.yml`.
  - For Azure DevOps, select `Azure DevOps` and follow prompts to create `azure-dev.yml`.

### 4. Validate Deployment
- Run the script: `scripts/validate-deployment.ps1`
- Check for any errors in the deployment status.
- Ensure all components are functioning as expected.

### 5. Monitor Application
- Access the service endpoints to confirm the application is running.
- If issues arise, refer to the logs for troubleshooting.

### 6. Cleanup Resources (if necessary)
- If the deployment is no longer needed, run the script: `scripts/cleanup.ps1` to remove unnecessary resources.

### Validation Rounds
- After each major step, validate the following:
  - **Infrastructure Provisioning**: Ensure all resources are created in Azure.
  - **Environment Configuration**: Confirm that environment variables are set correctly.
  - **CI/CD Pipeline**: Verify that the pipeline is configured and can trigger deployments.
  - **Deployment Validation**: Check that the application is accessible and functioning.

### Final Verification
- After deployment, run the script: `scripts/validate-deployment.ps1` again to ensure everything is operational.
- Document any issues encountered during the process for future reference.

This checklist ensures a structured approach to deploying the project to Azure, minimizing ambiguity and providing clear validation checkpoints.