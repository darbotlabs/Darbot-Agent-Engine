# Azure Setup Checklist

## Azure Setup Checklist

1. **Verify Azure Subscription**
   - Ensure you have an active Azure subscription with the necessary permissions to create resources.

2. **Check Azure OpenAI Quota**
   - Confirm that your Azure subscription has sufficient quota for Azure OpenAI Service. Refer to the [quota check instructions guide](../documentation/quota_check.md).

3. **Select Azure Region**
   - Choose an Azure region where the required services (Azure OpenAI Service, Azure AI Search, Azure Semantic Search) are available. Example regions include:
     - East US
     - East US2
     - Japan East
     - UK South
     - Sweden Central

4. **Set Up Resource Group**
   - Create a new resource group in Azure for organizing your resources. Use the Azure Portal or Azure CLI:
     ```
     az group create --name <your-resource-group-name> --location <your-region>
     ```

5. **Deploy Azure Resources**
   - Run the following command to provision the necessary infrastructure:
     ```
     azd up
     ```
   - Alternatively, run the commands separately:
     ```
     azd provision
     azd deploy
     ```

6. **Configure Environment Variables**
   - Modify the `env` settings in `resources.bicep` to configure any necessary environment variables for your services.

7. **Set Up Azure Key Vault**
   - Create an Azure Key Vault to securely store secrets and connection strings required for your application.

8. **Configure Managed Identity**
   - Ensure that Managed Identity is enabled for your Azure resources to facilitate secure communication.

9. **Validate Azure Setup**
   - Run the validation script to ensure that the Azure environment is correctly configured:
     ```
     .\scripts\validate-azure-setup.ps1
     ```

10. **Review Azure Resource Configuration**
    - Check the Azure Portal to confirm that all resources have been created successfully and are in the correct state.

11. **Document Azure Setup**
    - Update any relevant documentation with details about the Azure setup, including resource group name, region, and any specific configurations made.

## Validation Round
- After completing the checklist, perform a final review to ensure all steps have been executed correctly and that the Azure environment is ready for project deployment.