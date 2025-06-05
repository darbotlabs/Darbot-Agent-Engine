// Simple UI Task Creation Test for Darbot Agent Engine
// Tests the complete task creation flow through the UI

const { chromium } = require('playwright');

async function testTaskCreationFlow() {
    console.log('🚀 Starting UI Task Creation Test...');
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    try {
        // Navigate to the application
        console.log('🌐 Navigating to http://localhost:3000...');
        await page.goto('http://localhost:3000');
        await page.waitForTimeout(2000);
        
        // Take a screenshot of the main page
        await page.screenshot({ path: 'main_page.png', fullPage: true });
        console.log('📸 Main page screenshot saved');
        
        // Look for the task input area in the iframe
        console.log('🔍 Looking for iframe content...');
        const iframe = page.frameLocator('#viewIframe');
        
        // Wait for iframe to load
        await page.waitForTimeout(3000);
        
        // Check if we can find the task input textarea
        const taskInput = iframe.locator('#newTaskPrompt');
        
        if (await taskInput.isVisible()) {
            console.log('✅ Found task input textarea');
            
            // Fill in the task description
            const testTask = "I need help testing the Darbot Agent Engine setup and task creation flow";
            await taskInput.fill(testTask);
            console.log(`📝 Filled task: ${testTask}`);
            
            // Take screenshot with task filled
            await page.screenshot({ path: 'task_filled.png', fullPage: true });
            
            // Look for and click the start task button
            const startButton = iframe.locator('#startTaskButton');
            if (await startButton.isVisible()) {
                console.log('✅ Found start task button');
                await startButton.click();
                console.log('🚀 Clicked start task button');
                
                // Wait for response
                await page.waitForTimeout(5000);
                
                // Take screenshot after submission
                await page.screenshot({ path: 'task_submitted.png', fullPage: true });
                
                console.log('✅ Task creation flow completed successfully');
                return true;
            } else {
                console.log('❌ Start task button not found');
                return false;
            }
        } else {
            console.log('❌ Task input textarea not found');
            
            // Try to find quick task cards instead
            const quickTasks = iframe.locator('.quick-task');
            const quickTaskCount = await quickTasks.count();
            
            if (quickTaskCount > 0) {
                console.log(`✅ Found ${quickTaskCount} quick task options`);
                
                // Click the first quick task
                await quickTasks.first().click();
                console.log('🚀 Clicked first quick task');
                
                await page.waitForTimeout(3000);
                await page.screenshot({ path: 'quick_task_clicked.png', fullPage: true });
                
                return true;
            } else {
                console.log('❌ No quick tasks found either');
                return false;
            }
        }
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        await page.screenshot({ path: 'error_state.png', fullPage: true });
        return false;
    } finally {
        await browser.close();
        console.log('🔒 Browser closed');
    }
}

// Run the test
testTaskCreationFlow()
    .then(success => {
        if (success) {
            console.log('🎉 Test completed successfully!');
        } else {
            console.log('❌ Test failed!');
        }
    })
    .catch(error => {
        console.error('💥 Test crashed:', error);
    });
