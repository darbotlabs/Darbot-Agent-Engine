// Thought into existence by Darbot
// Test script that tries multiple browsers to find one that works

const { chromium, firefox, webkit } = require('playwright');

async function testBrowser(browserType, name) {
    console.log(`\n🚀 Testing ${name} browser...`);
    
    try {
        // Launch browser with minimal arguments
        const browser = await browserType.launch({ 
            headless: false,
            slowMo: 100  // Slow down operations for better visibility
        });
        
        const context = await browser.newContext();
        const page = await context.newPage();
        
        console.log(`✅ ${name} browser launched successfully`);
        
        // Navigate to app
        await page.goto('http://localhost:3000', { 
            waitUntil: 'networkidle',
            timeout: 15000 
        });
        
        console.log(`✅ Loaded app in ${name}`);
        
        // Take screenshot
        await page.screenshot({ 
            path: `./screenshots/${name.toLowerCase()}_test.png`, 
            fullPage: true 
        });
        
        console.log(`📸 Screenshot saved for ${name}`);
        
        // Wait briefly for visual inspection
        await page.waitForTimeout(3000);
        
        // Clean up
        await browser.close();
        return true;
    } catch (error) {
        console.error(`❌ ${name} browser test failed:`, error.message);
        return false;
    }
}

(async () => {
    let success = false;
    
    // Try Chromium first
    success = await testBrowser(chromium, 'Chromium');
    
    // If Chromium fails, try Firefox
    if (!success) {
        success = await testBrowser(firefox, 'Firefox');
    }
    
    // If Firefox fails, try WebKit
    if (!success) {
        success = await testBrowser(webkit, 'WebKit');
    }
    
    if (success) {
        console.log('\n✅ Successfully found a working browser');
    } else {
        console.log('\n❌ All browser tests failed');
    }
})();
