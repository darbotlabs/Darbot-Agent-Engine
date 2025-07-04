# Set Up Authentication in Azure App Service

## Step 1: Add Authentication in Azure App Service configuration

1. Click on `Authentication` from left menu.

![Authentication](./images/azure-app-service-auth-setup/AppAuthentication.png)

2. Click on `+ Add Provider` to see a list of identity providers.

![Authentication Identity](./images/azure-app-service-auth-setup/AppAuthenticationIdentity.png)

3. Click on `+ Add Provider` to see a list of identity providers.

![Add Provider](./images/azure-app-service-auth-setup/AppAuthIdentityProvider.png)

4. Select the first option `Microsoft Entra Id` from the drop-down list. If `Create new app registration` is disabled, go to [Step 1a](#step-1a-creating-a-new-app-registration).

![Add Provider](./images/azure-app-service-auth-setup/AppAuthIdentityProviderAdd.png)

5. Accept the default values and click on `Add` button to go back to the previous page with the identity provider added.

![Add Provider](./images/azure-app-service-auth-setup/AppAuthIdentityProviderAdded.png)

### Step 1a: Creating a new App Registration

1. Click on `Home` and select `Microsoft Entra ID`.

![Microsoft Entra ID](./images/azure-app-service-auth-setup/MicrosoftEntraID.png)

2. Click on `App registrations`.

![App registrations](./images/azure-app-service-auth-setup/Appregistrations.png)

3. Click on `+ New registration`.

![New Registrations](./images/azure-app-service-auth-setup/NewRegistration.png)

4. Provide the `Name`, select supported account types as `Accounts in this organizational directory only(Contoso only - Single tenant)`, select platform as `Web`, enter/select the `URL` and register.

![Add Details](./images/azure-app-service-auth-setup/AddDetails.png)

5. After application is created successfully, then click on `Add a Redirect URL`.

![Redirect URL](./images/azure-app-service-auth-setup/AddRedirectURL.png)

6. Click on `+ Add a platform`.

![+ Add platform](./images/azure-app-service-auth-setup/AddPlatform.png)

7. Click on `Web`.

![Web](./images/azure-app-service-auth-setup/Web.png)

8. Enter the `web app URL` (Provide the app service name in place of XXXX) and Save. Then go back to [Step 1](#step-1-add-authentication-in-azure-app-service-configuration) and follow from _Point 4_ choose `Pick an existing app registration in this directory` from the Add an Identity Provider page and provide the newly registered App Name.
E.g. <<https://<< appservicename >>.azurewebsites.net/.auth/login/aad/callback>>

![Add Details](./images/azure-app-service-auth-setup/WebAppURL.png)

## RBAC-Only, Keyless Operation

- This application enforces Azure RBAC for all backend operations.
- All authentication is performed using Managed Identity and DefaultAzureCredential.
- No API keys or connection strings are used for CosmosDB or Azure OpenAI.
- User roles are extracted from Azure AD/Entra ID claims and enforced in backend endpoints.
- Sensitive operations (e.g., deleting all messages) require the 'admin' role.
- To assign roles, use Azure Portal or CLI to add users to the appropriate Azure AD groups or roles.
- For local development, ensure you are signed in with an account that has the required RBAC roles.

# Thought into existence by Darbot
