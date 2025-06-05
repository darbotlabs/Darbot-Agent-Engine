# Darbot Agent Engine Debugging Tools

<!-- Thought into existence by Darbot -->

## Task Submission Debugging Tools

This package contains several debugging and testing tools designed to help identify and fix issues with the Darbot Agent Engine's task submission functionality. The main focus was on addressing these critical issues:

1. ✅ The double API prefix problem causing 404 errors when submitting tasks
2. ✅ The CosmosDB authentication failure that prevents tasks from being saved 
3. ✅ Frontend proxy configuration and error handling improvements
4. ✅ Browser caching issues affecting API endpoint consistency

## Key Files and Tools

### Debugging Scripts

- **`debug_backend_api.py`**: Tests the backend API endpoints directly without going through the frontend server
- **`debug_frontend_proxy.py`**: Tests the frontend server's proxy functionality to ensure it correctly forwards requests to the backend
- **`server_monitor.py`**: Real-time monitor for both backend and frontend servers that checks their health status
- **`test_task_submission.py`**: End-to-end test for task submission to verify the complete flow works

### Validation and Testing

- **`validate_ui_fixes.js`**: Validates UI functionality with Playwright to check for visual and interactive issues
- **`tests/network_debug.js`**: Analyzes network requests and console logs to identify API communication problems
- **`test_api_endpoints.py`**: Tests backend API endpoints directly to check for availability and response formats

### Utility Scripts

- **`run_comprehensive_debug.ps1`**: PowerShell script to start both servers, run all debug tests, and collect logs
- **`validate_and_test.ps1`**: PowerShell script to validate fixes and run tests after changes are made

## Running the Debugging Tools

1. Start both the backend and frontend servers:
   ```powershell
   # Navigate to project directory
   cd d:\0GH_PROD\Darbot-Agent-Engine\
   
   # Run the comprehensive debugging script
   .\run_comprehensive_debug.ps1
   ```

2. Monitor server health in real-time:
   ```powershell
   python server_monitor.py
   ```

3. Test task submission flow:
   ```powershell
   python test_task_submission.py
   ```

## Key Fixes Implemented

1. **Frontend Proxy Approach**: Updated the frontend server to properly proxy API requests to the backend
   - Modified `frontend_server.py` to handle request forwarding with proper query parameters
   - Added error handling and logging for better debugging

2. **CosmosDB Fallback**: Improved the local memory store fallback mechanism when CosmosDB is unavailable
   - Enhanced `utils_kernel.py` to properly initialize LocalMemoryContext
   - Added proper error handling and logging during fallback

3. **API Endpoint Consistency**: Updated frontend code to use relative URLs for API requests
   - Changed API requests in `home.js` and `app.js` to use the proxy approach
   - Set `BACKEND_API_URL` to an empty string in frontend config

## Testing the Fixes

1. Run the frontend in local storage mode:
   ```powershell
   $env:USE_LOCAL_STORAGE = "true"
   cd d:\0GH_PROD\Darbot-Agent-Engine\src\backend
   python -m uvicorn app_kernel:app --host 0.0.0.0 --port 8001 --reload
   ```

2. In another terminal, run the frontend:
   ```powershell
   cd d:\0GH_PROD\Darbot-Agent-Engine\src\frontend
   python -m uvicorn frontend_server:app --host 127.0.0.1 --port 3000 --reload
   ```

3. Navigate to http://localhost:3000 in your browser to test the application

## Troubleshooting

If you encounter issues:

1. Check the logs in the `debug_logs` directory for detailed error messages
2. Run the `server_monitor.py` script to check server health
3. Test the API endpoints directly using `debug_backend_api.py`
4. Verify the proxy functionality with `debug_frontend_proxy.py`

## Future Improvements

- Add comprehensive error logging to both backend and frontend
- Implement retry mechanisms for API requests
- Add more detailed validation for the LocalMemoryContext implementation
- Create a dashboard for real-time monitoring of the application state

---
*Thought into existence by Darbot*
