# Scripts Catalog

This catalog lists important scripts in the Darbot Agent Engine repository along with brief descriptions and their current locations.

## Deployment PowerShell Scripts

| Script | Description | Location |
|-------|-------------|---------|
| `configure_local_env.ps1` | Configure local environment variables for Azure deployment. | `Deployer/deployment-checklist/configure_local_env.ps1` |
| `setup_azure_production.ps1` | Prepare Azure resources for a production deployment. | `Deployer/deployment-checklist/setup_azure_production.ps1` |
| `run_azure_production.ps1` | Launch the engine using Azure services. | `Deployer/deployment-checklist/run_azure_production.ps1` |
| `run_fixed_ports.ps1` | Start the local environment on predefined ports. | `Deployer/deployment-checklist/run_fixed_ports.ps1` |
| `test_azure_access.ps1` | Validate Azure subscription permissions. | `Deployer/deployment-checklist/test_azure_access.ps1` |
| `clear_azure_cli_cache.ps1` | Remove stale Azure CLI credentials. | `Deployer/deployment-checklist/clear_azure_cli_cache.ps1` |
| `fix_cosmos_rbac.ps1` | Apply required RBAC permissions to Cosmos DB. | `Deployer/deployment-checklist/fix_cosmos_rbac.ps1` |
| `validate-deployment-config.ps1` | Ensure deployment configuration files are valid. | `Deployer/deployment-checklist/validate-deployment-config.ps1` |
| `validate-prerequisites.ps1` | Check that required tools and modules are installed. | `Deployer/deployment-checklist/scripts/validate-prerequisites.ps1` |
| `validate-azure-setup.ps1` | Verify Azure resource configuration. | `Deployer/deployment-checklist/scripts/validate-azure-setup.ps1` |
| `validate-deployment.ps1` | Perform post-deployment verification. | `Deployer/deployment-checklist/scripts/validate-deployment.ps1` |
| `validate-post-deployment.ps1` | Confirm services remain healthy after deployment. | `Deployer/deployment-checklist/scripts/validate-post-deployment.ps1` |
| `run_servers.ps1` | Start backend and frontend servers together. | `Deployer/deployment-checklist/scripts/run_servers.ps1` |
| `Launcher.ps1` | PowerShell launcher that coordinates all components. | `Deployer/deployment-checklist/scripts/Launcher.ps1` |

Additional deployment scripts are located in the `Deployer/deployment-checklist/scripts` folder.

## Playwright Test Scripts

| Script | Description | Location |
|-------|-------------|---------|
| `launch_ui_playwright.js` | Launch the UI in Microsoft Edge via Playwright. | `tests/launch_ui_playwright.js` |
| `multi_browser_test.js` | Exercise the UI across multiple browsers. | `tests/multi_browser_test.js` |
| `ui_audit_playwright.js` | Perform a comprehensive UI audit using Playwright. | `tests/ui_audit_playwright.js` |
| `playwright.config.js` | Configuration for Playwright test runs. | `tests/playwright.config.js` |

Other Playwright-based tests reside under the `tests` directory.

## Validation Scripts

| Script | Description | Location |
|-------|-------------|---------|
| `validate_production_task_creation.py` | Validate task creation in a production Azure environment. | `validate_production_task_creation.py` |
| `validation_summary_report.py` | Generate a summary report of task creation validation results. | `validation_summary_report.py` |

## Launcher Utilities

| Script | Description | Location |
|-------|-------------|---------|
| `Launcher.ps1` | PowerShell utility to coordinate deployment and start the complete stack. | `Deployer/deployment-checklist/scripts/Launcher.ps1` |
| `open_with_edge.bat` | Open the web interface in Microsoft Edge. | `open_with_edge.bat` |
| `start_with_edge.bat` | Launch backend and frontend, then open Edge. | `start_with_edge.bat` |

