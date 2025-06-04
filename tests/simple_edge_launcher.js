// Thought into existence by Darbot
// Simple Edge launcher for Darbot Agent Engine

const { spawn } = require('child_process');
const http = require('http');

async function checkServer(port, name) {
    return new Promise((resolve) => {
        const req = http.get(`http://localhost:${port}`, (res) => {
            console.log(`✅ ${name} server is running on port ${port}`);
            resolve(true);
        });
        
        req.on('error', (err) => {
            console.log(`❌ ${name} server not accessible on port ${port}`);
            resolve(false);
        });
        
        req.setTimeout(5000, () => {
            console.log(`⏱️ ${name} server check timed out on port ${port}`);
            req.destroy();
            resolve(false);
        });
    });
}

async function launchWithSystemEdge() {
    console.log('🚀 Checking Darbot Agent Engine servers...');
    
    // Check both servers
    const backendRunning = await checkServer(8001, 'Backend');
    const frontendRunning = await checkServer(3000, 'Frontend');
    
    if (!backendRunning || !frontendRunning) {
        console.log('💡 Please run start_with_edge.bat to start both servers first');
        return;
    }
    
    console.log('🌐 Launching Microsoft Edge with Darbot Agent Engine...');
    
    // Launch Edge using system command
    const edgeProcess = spawn('cmd', ['/c', 'start', 'msedge', 'http://localhost:3000'], {
        detached: true,
        stdio: 'ignore'
    });
    
    // Also open FastAPI docs in a new tab
    setTimeout(() => {
        const docsProcess = spawn('cmd', ['/c', 'start', 'msedge', 'http://localhost:8001/docs'], {
            detached: true,
            stdio: 'ignore'
        });
        console.log('📋 FastAPI docs opened in Edge');
    }, 2000);
    
    console.log('✅ Microsoft Edge launched with:');
    console.log('   🎯 Main UI: http://localhost:3000');
    console.log('   📋 API Docs: http://localhost:8001/docs');
    console.log('');
    console.log('🔍 Now navigate in the browser to reproduce the error');
    console.log('   Then come back here to describe what you see');
}

launchWithSystemEdge().catch(console.error);
