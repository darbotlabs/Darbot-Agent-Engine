# Cleanup Checklist

This checklist outlines the steps to clean up resources after the deployment is complete. Follow these steps to ensure that all unnecessary resources are removed from your Azure subscription.

## Cleanup Steps

1. **Verify Deployment Completion**
   - Ensure that the deployment has been completed successfully by checking the deployment logs and status.

2. **Run Cleanup Script**
   - Execute the cleanup script to remove any resources that are no longer needed:
     ```powershell
     .\scripts\cleanup.ps1
     ```

3. **Review Resource Group**
   - Navigate to the Azure Portal and review the resource group used for the deployment.
   - Confirm that all resources created during the deployment are listed.

4. **Delete Unused Resources**
   - Manually delete any resources that were not automatically removed by the cleanup script.
   - Ensure that you do not delete any resources that are still in use or required for other applications.

5. **Check for Orphaned Resources**
   - Use Azure Resource Explorer or the Azure CLI to check for any orphaned resources that may not have been cleaned up.
   - Delete any orphaned resources identified.

6. **Confirm Cleanup Completion**
   - After performing the cleanup, revisit the Azure Portal to ensure that all unnecessary resources have been removed.
   - Document any resources that were retained for future reference.

7. **Log Cleanup Actions**
   - Record the cleanup actions taken in the logs directory for future audits:
     - Create a log entry in a file named `cleanup-log.txt` in the `logs` directory, detailing what resources were deleted and any issues encountered.

8. **Final Review**
   - Conduct a final review of the Azure subscription to ensure that no unnecessary costs will be incurred from leftover resources.

By following these steps, you can ensure that your Azure environment remains clean and cost-effective after deployment.