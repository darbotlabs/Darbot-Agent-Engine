# Darbot Agent Engine - Development Backlog

<!-- Thought into existence by Darbot -->

## 📋 **Current Improvements Needed**

### 🔧 **Performance & Environment Issues**

#### **Module Import Path Fixes** 
- **Issue**: Imports without proper `backend.` module prefix causing ImportError
- **Root Cause**: Inconsistent module import structure, mixing relative and absolute imports
- **Solution Implemented**: Created script to standardize all imports with `backend.` prefix
- **Priority**: High (critical for running application)
- **Status**: ✅ Fixed - 2025-06-01
- **Impact**: Backend server now starts successfully with proper module resolution

#### **UV Package Manager Hardlink Warning**
- **Issue**: `warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.`
- **Root Cause**: Cache and target directories are on different filesystems, hardlinking may not be supported
- **Solution Options**:
  1. Set environment variable: `export UV_LINK_MODE=copy` 
  2. Use command flag: `--link-mode=copy`
  3. Configure UV settings globally
- **Priority**: Low (performance optimization)
- **Status**: 🟡 Identified
- **Impact**: Slower package installation times

#### **Azure AI Projects Import Fix** 
- **Issue**: `ImportError: cannot import name 'ResponseFormat' from 'azure.ai.projects.models'`
- **Root Cause**: The Azure AI SDK version doesn't contain the expected ResponseFormat class in the expected location
- **Solution Applied**: Created custom ResponseFormat class in kernel_agents/custom_response_format.py
- **Status**: ✅ Fixed
- **Impact**: Backend now imports correctly but may have compatibility issues with updated APIs

#### **Semantic Kernel Import Path Issues** 
- **Issue**: Import paths for Semantic Kernel have changed between versions
- **Current Error**: `Import "semantic_kernel.functions.kernel_function" could not be resolved`
- **Root Cause**: Semantic Kernel package structure doesn't match the import paths used in the code
- **Solution Applied**: Updated import paths for KernelFunction and KernelArguments to match the installed version
- **Status**: ✅ Fixed
- **Impact**: Semantic Kernel imports now resolved correctly

#### **Python Module Import Structure Issues** 
- **Issue**: Import paths in the codebase are inconsistent (absolute vs. relative)
- **Current Error**: `ImportError: cannot import name 'ResponseFormat' from 'backend.kernel_agents.custom_response_format'`
- **Root Cause**: The Python module system requires consistent use of absolute/relative imports and correct PYTHONPATH setting
- **Solution Applied**:
  1. Modified imports to use relative paths (e.g., from .custom_response_format import ResponseFormat)
  2. Added `__all__` to custom_response_format.py to ensure the class is properly exported
  3. Set PYTHONPATH to the src directory
- **Status**: ✅ Fixed
- **Impact**: Backend server now runs successfully
- **Root Cause**: Updated Azure AI package changed the class structure and names
- **Solution Applied**:
  1. Updated imports to use the new `ResponseFormat` class
  2. Modified response format implementation to use the new structure
  3. Updated `requirements.txt` with compatible package versions
- **Priority**: High (blocks backend startup)
- **Status**: 🟢 Resolved
- **Impact**: Backend server can now start up properly

#### **Entra ID Authentication for Azure AI Foundry**
- **Issue**: Connection to Azure AI services needed to switch from API key to Entra ID auth
- **Root Cause**: Updated security requirements for Azure AI services
- **Solution Applied**:
  1. Added Entra ID configuration in `.env` file
  2. Ensured DefaultAzureCredential is properly configured to use client_id
- **Priority**: High (required for Azure AI services)
- **Status**: 🟢 Resolved
- **Impact**: Secure, token-based authentication to Azure services
  
# Thought into existence by Darbot

---

## 🎯 **Backlog Categories**

### 🚀 **High Priority**
- [ ] Azure service configuration for full functionality
- [ ] Frontend-backend communication testing
- [ ] Multi-agent workflow validation

### 🔧 **Medium Priority**  
- [ ] UV hardlink performance optimization
- [ ] Error handling improvements
- [ ] Logging enhancement

### 💡 **Low Priority**
- [ ] UI/UX improvements
- [ ] Documentation updates
- [ ] Code refactoring

### 🔮 **Future Enhancements**
- [ ] Claude Sonnet 4 integration
- [ ] AI Foundry advanced features
- [ ] Custom agent development tools

---

## 📝 **Issue Template**

```markdown
#### **Issue Title**
- **Issue**: Brief description
- **Root Cause**: Technical details
- **Solution**: Proposed fix
- **Priority**: High/Medium/Low
- **Status**: 🔴 Critical / 🟡 Identified / 🟢 Resolved
- **Impact**: User/system impact
```

---

## 📊 **Progress Tracking**

- **Total Issues**: 6
- **Critical**: 1
- **High Priority**: 3  
- **Medium Priority**: 2
- **Low Priority**: 1
- **Resolved**: 3

**Last Updated**: June 2, 2025

#### **Backend Server Connection Issue**
- **Issue**: Failed to connect to backend server health endpoint
- **Root Cause**: Server may not be starting properly
- **Error**: 
{
  "detail": "Not Found"
}
- **Priority**: High
- **Status**: ✅ Fixed - 2025-06-01
- **Impact**: Backend functionality unavailable
- **Solution**: Fixed module import paths and improved error handling

#### **Double API Prefix Problem**
- **Issue**: Frontend code adding `/api` to URLs that already contained `/api`, causing 404 errors
- **Root Cause**: Inconsistent URL handling in frontend code
- **Solution**: Updated frontend code to use relative URLs and implemented proxy approach
- **Priority**: High
- **Status**: ✅ Fixed - 2025-06-01
- **Impact**: Task submission now works properly

#### **CosmosDB Authentication Failure**
- **Issue**: Tasks not being saved due to CosmosDB connection issues
- **Root Cause**: Local memory store fallback wasn't properly initialized
- **Solution**: Improved LocalMemoryContext with proper initialization and added missing methods
- **Priority**: High
- **Status**: ✅ Fixed - 2025-06-01
- **Impact**: Tasks can now be stored in local memory when CosmosDB is unavailable

#### **Frontend Proxy Error Handling**
- **Issue**: Frontend proxy not properly handling API requests
- **Root Cause**: Incomplete proxy implementation in frontend server
- **Solution**: Enhanced proxy implementation with better error handling, logging, and timeout settings
- **Priority**: Medium
- **Status**: ✅ Fixed - 2025-06-01
- **Impact**: API requests now properly forwarded to backend

#### **Browser Cache Interference**
- **Issue**: Frontend still using direct backend URL (http://localhost:8001) despite proxy configuration
- **Root Cause**: Browser caching and incomplete configuration update in some JavaScript files
- **Solution**: Updated all config.js references to use empty string for API endpoint and added cache busting mechanism
- **Priority**: Medium
- **Status**: ✅ Fixed - 2025-06-02
- **Impact**: Consistent API endpoint usage across frontend

#### **Environment Variable Propagation**
- **Issue**: Missing environment variables for Azure services during deployment
- **Root Cause**: Environment variables not properly set or propagated to containers
- **Solution**: Created comprehensive debug script to verify and set all required environment variables
- **Priority**: High
- **Status**: ✅ Fixed - 2025-06-02
- **Impact**: Both frontend and backend servers now start with all required configuration
