# Fixing CosmosDB RBAC Permissions for Darbot Agent Engine

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

## Solution Steps

### Step 1: Add RBAC Role Assignment in Azure Portal

1. Go to: https://portal.azure.com
2. Navigate to Resource Group 'Studio-CAT'
3. Find the CosmosDB accounts (darbot-cosmos-dev and darbot-cosmos-dev2)
4. For each account, select Access control (IAM)
5. Click + Add → Add role assignment
6. Select role: 
   - For write access: 'Cosmos DB Operator' 
   - For read-only: 'Cosmos DB Account Reader Role'
7. Assign access to: 'User, group, or service principal'
8. Select members: Search for your account 'dayour@microsoft.com'
9. Click 'Review + assign'

### Step 2: Wait for Permissions to Propagate

After assigning roles, wait a few minutes (up to 30) for permissions to propagate.

### Step 3: Run with Azure Integration

After fixing permissions, run the Darbot Agent Engine with Azure integration:

```powershell
.\scripts\run_servers.ps1 -UseAzure `
    -AzureOpenAIEndpoint "https://cat-studio-foundry.openai.azure.com/" `
    -AzureResourceGroup "Studio-CAT" `
    -AzureAIProjectName "cat-studio-foundry"
```

## Alternative: Using Azure CLI Commands

When Azure CLI decryption issues are fixed, you can use this command:

```bash
# Assign Cosmos DB Operator Role (for write access)
az role assignment create \
  --assignee "ebb01e50-f389-4f45-84a3-8d588f0b5bab" \
  --role "Cosmos DB Operator" \
  --scope "/subscriptions/99fc47d1-e510-42d6-bc78-63cac040a902/resourceGroups/Studio-CAT/providers/Microsoft.DocumentDB/databaseAccounts/darbot-cosmos-dev"
```

## Verification Steps

1. After adding permissions, run this command to test CosmosDB access:
   ```powershell
   az cosmosdb database list --name darbot-cosmos-dev --resource-group Studio-CAT
   ```

2. If successful, you should see a list of databases in the CosmosDB account.

3. Run the application with Azure integration as described in Step 3 above.

## More Information

For more details, see:
- COSMOS_RBAC_SETUP.md
- RUNNING_WITH_AZURE.md
