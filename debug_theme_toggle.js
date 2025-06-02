// Thought into existence by Darbot
// Debug script to check theme toggle visibility

const { chromium } = require('playwright');

(async () => {
    console.log('🔍 Debugging Theme Toggle...');
    
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized']
    });
    
    const context = await browser.newContext({
        viewport: null
    });
      const page = await context.newPage();
    
    // Monitor console errors
    page.on('console', msg => console.log('BROWSER LOG:', msg.text()));
    page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
    page.on('requestfailed', request => console.log('FAILED REQUEST:', request.url()));
    
    try {        // Navigate to the app (root serves app.html)
        await page.goto('http://localhost:3000', { 
            waitUntil: 'load',
            timeout: 15000 
        });
        
        console.log('✅ App loaded successfully');
        
        // Wait for dynamic content to load
        await page.waitForTimeout(3000);
        
        // Check page content first
        const pageTitle = await page.title();
        console.log('📄 Page title:', pageTitle);
        
        const html = await page.innerHTML('html');
        const bodyContent = html.substring(0, 500) + '...';
        console.log('📄 Page content sample:', bodyContent);
        
        // Check all elements in the sidebar
        const sidebarElements = await page.locator('.asside .menu').count();
        console.log('📊 Number of menu elements:', sidebarElements);
        
        // Check if theme toggle container exists
        const themeContainer = await page.locator('.theme-toggle-bottom');
        const containerExists = await themeContainer.count();
        console.log('📦 Theme toggle container count:', containerExists);
        
        if (containerExists > 0) {
            const containerVisible = await themeContainer.isVisible();
            console.log('👁️ Theme toggle container visible:', containerVisible);
        }
        
        // Check theme toggle element
        const themeToggle = await page.locator('#themeToggle');
        const toggleExists = await themeToggle.count();
        console.log('🔘 Theme toggle element count:', toggleExists);
        
        if (toggleExists > 0) {
            const toggleVisible = await themeToggle.isVisible();
            console.log('👁️ Theme toggle visible:', toggleVisible);
            
            const boundingBox = await themeToggle.boundingBox();
            console.log('📍 Theme toggle bounding box:', boundingBox);
        }
        
        // Get page HTML for debugging
        const pageContent = await page.content();
        const hasThemeToggle = pageContent.includes('themeToggle');
        const hasThemeContainer = pageContent.includes('theme-toggle-bottom');
        
        console.log('🔍 Page contains theme toggle ID:', hasThemeToggle);
        console.log('🔍 Page contains theme container class:', hasThemeContainer);
        
        // Take a screenshot for visual inspection
        await page.screenshot({ 
            path: './screenshots/debug_theme_toggle.png', 
            fullPage: true 
        });
        console.log('📸 Debug screenshot taken');
        
        // Wait for inspection
        await page.waitForTimeout(5000);
        
    } catch (error) {
        console.error('❌ Error during debug:', error);
    } finally {
        await browser.close();
        console.log('🏁 Debug complete');
    }
})();
