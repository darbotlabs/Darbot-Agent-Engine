// Thought into existence by Darbot
// Launch both the backend server and the frontend UI

const { exec, spawn } = require('child_process');
const http = require('http');
const path = require('path');
const fs = require('fs');

const rootDir = 'd:\\0GH_PROD\\Darbot-Agent-Engine';
const startBackendScript = path.join(rootDir, 'start_backend.ps1');
const frontendDir = path.join(rootDir, 'src', 'frontend');

// Check if backend server is running
async function checkServerRunning(port, name) {
    return new Promise((resolve) => {
        const req = http.get(`http://localhost:${port}`, (res) => {
            console.log(`✅ ${name} server is already running on port ${port}`);
            resolve(true);
        });
        
        req.on('error', () => {
            console.log(`❌ ${name} server is not accessible on port ${port}`);
            resolve(false);
        });
        
        req.setTimeout(2000, () => {
            console.log(`⏱️ ${name} server check timed out on port ${port}`);
            req.destroy();
            resolve(false);
        });
    });
}

// Start backend server
function startBackendServer() {
    return new Promise((resolve) => {
        console.log('🚀 Starting backend server...');
        
        const backendProcess = spawn('powershell', ['-File', startBackendScript], {
            detached: true,
            stdio: 'inherit'
        });
        
        backendProcess.unref();
        
        // Give it some time to start
        setTimeout(() => {
            console.log('⏳ Waiting for backend to initialize...');
            resolve();
        }, 5000);
    });
}

// Start frontend server
function startFrontendServer() {
    return new Promise((resolve) => {
        console.log('🚀 Starting frontend server...');
        
        const frontendProcess = spawn('python', ['-m', 'uvicorn', 'frontend_server:app', '--host', '127.0.0.1', '--port', '3000'], {
            cwd: frontendDir,
            detached: true,
            stdio: 'inherit'
        });
        
        frontendProcess.unref();
        
        // Give it some time to start
        setTimeout(() => {
            console.log('⏳ Waiting for frontend to initialize...');
            resolve();
        }, 3000);
    });
}

// Launch Edge browser
function launchEdge() {
    console.log('🌐 Launching Microsoft Edge with Darbot Agent Engine...');
    
    const edgeProcess = spawn('cmd', ['/c', 'start', 'msedge', 'http://localhost:3000'], {
        detached: true,
        stdio: 'ignore'
    });
    
    edgeProcess.unref();
    
    // Also open FastAPI docs in a new tab
    setTimeout(() => {
        const docsProcess = spawn('cmd', ['/c', 'start', 'msedge', 'http://localhost:8001/docs'], {
            detached: true,
            stdio: 'ignore'
        });
        docsProcess.unref();
        
        console.log('📋 FastAPI docs opened in Edge');
    }, 2000);
    
    console.log('✅ Microsoft Edge launched with:');
    console.log('   🎯 Main UI: http://localhost:3000');
    console.log('   📋 API Docs: http://localhost:8001/docs');
}

// Main execution sequence
async function main() {
    console.log('🔍 Checking server status...');
    
    // Check if servers are already running
    const backendRunning = await checkServerRunning(8001, 'Backend');
    const frontendRunning = await checkServerRunning(3000, 'Frontend');
    
    // Start backend if needed
    if (!backendRunning) {
        await startBackendServer();
    }
    
    // Start frontend if needed
    if (!frontendRunning) {
        await startFrontendServer();
    }
    
    // Launch Edge
    launchEdge();
    
    console.log('');
    console.log('🔍 Now navigate in the browser to test the application');
    console.log('   Then come back here to check for any errors');
}

// Run the main function
main().catch(console.error);
