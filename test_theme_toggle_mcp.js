// filepath: d:\0GH_PROD\Darbot-Agent-Engine\test_theme_toggle_mcp.js
// Thought into existence by Darbot
// Comprehensive Test for Theme Toggle Position using Playwright MCP

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    console.log('🚀 Testing Theme Toggle Position with Playwright...');
    
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
            path: path.join(screenshotsDir, 'theme_toggle_initial_state.png'), 
            fullPage: true 
        });
        console.log('📸 Initial screenshot taken');
        
        // Check if theme toggle is in the bottom left of sidebar
        console.log('🔍 Checking for theme toggle in bottom left of sidebar...');
        
        // Check theme toggle element
        const themeToggle = await page.locator('#themeToggle').first();
        const isVisible = await themeToggle.isVisible();
        
        if (isVisible) {
            console.log('✅ Theme toggle is visible');
            
            // Get the bounding box to verify position
            const boundingBox = await themeToggle.boundingBox();
            console.log('📍 Theme toggle position:', boundingBox);
            
            // Get parent container to verify it's in the theme-toggle-bottom container
            const container = await page.locator('.theme-toggle-bottom').first();
            const containerVisible = await container.isVisible();
            const containerBox = await container.boundingBox();
            
            console.log('📦 Theme toggle container:', containerVisible ? 'visible' : 'not visible');
            console.log('📦 Container position:', containerBox);
            
            // Test whether the theme toggle is actually at the bottom of the sidebar
            const sidebar = await page.locator('.asside').first();
            const sidebarBox = await sidebar.boundingBox();
            
            if (containerBox && sidebarBox) {
                const isAtBottom = (containerBox.y + containerBox.height) > (sidebarBox.y + sidebarBox.height - 100);
                console.log(`🧮 Is theme toggle at bottom? ${isAtBottom ? 'Yes' : 'No'}`);
            }
            
            // Test theme toggle functionality
            console.log('🔄 Testing theme toggle functionality...');
            
            // Check initial theme
            const initialTheme = await page.getAttribute('html', 'data-theme');
            console.log('🎨 Initial theme:', initialTheme);
            
            // Click the toggle
            await themeToggle.click();
            await page.waitForTimeout(1000);
            
            // Check new theme
            const newTheme = await page.getAttribute('html', 'data-theme');
            console.log('🎨 Theme after clicking toggle:', newTheme);
            
            // Take screenshot of theme change
            await page.screenshot({ 
                path: path.join(screenshotsDir, `theme_toggle_${newTheme}.png`), 
                fullPage: true 
            });
            console.log(`📸 Screenshot taken with ${newTheme} theme`);
            
            // Test switching back
            await themeToggle.click();
            await page.waitForTimeout(1000);
            
            // Check final theme
            const finalTheme = await page.getAttribute('html', 'data-theme');
            console.log('🎨 Theme after clicking toggle again:', finalTheme);
            
            // Take final screenshot
            await page.screenshot({ 
                path: path.join(screenshotsDir, `theme_toggle_${finalTheme}_final.png`), 
                fullPage: true 
            });
            console.log(`📸 Final screenshot taken with ${finalTheme} theme`);
            
            // Verify the icon and text changed
            const iconClass = await page.locator('#themeToggle i').getAttribute('class');
            const toggleText = await page.locator('#themeToggle span').textContent();
            
            console.log('🔣 Theme toggle icon class:', iconClass);
            console.log('📝 Theme toggle text:', toggleText);
            
            console.log('✅ Theme toggle functionality test complete');
            
            // Final result
            if (containerBox && isAtBottom) {
                console.log('🎯 RESULT: Theme toggle is successfully positioned at the bottom left of the sidebar');
            } else {
                console.log('❌ RESULT: Theme toggle is not properly positioned at the bottom left');
            }
        } else {
            console.log('❌ Theme toggle element not visible');
            
            // Debug: Check if it exists but is hidden
            const toggleExists = await page.locator('#themeToggle').count();
            console.log(`🔢 Theme toggle element exists but not visible: ${toggleExists > 0}`);
            
            // Debug: Take screenshot anyway
            await page.screenshot({ 
                path: path.join(screenshotsDir, 'theme_toggle_not_visible.png'), 
                fullPage: true 
            });
        }
        
        // Wait a moment for visual inspection
        console.log('⏳ Waiting for 3 seconds for visual inspection...');
        await page.waitForTimeout(3000);
        
    } catch (error) {
        console.error('❌ Error during test:', error);
        await page.screenshot({ 
            path: path.join(screenshotsDir, 'theme_toggle_error.png'), 
            fullPage: true 
        });
    } finally {
        await browser.close();
        console.log('🏁 Test complete');
    }
})();
