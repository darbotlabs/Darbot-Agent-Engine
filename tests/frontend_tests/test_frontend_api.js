// Thought into existence by Darbot
// Test script to validate frontend API connectivity

const { chromium } = require('playwright');

async function testFrontendAPI() {
    console.log('Starting frontend API connectivity test...');
    
    const browser = await chromium.launch({ headless: false });
    const page = await browser.newPage();
    
    // Listen to console messages
    page.on('console', msg => {
        console.log(`BROWSER: ${msg.text()}`);
    });
    
    // Listen to network requests
    page.on('request', request => {
        console.log(`REQUEST: ${request.method()} ${request.url()}`);
    });
    
    page.on('response', response => {
        console.log(`RESPONSE: ${response.status()} ${response.url()}`);
    });
    
    try {
        // Navigate to frontend
        console.log('Navigating to frontend...');
        await page.goto('http://localhost:3000/', { waitUntil: 'networkidle' });
        
        // Wait for the page to load
        await page.waitForTimeout(2000);
        
        // Test API call directly in browser
        console.log('Testing API call...');
        const apiResult = await page.evaluate(async () => {
            try {
                const response = await fetch('/api/plans');
                const data = await response.json();
                return { success: true, status: response.status, data };
            } catch (error) {
                return { success: false, error: error.message };
            }
        });
        
        console.log('API Result:', apiResult);
        
        // Check for task creation elements
        console.log('Checking for task creation elements...');
        const elements = await page.evaluate(() => {
            const taskForm = document.querySelector('#taskForm');
            const createTaskBtn = document.querySelector('#createTaskBtn');
            const taskDescription = document.querySelector('#taskDescription');
            
            return {
                hasTaskForm: !!taskForm,
                hasCreateTaskBtn: !!createTaskBtn,
                hasTaskDescription: !!taskDescription,
                taskFormVisible: taskForm ? !taskForm.hidden && taskForm.style.display !== 'none' : false
            };
        });
        
        console.log('UI Elements:', elements);
        
        // If elements exist, try to create a task
        if (elements.hasTaskForm && elements.hasCreateTaskBtn) {
            console.log('Attempting to create a test task...');
            
            await page.fill('#taskDescription', 'Test task creation from automated test');
            await page.click('#createTaskBtn');
            
            // Wait for response
            await page.waitForTimeout(3000);
            
            // Check for any success/error messages
            const messages = await page.evaluate(() => {
                const alerts = Array.from(document.querySelectorAll('.alert, .error, .success, .message'));
                return alerts.map(alert => alert.textContent);
            });
            
            console.log('Messages after task creation:', messages);
        }
        
    } catch (error) {
        console.error('Test failed:', error);
    } finally {
        await browser.close();
    }
}

testFrontendAPI().catch(console.error);
