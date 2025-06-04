// Thought into existence by Darbot
// Quick UI test script to verify theme toggle position

const { chromium } = require('playwright');

(async () => {
    console.log('🚀 Testing Theme Toggle Position...');
    
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
        await page.goto('http://localhost:3000', { 
            waitUntil: 'networkidle',
            timeout: 15000 
        });
        
        console.log('✅ App loaded successfully');
        
        // Take screenshot of initial state
        await page.screenshot({ 
            path: './screenshots/theme_toggle_initial.png', 
            fullPage: true 
        });
        console.log('📸 Initial screenshot taken');
        
        // Check if theme toggle is in the bottom left of sidebar
        const themeToggle = await page.locator('#themeToggle');
        const isVisible = await themeToggle.isVisible();
        
        if (isVisible) {
            console.log('✅ Theme toggle is visible');
            
            // Get the bounding box to verify position
            const boundingBox = await themeToggle.boundingBox();
            console.log('📍 Theme toggle position:', boundingBox);
            
            // Test theme toggle functionality
            await themeToggle.click();
            await page.waitForTimeout(1000);
            
            const currentTheme = await page.getAttribute('html', 'data-theme');
            console.log('🎨 Current theme after click:', currentTheme);
            
            // Take screenshot after theme change
            await page.screenshot({ 
                path: `./screenshots/theme_toggle_${currentTheme}.png`, 
                fullPage: true 
            });
            console.log(`📸 Screenshot taken for ${currentTheme} theme`);
            
            // Test switching back
            await themeToggle.click();
            await page.waitForTimeout(1000);
            
            const newTheme = await page.getAttribute('html', 'data-theme');
            console.log('🎨 Theme after second click:', newTheme);
            
            await page.screenshot({ 
                path: `./screenshots/theme_toggle_${newTheme}_final.png`, 
                fullPage: true 
            });
            console.log(`📸 Final screenshot taken for ${newTheme} theme`);
            
            console.log('✅ Theme toggle functionality test complete');
        } else {
            console.log('❌ Theme toggle not visible');
        }
        
        // Wait a moment for visual inspection
        await page.waitForTimeout(3000);
        
    } catch (error) {
        console.error('❌ Error during test:', error);
        await page.screenshot({ 
            path: './screenshots/theme_toggle_error.png', 
            fullPage: true 
        });
    } finally {
        await browser.close();
        console.log('🏁 Test complete');
    }
})();
