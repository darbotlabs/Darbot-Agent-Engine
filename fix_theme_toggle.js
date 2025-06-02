// Thought into existence by Darbot
// Enhanced script to debug and fix the theme toggle functionality

const { chromium } = require('playwright');

(async () => {
    console.log('🔍 Starting Enhanced Theme Toggle Debug...');
    
    // Launch browser with developer tools enabled
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--start-maximized', '--auto-open-devtools-for-tabs']
    });
    
    const context = await browser.newContext({
        viewport: null
    });
    
    const page = await context.newPage();
    
    try {
        // Navigate to the app
        console.log('🌐 Navigating to the Darbot Agent Engine...');
        await page.goto('http://localhost:3000', { 
            waitUntil: 'networkidle',
            timeout: 15000 
        });
        
        console.log('✅ App loaded successfully');
        
        // Enhanced logging of page title and URL
        const title = await page.title();
        const url = page.url();
        console.log(`📄 Page title: ${title}`);
        console.log(`🔗 Current URL: ${url}`);
        
        // Take screenshot of initial state
        await page.screenshot({ 
            path: './screenshots/theme_debug_initial.png', 
            fullPage: true 
        });
        console.log('📸 Initial screenshot taken');
        
        // Get current theme
        const initialTheme = await page.evaluate(() => {
            return document.documentElement.getAttribute('data-theme') || 
                   document.body.getAttribute('data-theme') || 
                   document.body.classList.contains('dark-theme') ? 'dark' : 'light';
        });
        console.log(`🎨 Initial theme detected: ${initialTheme}`);
        
        // Check if theme toggle exists
        const themeToggleSelector = '#themeToggle';
        await page.waitForSelector(themeToggleSelector, { timeout: 5000 })
            .catch(() => console.log('⚠️ Theme toggle not found with selector: #themeToggle'));
        
        // Try alternative selectors if needed
        const alternativeSelectors = [
            '.theme-toggle', 
            '.dark-mode-toggle', 
            'button[aria-label="Toggle theme"]',
            '[data-testid="theme-toggle"]'
        ];
        
        let themeToggleElement = await page.$(themeToggleSelector);
        
        if (!themeToggleElement) {
            console.log('🔄 Trying alternative selectors...');
            for (const selector of alternativeSelectors) {
                themeToggleElement = await page.$(selector);
                if (themeToggleElement) {
                    console.log(`✅ Found theme toggle with alternative selector: ${selector}`);
                    break;
                }
            }
        }
        
        // If still not found, search for any button that might be the theme toggle
        if (!themeToggleElement) {
            console.log('🔎 Looking for any button that might control theme...');
            const buttons = await page.$$('button');
            for (const button of buttons) {
                const text = await button.textContent();
                const classes = await button.getAttribute('class');
                console.log(`Button found: "${text}" with classes "${classes}"`);
            }
        }
        
        if (themeToggleElement) {
            console.log('✅ Theme toggle element found');
            
            // Get element details
            const boundingBox = await themeToggleElement.boundingBox();
            const isVisible = await themeToggleElement.isVisible();
            const classes = await themeToggleElement.getAttribute('class');
            const elementHTML = await page.evaluate(el => el.outerHTML, themeToggleElement);
            
            console.log('📍 Element position:', boundingBox);
            console.log(`👁️ Visibility: ${isVisible ? 'Visible' : 'Not visible'}`);
            console.log(`🏷️ Classes: ${classes}`);
            console.log(`🧩 HTML: ${elementHTML}`);
            
            // Check if element is in viewport
            const isInViewport = await page.evaluate(el => {
                const rect = el.getBoundingClientRect();
                return (
                    rect.top >= 0 &&
                    rect.left >= 0 &&
                    rect.bottom <= window.innerHeight &&
                    rect.right <= window.innerWidth
                );
            }, themeToggleElement);
            console.log(`📱 In viewport: ${isInViewport ? 'Yes' : 'No'}`);
            
            // If not in viewport, scroll to it
            if (!isInViewport) {
                console.log('📜 Scrolling to theme toggle...');
                await themeToggleElement.scrollIntoViewIfNeeded();
                await page.waitForTimeout(1000);
            }
            
            console.log('🖱️ Clicking theme toggle...');
            await themeToggleElement.click();
            await page.waitForTimeout(2000);
            
            // Check new theme
            const newTheme = await page.evaluate(() => {
                return document.documentElement.getAttribute('data-theme') || 
                       document.body.getAttribute('data-theme') || 
                       document.body.classList.contains('dark-theme') ? 'dark' : 'light';
            });
            console.log(`🎨 Theme after clicking toggle: ${newTheme}`);
            
            // Check if theme actually changed
            if (initialTheme !== newTheme) {
                console.log('✅ Theme changed successfully!');
            } else {
                console.log('❌ Theme did not change!');
                
                // Deeper debugging - check for JavaScript errors
                console.log('⚙️ Checking for JavaScript errors during click...');
                
                await page.evaluate(() => {
                    const originalConsoleError = console.error;
                    console.error = (...args) => {
                        console.log('CONSOLE ERROR:', ...args);
                        originalConsoleError(...args);
                    };
                    
                    const themeToggle = document.querySelector('#themeToggle');
                    
                    if (themeToggle) {
                        // Check event listeners
                        const listeners = getEventListeners(themeToggle);
                        console.log('Event listeners:', listeners);
                    }
                });
            }
            
            // Take screenshot after toggle attempt
            await page.screenshot({ 
                path: './screenshots/theme_debug_after_click.png', 
                fullPage: true 
            });
            console.log('📸 Post-click screenshot taken');
            
            // Look for theme-related CSS variables
            const themeVars = await page.evaluate(() => {
                const rootStyles = getComputedStyle(document.documentElement);
                const result = {};
                // Common theme-related CSS variables
                const vars = [
                    '--background-color', '--text-color', '--primary-color',
                    '--background', '--foreground', '--theme-color'
                ];
                
                vars.forEach(v => {
                    const value = rootStyles.getPropertyValue(v);
                    if (value) result[v] = value;
                });
                
                return result;
            });
            
            console.log('🎭 Theme CSS variables:');
            Object.entries(themeVars).forEach(([key, value]) => {
                console.log(`  ${key}: ${value}`);
            });
            
            // Examine localStorage for theme settings
            const localStorage = await page.evaluate(() => {
                const result = {};
                for (let i = 0; i < window.localStorage.length; i++) {
                    const key = window.localStorage.key(i);
                    if (key && (key.includes('theme') || key.includes('dark') || key.includes('mode'))) {
                        result[key] = window.localStorage.getItem(key);
                    }
                }
                return result;
            });
            
            console.log('💾 Theme data in localStorage:');
            Object.entries(localStorage).forEach(([key, value]) => {
                console.log(`  ${key}: ${value}`);
            });
            
        } else {
            console.log('❌ Theme toggle element not found after all attempts!');
        }
        
        // Wait a moment for manual inspection
        console.log('⏳ Waiting for 10 seconds for manual inspection...');
        await page.waitForTimeout(10000);
        
    } catch (error) {
        console.error('❌ Error during test:', error);
        await page.screenshot({ 
            path: './screenshots/theme_debug_error.png', 
            fullPage: true 
        });
    } finally {
        console.log('🏁 Debug test complete. Keeping browser open for inspection...');
        // Keep the browser open for manual inspection
        // await browser.close();
    }
})();
