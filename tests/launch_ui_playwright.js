// Thought into existence by Darbot
// Playwright script to launch Darbot Agent Engine UI in Microsoft Edge

const { chromium } = require('playwright');

async function checkBrowserInstallation() {
    try {
        console.log('🔍 Checking Microsoft Edge browser installation...');
        const browser = await chromium.launch({
            channel: 'msedge',
            headless: true
        });
        await browser.close();
        console.log('✅ Microsoft Edge is available');
        return true;
    } catch (error) {
        console.log('❌ Microsoft Edge not found, installing browsers...');
        console.log('Please wait while Playwright installs browsers...');
        return false;
    }
}

async function launchDarbotUI() {
    console.log('🚀 Starting Playwright with Microsoft Edge...');
    
    // Check if browser is installed
    const browserAvailable = await checkBrowserInstallation();
    if (!browserAvailable) {
        console.log('Please run: npx playwright install msedge');
        return;
    }
    
    let browser;
    try {
        // Launch Edge browser
        console.log('🌐 Launching Microsoft Edge...');
        browser = await chromium.launch({
            channel: 'msedge',
            headless: false,
            args: [
                '--start-maximized',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        });
        
        const context = await browser.newContext({
            viewport: null // Use full screen
        });
        
        const page = await context.newPage();
        
        console.log('🔍 Checking server status...');
        
        // First, check backend server
        try {
            console.log('📋 Accessing FastAPI docs at http://localhost:8001/docs...');
            await page.goto('http://localhost:8001/docs', { 
                waitUntil: 'load',
                timeout: 8000 
            });
            
            console.log('✅ Backend server is running - FastAPI docs loaded');
            
            // Take screenshot of API docs
            await page.screenshot({ 
                path: 'fastapi_docs_screenshot.png',
                fullPage: true 
            });
            console.log('📸 FastAPI docs screenshot saved');
            
        } catch (error) {
            console.log('❌ Backend server not accessible:', error.message);
        }
        
        // Navigate to main application
        console.log('🎯 Navigating to Darbot Agent Engine UI...');
        try {
            await page.goto('http://localhost:3000', { 
                waitUntil: 'load',
                timeout: 10000 
            });
            
            const title = await page.title();
            console.log('✅ Frontend loaded successfully!');
            console.log('📄 Page title:', title);
            
            // Set up comprehensive error monitoring
            page.on('console', msg => {
                const type = msg.type();
                const text = msg.text();
                if (type === 'error') {
                    console.log('🚨 Console Error:', text);
                } else if (type === 'warning') {
                    console.log('⚠️ Console Warning:', text);
                } else if (type === 'log' && text.includes('error')) {
                    console.log('📝 Console Log (Error):', text);
                }
            });
            
            page.on('pageerror', error => {
                console.log('🚨 Page Error:', error.message);
                console.log('📍 Stack:', error.stack);
            });
            
            page.on('requestfailed', request => {
                console.log('🚨 Failed Request:', request.url());
                console.log('   Failure text:', request.failure()?.errorText);
            });
            
            // Take UI screenshot
            await page.screenshot({ 
                path: 'ui_screenshot.png',
                fullPage: true 
            });
            console.log('📸 UI screenshot saved');
            
            console.log('🎉 Darbot Agent Engine is now running in Microsoft Edge!');
            console.log('👀 Monitor console for navigation errors');
            console.log('🛠️ Navigate in the browser to see the error, then press Ctrl+C here');
            
            // Keep script running for debugging
            let keepRunning = true;
            process.on('SIGINT', () => {
                keepRunning = false;
                console.log('\n👋 Shutting down...');
            });
            
            while (keepRunning) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
            
        } catch (error) {
            console.log('❌ Frontend error:', error.message);
            
            // Take error screenshot
            await page.screenshot({ path: 'error_screenshot.png' });
            console.log('📸 Error screenshot saved');
            
            // Get page content for debugging
            try {
                const content = await page.content();
                console.log('📄 Page content preview:', content.substring(0, 300) + '...');
            } catch (e) {
                console.log('Could not get page content');
            }
        }
        
    } catch (error) {
        console.error('❌ Failed to launch browser:', error.message);
    } finally {
        if (browser) {
            await browser.close();
            console.log('🔒 Browser closed');
        }
    }
}

// Handle graceful shutdown and start the application
launchDarbotUI().catch(console.error);
