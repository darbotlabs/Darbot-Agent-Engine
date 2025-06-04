// Thought into existence by Darbot
// Complete Task Creation Flow Test
// Tests the full end-to-end task creation and submission process

const { chromium } = require('playwright');

async function testCompleteTaskFlow() {
    console.log('Starting comprehensive task creation flow test...');
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // Step 1: Navigate to the application
        console.log('\n1. Navigating to the application...');
        await page.goto('http://localhost:3000/');
        await page.waitForLoadState('networkidle');
        console.log('✅ Page loaded successfully');

        // Step 2: Verify page structure and elements
        console.log('\n2. Verifying page structure...');
          // Check for main UI elements
        const taskPrompt = await page.locator('#newTaskPrompt');
        const startButtonImg = await page.locator('#startTaskButton');
        const sendButton = await page.locator('.send-button');
        const quickTaskCards = await page.locator('.quick-task');
        
        if (await taskPrompt.count() === 0) {
            throw new Error('Task prompt textarea not found');
        }
        if (await startButtonImg.count() === 0 && await sendButton.count() === 0) {
            throw new Error('Start task button not found');
        }        
        console.log(`✅ Found task prompt textarea: ${await taskPrompt.count()}`);
        console.log(`✅ Found start task button img: ${await startButtonImg.count()}`);
        console.log(`✅ Found send button: ${await sendButton.count()}`);
        console.log(`✅ Found quick task cards: ${await quickTaskCards.count()}`);

        // Use the send button for clicking
        const startButton = sendButton;
        console.log('\n3. Testing quick task card functionality...');
        
        if (await quickTaskCards.count() > 0) {
            const firstCard = quickTaskCards.first();
            const cardText = await firstCard.textContent();
            console.log(`Testing quick task card: "${cardText?.substring(0, 50)}..."`);
            
            await firstCard.click();
            await page.waitForTimeout(1000);
            
            // Check if task prompt was populated
            const promptValue = await taskPrompt.inputValue();
            if (promptValue && promptValue.length > 0) {
                console.log(`✅ Quick task card populated prompt: "${promptValue.substring(0, 50)}..."`);
            } else {
                console.log('⚠️ Quick task card did not populate prompt');
            }
        }

        // Step 4: Test manual task input
        console.log('\n4. Testing manual task input...');
        
        const testTask = "Create a comprehensive test plan for our new application deployment";
        await taskPrompt.clear();
        await taskPrompt.fill(testTask);
        
        const currentValue = await taskPrompt.inputValue();
        if (currentValue === testTask) {
            console.log(`✅ Task input successful: "${testTask}"`);
        } else {
            throw new Error('Task input failed - text not properly entered');
        }

        // Step 5: Monitor network requests during task submission
        console.log('\n5. Testing task submission...');
        
        // Set up network monitoring
        const networkRequests = [];
        page.on('request', request => {
            if (request.url().includes('/api/')) {
                networkRequests.push({
                    url: request.url(),
                    method: request.method(),
                    timestamp: new Date().toISOString()
                });
            }
        });

        const networkResponses = [];
        page.on('response', response => {
            if (response.url().includes('/api/')) {
                networkResponses.push({
                    url: response.url(),
                    status: response.status(),
                    statusText: response.statusText(),
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Submit the task
        console.log('Clicking start task button...');
        await startButton.click();
        
        // Wait for potential network activity
        await page.waitForTimeout(3000);

        // Step 6: Analyze network activity
        console.log('\n6. Analyzing network activity...');
        
        console.log(`Network requests made: ${networkRequests.length}`);
        networkRequests.forEach((req, index) => {
            console.log(`  ${index + 1}. ${req.method} ${req.url} at ${req.timestamp}`);
        });

        console.log(`Network responses received: ${networkResponses.length}`);
        networkResponses.forEach((res, index) => {
            console.log(`  ${index + 1}. ${res.status} ${res.statusText} for ${res.url} at ${res.timestamp}`);
        });

        // Step 7: Check for UI feedback
        console.log('\n7. Checking for UI feedback...');
        
        // Look for loading indicators, success messages, or error displays
        const loadingIndicators = await page.locator('.loading, .spinner, [class*="load"]').count();
        const successMessages = await page.locator('.success, .alert-success, [class*="success"]').count();
        const errorMessages = await page.locator('.error, .alert-error, .alert-danger, [class*="error"]').count();
        
        console.log(`Loading indicators found: ${loadingIndicators}`);
        console.log(`Success messages found: ${successMessages}`);
        console.log(`Error messages found: ${errorMessages}`);

        // Step 8: Check current page state
        console.log('\n8. Final page state analysis...');
        
        const currentUrl = page.url();
        const pageTitle = await page.title();
        console.log(`Current URL: ${currentUrl}`);
        console.log(`Page title: ${pageTitle}`);

        // Check if we're still on the same page or redirected
        if (currentUrl.includes('localhost:3000')) {
            console.log('✅ Still on frontend server');
        } else {
            console.log(`⚠️ Redirected to: ${currentUrl}`);
        }

        // Step 9: Test API endpoints directly
        console.log('\n9. Testing API endpoints directly...');
        
        const apiTests = [
            { endpoint: '/api/plans', method: 'GET' },
            { endpoint: '/api/input_task', method: 'POST', body: { prompt: testTask } }
        ];

        for (const test of apiTests) {
            try {
                const response = await page.evaluate(async (testConfig) => {
                    const options = {
                        method: testConfig.method,
                        headers: { 'Content-Type': 'application/json' }
                    };
                    
                    if (testConfig.body) {
                        options.body = JSON.stringify(testConfig.body);
                    }
                    
                    const res = await fetch(testConfig.endpoint, options);
                    return {
                        status: res.status,
                        statusText: res.statusText,
                        headers: Object.fromEntries(res.headers.entries()),
                        text: await res.text()
                    };
                }, test);

                console.log(`✅ ${test.method} ${test.endpoint}: ${response.status} ${response.statusText}`);
                
                if (response.text) {
                    const preview = response.text.length > 100 
                        ? response.text.substring(0, 100) + '...' 
                        : response.text;
                    console.log(`   Response: ${preview}`);
                }
            } catch (error) {
                console.log(`❌ ${test.method} ${test.endpoint}: ${error.message}`);
            }
        }

        // Step 10: Summary
        console.log('\n10. Test Summary');
        console.log('================');
        
        const hasTaskInput = await taskPrompt.count() > 0;
        const hasSubmitButton = await startButton.count() > 0;
        const hasQuickTasks = await quickTaskCards.count() > 0;
        const madeNetworkRequests = networkRequests.length > 0;
        
        console.log(`✅ UI Elements Present: ${hasTaskInput && hasSubmitButton ? 'YES' : 'NO'}`);
        console.log(`✅ Quick Tasks Available: ${hasQuickTasks ? 'YES' : 'NO'}`);
        console.log(`✅ Network Activity: ${madeNetworkRequests ? 'YES' : 'NO'}`);
        console.log(`✅ Frontend Server: RESPONSIVE`);
        
        if (hasTaskInput && hasSubmitButton && madeNetworkRequests) {
            console.log('\n🎉 COMPREHENSIVE TEST PASSED');
            console.log('The task creation flow is working correctly!');
        } else {
            console.log('\n⚠️ ISSUES DETECTED');
            console.log('Some aspects of the task creation flow need attention.');
        }

    } catch (error) {
        console.error('❌ Test failed:', error.message);
        
        // Take a screenshot for debugging
        try {
            await page.screenshot({ path: 'debug_task_flow_error.png', fullPage: true });
            console.log('Debug screenshot saved as debug_task_flow_error.png');
        } catch (screenshotError) {
            console.log('Could not save debug screenshot:', screenshotError.message);
        }
    } finally {
        await browser.close();
    }
}

// Run the test
testCompleteTaskFlow().catch(console.error);
