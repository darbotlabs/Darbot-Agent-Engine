# Fixing CosmosDB RBAC Permissions for Darbot Agent Engine
# Thought into existence by Darbot

## Summary of the Issue

The system is successfully authenticating with Azure AD using `DefaultAzureCredential`, but the user doesn't have the required RBAC permissions to access CosmosDB.

Error from COSMOS_RBAC_SETUP.md:
```
Request blocked by Auth darbot-cosmos-dev2 : Request is blocked because principal [ebb01e50-f389-4f45-84a3-8d588f0b5bab] does not have required RBAC permissions to perform action [Microsoft.DocumentDB/databaseAccounts/readMetadata] on resource [/].
```

## Key Information

- **Principal ID:** `ebb01e50-f389-4f45-84a3-8d588f0b5bab`
- **Missing Action:** `Microsoft.DocumentDB/databaseAccounts/readMetadata`
- **Resource:** CosmosDB account (darbot-cosmos-dev, darbot-cosmos-dev2)
- **Current user:** dayour@microsoft.com
- **Subscription:** 99fc47d1-e510-42d6-bc78-63cac040a902 (FastTrack Azure Commercial Shared POC)
- **Resource Group:** Studio-CAT

## Step-by-Step Solution Using Azure Portal

### Step 1: Access the Azure Portal
1. Open a web browser and navigate to [Azure Portal](https://portal.azure.com)
2. Log in with your Microsoft account (dayour@microsoft.com)

### Step 2: Add RBAC Role for darbot-cosmos-dev
1. In the search bar at the top, type "darbot-cosmos-dev" and select the CosmosDB account from the results
2. In the left navigation menu, select "Access control (IAM)"
3. Click "+ Add" button, then choose "Add role assignment"
4. In the "Role" tab, search for and select "Cosmos DB Operator" role
5. Click "Next"
6. In the "Members" tab:
   - For Assignment type: Select "User, group, or service principal"
   - Click "+ Select members"
   - Search for "ebb01e50-f389-4f45-84a3-8d588f0b5bab" or "dayour@microsoft.com"
   - Select your account and click "Select"
7. Click "Review + assign" and then "Assign"
8. Repeat steps 3-7 for the "Cosmos DB Account Reader Role" role

### Step 3: Add RBAC Role for darbot-cosmos-dev2
1. In the search bar at the top, type "darbot-cosmos-dev2" and select the CosmosDB account from the results
2. Follow the same steps 2-8 as above to assign both "Cosmos DB Operator" and "Cosmos DB Account Reader Role" roles

### Step 4: Wait for Permissions to Propagate
- After assigning roles, wait approximately 5-30 minutes for the permissions to propagate throughout the Azure system
- This is a critical step as permission changes are not instantaneous

### Step 5: Verify Permissions
After waiting for permissions to propagate, you can verify access in one of two ways:

**Option 1: Using Azure Portal**
1. Navigate to either CosmosDB account
2. Select "Data Explorer" from the left menu
3. You should be able to view and manage databases and containers

**Option 2: Using Azure CLI (if decryption issues are resolved)**
```powershell
az cosmosdb sql database list --account-name darbot-cosmos-dev --resource-group Studio-CAT
```

**Option 3: Using Azure MCP CLI**
```powershell
azmcp cosmos database list --subscription 99fc47d1-e510-42d6-bc78-63cac040a902 --account-name darbot-cosmos-dev
```

### Step 6: Run with Azure Integration
Once permissions are verified, run the Darbot Agent Engine with Azure integration:

```powershell
.\scripts\run_servers.ps1 -UseAzure `
    -AzureOpenAIEndpoint "https://cat-studio-foundry.openai.azure.com/" `
    -AzureResourceGroup "Studio-CAT" `
    -AzureAIProjectName "cat-studio-foundry"
```

## Troubleshooting

If you're still encountering permission issues after following these steps:

1. **Check Principal ID**: Verify that the Principal ID you're granting permissions to is correct. You can find your current user's Principal ID by running:
   ```powershell
   az ad signed-in-user show --query id -o tsv
   ```

2. **Verify Azure AD Token**: Ensure your Azure AD token isn't expired. Sign out and sign back in to refresh your token.

3. **Check for Resource Locks**: Ensure there are no resource locks preventing role assignments.

4. **Elevated Permissions**: Ensure your account has Owner or User Access Administrator role at the subscription or resource group level to grant these permissions.

5. **Azure CLI Decryption Issues**: If encountering "Decryption failed" errors with Azure CLI commands, try clearing your Azure CLI token cache:
   ```powershell
   rm -r -fo "$env:USERPROFILE\.azure\msal_token_cache.bin"
   az login
   ```

## More Information

For more details, see:
- COSMOS_RBAC_SETUP.md
- RUNNING_WITH_AZURE.md
- [Azure Cosmos DB RBAC Documentation](https://aka.ms/cosmos-native-rbac)
