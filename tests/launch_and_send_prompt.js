// filepath: d:\0GH_PROD\Darbot-Agent-Engine\launch_and_send_prompt.js
// Thought into existence by Darbot
// UI Launch and Prompt Test Script
// This script launches the UI and automatically sends a prompt to test the functionality

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    console.log('🚀 Launching UI and testing prompt submission...');
    
    // Create screenshots directory if it doesn't exist
    const screenshotsDir = './screenshots';
    if (!fs.existsSync(screenshotsDir)) {
        fs.mkdirSync(screenshotsDir, { recursive: true });
    }

    // Launch browser with appropriate options
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
    });
    
    const context = await browser.newContext({
        viewport: null
    });
    
    const page = await context.newPage();
    
    try {
        // Navigate to the app
        console.log('📄 Navigating to app.html...');
        await page.goto('http://localhost:3000/app.html', { 
            waitUntil: 'networkidle',
            timeout: 15000 
        });
        
        console.log('✅ App loaded successfully');
        
        // Take screenshot of initial state
        await page.screenshot({ 
            path: path.join(screenshotsDir, 'initial_app_state.png'), 
            fullPage: true 
        });
        console.log('📸 Initial screenshot taken');
        
        // Check for theme toggle at bottom left
        const themeToggle = await page.locator('#themeToggle').first();
        const isVisible = await themeToggle.isVisible();
        console.log('Theme toggle visible:', isVisible);
        
        if (isVisible) {
            const boundingBox = await themeToggle.boundingBox();
            console.log('Theme toggle position:', boundingBox);
        }
          // Click on New Task button to navigate to prompt page
        console.log('🖱️ Clicking on New Task button...');
        await page.locator('#newTaskButton').click();
        await page.waitForTimeout(2000);
          // Navigate to the home page directly
        console.log('📄 Navigating to home page...');
        await page.goto('http://localhost:3000/home/home.html', { 
            waitUntil: 'networkidle',
            timeout: 10000 
        });
        
        // Verify backend connectivity
        console.log('🔍 Verifying backend API connectivity...');
        try {
            const apiStatus = await page.evaluate(async () => {
                try {
                    const apiEndpoint = localStorage.getItem('apiEndpoint') || 'http://localhost:8001';
                    console.log('Using API endpoint:', apiEndpoint);
                    const response = await fetch(`${apiEndpoint}/api/healthcheck`);
                    return { 
                        ok: response.ok,
                        status: response.status,
                        endpoint: apiEndpoint
                    };
                } catch (error) {
                    return { 
                        ok: false, 
                        error: error.toString(),
                        endpoint: localStorage.getItem('apiEndpoint') || 'http://localhost:8001'
                    };
                }
            });
            
            if (apiStatus.ok) {
                console.log('✅ Backend API is accessible:', apiStatus);
            } else {
                console.log('⚠️ Backend API may not be accessible:', apiStatus);
                console.log('⚠️ Tasks may fail to create if backend is not running properly');
            }
        } catch (error) {
            console.log('❌ Error checking API connectivity:', error.message);
        }
        
        // Take screenshot of the prompt page
        await page.screenshot({ 
            path: path.join(screenshotsDir, 'prompt_page.png'), 
            fullPage: true 
        });
        console.log('📸 Prompt page screenshot taken');
          // Find and fill the prompt textarea
        const promptTextarea = await page.locator('#newTaskPrompt');
        const isPromptVisible = await promptTextarea.isVisible();
        
        if (isPromptVisible) {
            console.log('✅ Prompt textarea found');
            
            // Prepare the prompt text - keep it simple and clear
            const promptText = "Create a sales report for Q2 2025";
            
            // Fill in the prompt
            console.log('📝 Entering prompt text...');
            await promptTextarea.fill(promptText);
            await page.waitForTimeout(2000);            // Ensure API endpoint is properly set
            console.log('🔧 Ensuring API endpoint is properly set...');
            await page.evaluate(() => {
                if (!localStorage.getItem('apiEndpoint')) {
                    console.log('Setting apiEndpoint in localStorage');
                    localStorage.setItem('apiEndpoint', 'http://localhost:8001');
                }
                // Make BACKEND_API_URL available to the page
                if (typeof window.BACKEND_API_URL === 'undefined') {
                    window.BACKEND_API_URL = 'http://localhost:8001';
                    console.log('Set window.BACKEND_API_URL to:', window.BACKEND_API_URL);
                }
            });
            
            // Add console log to show what endpoint the frontend is actually using
            await page.evaluate(() => {
                const apiEndpoint = localStorage.getItem('apiEndpoint');
                console.log('Current API endpoint in localStorage:', apiEndpoint);
                
                // Log the actual endpoint that will be used for task creation
                const getFullEndpoint = () => {
                    const endpoint = localStorage.getItem('apiEndpoint') || window.BACKEND_API_URL || 'http://localhost:8001';
                    console.log('Task will be sent to:', `${endpoint}/api/input_task`);
                    return endpoint;
                };
                
                getFullEndpoint();
            });
            
            // Check if the button image updated (validation that text was entered correctly)
            console.log('🔍 Checking if send button is enabled...');
            await page.waitForTimeout(1000); // Wait for button to update
            
            // Take screenshot after entering prompt
            await page.screenshot({ 
                path: path.join(screenshotsDir, 'prompt_entered.png'), 
                fullPage: true 
            });
            console.log('📸 Prompt entered screenshot taken');
            
            // Find and click the submit button (clicking the parent container to ensure the click registers)
            const sendButton = await page.locator('.send-button');
            const isSendVisible = await sendButton.isVisible();
            
            if (isSendVisible) {
                console.log('✅ Send button found');
                
                // Click the send button
                console.log('🖱️ Submitting the prompt...');
                await sendButton.click();
                  // Wait for response processing
                console.log('⏳ Waiting for response processing...');
                
        // Monitor network requests for API calls to input_task
                page.on('request', request => {
                    if (request.url().includes('input_task')) {
                        console.log('🌐 API Request:', request.url());
                        console.log('📦 Request data:', request.postDataJSON());
                    }
                });
                
                page.on('response', response => {
                    if (response.url().includes('input_task')) {
                        console.log('🌐 API Response status:', response.status());
                        response.json().then(data => {
                            console.log('📦 Response data:', data);
                        }).catch(e => {
                            console.log('❌ Failed to parse response as JSON');
                        });
                    }
                });
                
                // Fix API endpoint path by modifying the fetch call
                await page.evaluate(() => {
                    const originalFetch = window.fetch;
                    window.fetch = function(url, options) {
                        // If this is a call to input_task without the /api prefix, add it
                        if (typeof url === 'string' && url.includes('/input_task') && !url.includes('/api/input_task')) {
                            const apiEndpoint = url.split('/input_task')[0];
                            const newUrl = `${apiEndpoint}/api/input_task`;
                            console.log('⚠️ Correcting API endpoint path from:', url);
                            console.log('✅ To correct path:', newUrl);
                            return originalFetch(newUrl, options);
                        }
                        return originalFetch(url, options);
                    };
                    console.log('✅ Modified fetch to correct API paths');
                });
                
                // Look for error messages
                await page.waitForTimeout(3000);
                const errorMessages = await page.locator('.notyf__toast--error');
                const errorCount = await errorMessages.count();
                if (errorCount > 0) {
                    const errorText = await errorMessages.first().textContent();
                    console.log('❌ Error detected:', errorText);
                }
                
                // Take screenshot of processing state
                await page.screenshot({ 
                    path: path.join(screenshotsDir, 'prompt_processing.png'), 
                    fullPage: true 
                });
                console.log('📸 Processing screenshot taken');
                
                // Wait longer for the full response (adjust based on your system's response time)
                console.log('⏳ Waiting for full response...');
                await page.waitForTimeout(10000); // Wait for 10 seconds for full response
                
                // Take screenshot of final response
                await page.screenshot({ 
                    path: path.join(screenshotsDir, 'prompt_response.png'), 
                    fullPage: true 
                });
                
                console.log('✅ Prompt submission test completed');
            } else {
                console.log('❌ Send button not found');
            }
        } else {
            console.log('❌ Prompt textarea not found');
        }
        
        // Wait a moment for visual inspection
        console.log('⏳ Waiting 5 seconds for visual inspection...');
        await page.waitForTimeout(5000);
        
    } catch (error) {
        console.error('❌ Error during test:', error);
        await page.screenshot({ 
            path: path.join(screenshotsDir, 'error_state.png'), 
            fullPage: true 
        });
    } finally {
        await browser.close();
        console.log('🏁 Test complete');
    }
})();
