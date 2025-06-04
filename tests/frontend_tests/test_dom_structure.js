// Thought into existence by Darbot
// DOM Structure Inspector
// Quick test to examine the actual DOM structure

const { chromium } = require('playwright');

async function inspectDOM() {
    console.log('Starting DOM structure inspection...');
    
    const browser = await chromium.launch({ headless: false });
    const context = await browser.newContext();
    const page = await context.newPage();

    try {
        // Navigate to the application
        console.log('Navigating to http://localhost:3000/...');
        await page.goto('http://localhost:3000/');
        await page.waitForLoadState('networkidle');
        console.log('✅ Page loaded successfully');

        // Get the page title
        const title = await page.title();
        console.log(`Page title: "${title}"`);

        // Get the current URL
        const url = page.url();
        console.log(`Current URL: ${url}`);

        // Look for all textareas
        console.log('\nSearching for textareas...');
        const textareas = await page.locator('textarea').all();
        console.log(`Found ${textareas.length} textarea elements:`);
        
        for (let i = 0; i < textareas.length; i++) {
            const textarea = textareas[i];
            const id = await textarea.getAttribute('id');
            const className = await textarea.getAttribute('class');
            const placeholder = await textarea.getAttribute('placeholder');
            console.log(`  ${i + 1}. ID: ${id}, Class: ${className}, Placeholder: ${placeholder}`);
        }

        // Look for all buttons
        console.log('\nSearching for buttons...');
        const buttons = await page.locator('button').all();
        console.log(`Found ${buttons.length} button elements:`);
        
        for (let i = 0; i < buttons.length; i++) {
            const button = buttons[i];
            const id = await button.getAttribute('id');
            const className = await button.getAttribute('class');
            const text = await button.textContent();
            console.log(`  ${i + 1}. ID: ${id}, Class: ${className}, Text: "${text?.trim()}"`);
        }

        // Look for elements with specific IDs
        console.log('\nSearching for specific elements...');
        const targetIds = ['newTaskPrompt', 'startTaskButton'];
        
        for (const targetId of targetIds) {
            const element = page.locator(`#${targetId}`);
            const count = await element.count();
            if (count > 0) {
                const tagName = await element.first().evaluate(el => el.tagName);
                const className = await element.first().getAttribute('class');
                console.log(`✅ Found #${targetId}: ${tagName} with class "${className}"`);
            } else {
                console.log(`❌ Not found: #${targetId}`);
            }
        }

        // Look for quick task elements
        console.log('\nSearching for quick task elements...');
        const quickTaskSelectors = ['.quick-task', '.quick-task-card', '.task-card', '.card'];
        
        for (const selector of quickTaskSelectors) {
            const elements = page.locator(selector);
            const count = await elements.count();
            console.log(`${selector}: ${count} elements found`);
        }

        // Get the complete HTML structure of the main container
        console.log('\nGetting page structure...');
        const bodyContent = await page.locator('body').innerHTML();
        const preview = bodyContent.length > 500 ? bodyContent.substring(0, 500) + '...' : bodyContent;
        console.log('Body content preview:');
        console.log(preview);

        // Wait a bit to see the page
        console.log('\nWaiting 5 seconds for manual inspection...');
        await page.waitForTimeout(5000);

    } catch (error) {
        console.error('❌ Inspection failed:', error.message);
    } finally {
        await browser.close();
    }
}

// Run the inspection
inspectDOM().catch(console.error);
