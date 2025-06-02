@echo off
REM Thought into existence by Darbot
REM Batch script to start Darbot Agent Engine with Microsoft Edge

REM Define the paths
SET backendPath=d:\0GH_PROD\Darbot-Agent-Engine\src\backend
SET frontendPath=d:\0GH_PROD\Darbot-Agent-Engine\src\frontend
SET pythonPath=d:\0GH_PROD\Darbot-Agent-Engine\src

REM Set environment variables
SET PYTHONPATH=%pythonPath%

REM Kill any existing processes on ports 8001 and 3000 (needs admin privileges)
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8001') DO (
  TASKKILL /F /PID %%P 2>NUL
)

FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :3000') DO (
  TASKKILL /F /PID %%P 2>NUL
)

REM Start the backend server
echo Starting backend server...
START "Darbot Backend" /D "%backendPath%" python -m uvicorn app_kernel:app --host 0.0.0.0 --port 8001

REM Wait for the backend server to start
echo Waiting for backend server to start...
timeout /t 5 /nobreak > NUL

REM Start the frontend server
echo Starting frontend server...
START "Darbot Frontend" /D "%frontendPath%" python -m uvicorn frontend_server:app --host 127.0.0.1 --port 3000

REM Wait for the frontend server to start
echo Waiting for frontend server to start...
timeout /t 5 /nobreak > NUL

REM Launch Microsoft Edge with the application
echo Launching Microsoft Edge...
START msedge http://localhost:3000

echo Darbot Agent Engine started successfully with Microsoft Edge.
echo Press Ctrl+C to exit and stop the servers.

REM Keep the batch file running
pause
