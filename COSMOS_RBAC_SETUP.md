# CosmosDB RBAC Setup Guide

*Thought into existence by Darbot*

## Current Status: ✅ Authentication Working, ❌ Permissions Missing

The keyless authentication implementation is working correctly. The system is successfully using `DefaultAzureCredential` and authenticating with Azure AD. However, RBAC permissions need to be configured.

## Error Analysis

```
Request blocked by Auth darbot-cosmos-dev2 : Request is blocked because principal [ebb01e50-f389-4f45-84a3-8d588f0b5bab] does not have required RBAC permissions to perform action [Microsoft.DocumentDB/databaseAccounts/readMetadata] on resource [/].
```

**Principal ID:** `ebb01e50-f389-4f45-84a3-8d588f0b5bab`
**Missing Action:** `Microsoft.DocumentDB/databaseAccounts/readMetadata`
**Resource:** `/` (CosmosDB account level)

## Required RBAC Roles

For the Darbot Agent Engine to function properly, assign one of these roles to the principal:

### Option 1: Built-in Role (Recommended)
- **Role:** `Cosmos DB Account Reader Role`
- **Permissions:** Read access to CosmosDB account metadata and data
- **Scope:** CosmosDB account `darbot-cosmos-dev2`

### Option 2: Custom Role (More Granular)
Create a custom role with these permissions:
- `Microsoft.DocumentDB/databaseAccounts/readMetadata`
- `Microsoft.DocumentDB/databaseAccounts/databases/read`
- `Microsoft.DocumentDB/databaseAccounts/databases/containers/read`
- `Microsoft.DocumentDB/databaseAccounts/databases/containers/items/read`
- `Microsoft.DocumentDB/databaseAccounts/databases/containers/items/create`
- `Microsoft.DocumentDB/databaseAccounts/databases/containers/items/upsert`
- `Microsoft.DocumentDB/databaseAccounts/databases/containers/items/delete`

## Setup Commands

### Azure CLI Commands
```bash
# Get your current user's object ID
az ad signed-in-user show --query id -o tsv

# Assign Cosmos DB Account Reader Role
az role assignment create \
  --assignee "ebb01e50-f389-4f45-84a3-8d588f0b5bab" \
  --role "Cosmos DB Account Reader Role" \
  --scope "/subscriptions/99fc47d1-e510-42d6-bc78-63cac040a902/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts/darbot-cosmos-dev2"

# Alternative: If you need write access, use Built-in Operator role
az role assignment create \
  --assignee "ebb01e50-f389-4f45-84a3-8d588f0b5bab" \
  --role "Cosmos DB Operator" \
  --scope "/subscriptions/99fc47d1-e510-42d6-bc78-63cac040a902/resourceGroups/YOUR_RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts/darbot-cosmos-dev2"
```

### Azure Portal Steps
1. Navigate to Azure Portal → CosmosDB → `darbot-cosmos-dev2`
2. Go to **Access control (IAM)**
3. Click **+ Add** → **Add role assignment**
4. Select role: **Cosmos DB Account Reader Role** (or **Cosmos DB Operator** for write access)
5. Assign access to: **User, group, or service principal**
6. Search for principal ID: `ebb01e50-f389-4f45-84a3-8d588f0b5bab`
7. Click **Save**

## Production Considerations

### For App Service Deployment
When deploying to Azure App Service, the system will use the App Service's Managed Identity instead of your local Azure CLI credentials.

1. **Enable Managed Identity** on the App Service
2. **Assign the same RBAC roles** to the App Service's Managed Identity
3. **Verify the Managed Identity** principal ID in the App Service → Identity section

### User Role Management
For the FastAPI RBAC implementation, users will need both:
1. **CosmosDB RBAC permissions** (for data access)
2. **Azure AD roles** (for application-level authorization like 'admin' role)

## Testing Commands

After assigning permissions, test the connection:

```bash
# Test basic connectivity
python check_cosmos.py

# Test full application integration
python test_cosmos_connection.py

# Test the FastAPI backend
cd src/backend
python -m uvicorn app_kernel:app --reload --port 8001
```

## Verification Checklist

- [ ] Principal `ebb01e50-f389-4f45-84a3-8d588f0b5bab` has CosmosDB RBAC role assigned
- [ ] Test scripts run without 403 Forbidden errors
- [ ] FastAPI backend can connect to CosmosDB
- [ ] User authentication and role extraction working in endpoints
- [ ] App Service Managed Identity configured (for production)

## Next Steps

1. Assign the RBAC permissions using one of the methods above
2. Run the test scripts to verify connectivity
3. Test the FastAPI backend endpoints
4. Deploy to Azure App Service and configure Managed Identity
5. Test end-to-end user authentication and authorization
