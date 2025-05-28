# Project Setup Checklist

## 1. Clone the Repository
- Ensure you have Git installed.
- Open a terminal and run:
  ```
  git clone <repository-url>
  cd <repository-directory>
  ```

## 2. Install Prerequisites
- Ensure you have the following installed:
  - Azure CLI
  - Azure Dev CLI
  - Docker (if applicable)
- Validate prerequisites by running:
  ```
  ./scripts/validate-prerequisites.ps1
  ```

## 3. Configure Environment Variables
- Open the `resources.bicep` file located in the `infra` directory.
- Modify the `env` settings to include necessary environment variables for your application.

## 4. Set Up Azure Resources
- Ensure your Azure subscription is active and you have the necessary permissions.
- Run the following command to provision the infrastructure:
  ```
  azd up
  ```
  Alternatively, you can run:
  ```
  azd provision
  azd deploy
  ```

## 5. Configure CI/CD Pipeline
- Run the following command to set up the CI/CD pipeline:
  ```
  azd pipeline config
  ```
- Choose your preferred provider (GitHub or Azure DevOps) when prompted.

## 6. Build the Application
- If your project does not contain a Dockerfile, build the application using Buildpacks:
  ```
  azd package
  ```
- Run the built image locally to ensure it works:
  ```
  docker run -it <Image Tag>
  ```

## 7. Validate Azure Setup
- Run the Azure setup validation script:
  ```
  ./scripts/validate-azure-setup.ps1
  ```

## 8. Deploy the Application
- Deploy the application to Azure:
  ```
  azd deploy
  ```

## 9. Verify Deployment
- Run the deployment validation script:
  ```
  ./scripts/validate-deployment.ps1
  ```

## 10. Access the Application
- Visit the service endpoints listed after deployment to ensure the application is running.

## 11. Clean Up Resources (if necessary)
- If you need to clean up resources after testing, run:
  ```
  ./scripts/cleanup.ps1
  ``` 

## 12. Document Any Issues
- If you encounter any issues, document them in the logs for future reference.