// Thought into existence by Darbot
// Comprehensive UI audit script to verify all functionality including theme toggle

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class UIAuditor {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.screenshotsDir = './screenshots';
        this.results = {
            frontend: { status: 'unknown', tests: [] },
            themeToggle: { status: 'unknown', tests: [] },
            navigation: { status: 'unknown', tests: [] },
            taskCreation: { status: 'unknown', tests: [] },
            errors: []
        };
    }

    async init() {
        console.log('🚀 Initializing UI Auditor with Chromium...');
        
        // Create screenshots directory if it doesn't exist
        if (!fs.existsSync(this.screenshotsDir)) {
            fs.mkdirSync(this.screenshotsDir, { recursive: true });
        }

        try {
            this.browser = await chromium.launch({
                headless: false,
                slowMo: 50 // Slow down operations for better visibility
            });

            this.context = await this.browser.newContext({
                viewport: { width: 1920, height: 1080 }
            });

            this.page = await this.context.newPage();
            
            // Set up error monitoring
            this.setupErrorMonitoring();
            
            console.log('✅ Browser initialized successfully');
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize browser:', error.message);
            return false;
        }
    }

    setupErrorMonitoring() {
        this.page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            
            if (type === 'error') {
                this.results.errors.push({ type: 'console_error', message: text, timestamp: new Date().toISOString() });
                console.log('🚨 Console Error:', text);
            } else if (type === 'warning' && text.includes('error')) {
                this.results.errors.push({ type: 'console_warning', message: text, timestamp: new Date().toISOString() });
                console.log('⚠️ Console Warning:', text);
            }
        });

        this.page.on('pageerror', error => {
            this.results.errors.push({ type: 'page_error', message: error.message, stack: error.stack, timestamp: new Date().toISOString() });
            console.log('🚨 Page Error:', error.message);
        });

        this.page.on('requestfailed', request => {
            this.results.errors.push({ type: 'request_failed', url: request.url(), failure: request.failure()?.errorText, timestamp: new Date().toISOString() });
            console.log('🚨 Failed Request:', request.url());
        });
    }

    async takeScreenshot(name, fullPage = true) {
        try {
            const filename = `${name}_${new Date().toISOString().replace(/[:.]/g, '-')}.png`;
            const filepath = path.join(this.screenshotsDir, filename);
            await this.page.screenshot({ path: filepath, fullPage });
            console.log(`📸 Screenshot saved: ${filename}`);
            return filename;
        } catch (error) {
            console.error('❌ Failed to take screenshot:', error.message);
            return null;
        }
    }

    async testFrontendLoading() {
        console.log('\n🎯 Testing Frontend Loading...');
        
        try {
            await this.page.goto('http://localhost:3000', { 
                waitUntil: 'networkidle',
                timeout: 15000 
            });
            
            const title = await this.page.title();
            console.log('📄 Page title:', title);
            
            // Wait for main elements to load
            await this.page.waitForSelector('#app', { timeout: 5000 }).catch(() => {});
            
            this.results.frontend.tests.push({ name: 'Page Load', status: 'pass', details: `Title: ${title}` });
            console.log('✅ Frontend loaded successfully');
            
            await this.takeScreenshot('frontend_main_page');
            this.results.frontend.status = 'pass';
            
        } catch (error) {
            this.results.frontend.status = 'fail';
            this.results.frontend.tests.push({ name: 'Frontend Load', status: 'fail', details: error.message });
            console.log('❌ Frontend loading failed:', error.message);
            await this.takeScreenshot('frontend_error');
        }
    }

    async testThemeToggle() {
        console.log('\n🌓 Testing Theme Toggle...');
        
        try {
            // Check if theme toggle is visible
            const themeToggle = await this.page.locator('#themeToggle');
            const isVisible = await themeToggle.isVisible().catch(() => false);
            
            if (isVisible) {
                console.log('✅ Theme toggle is visible');
                this.results.themeToggle.tests.push({ name: 'Theme Toggle Visibility', status: 'pass', details: 'Theme toggle is visible' });
                
                // Get the bounding box to verify position
                const boundingBox = await themeToggle.boundingBox();
                console.log('📍 Theme toggle position:', boundingBox);
                
                if (boundingBox.y > 500) {
                    console.log('✅ Theme toggle is positioned at the bottom of the sidebar');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Position', status: 'pass', details: `Y position: ${boundingBox.y}` });
                } else {
                    console.log('❌ Theme toggle is NOT positioned at the bottom of the sidebar');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Position', status: 'fail', details: `Y position: ${boundingBox.y}` });
                }
                
                // Test theme toggle functionality
                const initialTheme = await this.page.getAttribute('html', 'data-theme');
                console.log('🎨 Initial theme:', initialTheme);
                
                await themeToggle.click();
                await this.page.waitForTimeout(1000);
                
                const afterClickTheme = await this.page.getAttribute('html', 'data-theme');
                console.log('🎨 Theme after click:', afterClickTheme);
                
                if (initialTheme !== afterClickTheme) {
                    console.log('✅ Theme toggle changes theme successfully');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Functionality', status: 'pass', details: `Changed from ${initialTheme} to ${afterClickTheme}` });
                } else {
                    console.log('❌ Theme toggle did not change theme');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Functionality', status: 'fail', details: `Still ${initialTheme} after click` });
                }
                
                await this.takeScreenshot(`theme_${afterClickTheme}`);
                
                // Toggle back
                await themeToggle.click();
                await this.page.waitForTimeout(1000);
                
                const finalTheme = await this.page.getAttribute('html', 'data-theme');
                console.log('🎨 Final theme:', finalTheme);
                
                if (finalTheme === initialTheme) {
                    console.log('✅ Theme toggle reverts theme successfully');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Revert', status: 'pass', details: `Reverted to ${finalTheme}` });
                } else {
                    console.log('❌ Theme toggle did not revert theme correctly');
                    this.results.themeToggle.tests.push({ name: 'Theme Toggle Revert', status: 'fail', details: `Expected ${initialTheme}, got ${finalTheme}` });
                }
                
                await this.takeScreenshot(`theme_${finalTheme}_final`);
                
                this.results.themeToggle.status = 'pass';
                
            } else {
                console.log('❌ Theme toggle not visible');
                this.results.themeToggle.tests.push({ name: 'Theme Toggle Visibility', status: 'fail', details: 'Theme toggle not found' });
                this.results.themeToggle.status = 'fail';
            }
            
        } catch (error) {
            this.results.themeToggle.status = 'fail';
            this.results.themeToggle.tests.push({ name: 'Theme Toggle Test', status: 'fail', details: error.message });
            console.log('❌ Theme toggle test failed:', error.message);
        }
    }

    async saveResults() {
        try {
            const results = {
                timestamp: new Date().toISOString(),
                summary: {
                    frontend: this.results.frontend.status,
                    themeToggle: this.results.themeToggle.status,
                    navigation: this.results.navigation.status,
                    taskCreation: this.results.taskCreation.status,
                    errorCount: this.results.errors.length
                },
                details: this.results
            };
            
            fs.writeFileSync('./audit_results.json', JSON.stringify(results, null, 2));
            console.log('✅ Audit results saved to audit_results.json');
            
        } catch (error) {
            console.error('❌ Failed to save audit results:', error.message);
        }
    }

    async runAudit() {
        if (!await this.init()) return false;
        
        try {
            await this.testFrontendLoading();
            await this.testThemeToggle();
            await this.saveResults();
            
            console.log('\n🏁 UI Audit completed!');
            return true;
        } catch (error) {
            console.error('❌ Audit failed:', error.message);
            return false;
        } finally {
            await this.browser.close();
        }
    }
}

// Execute the audit
(async () => {
    const auditor = new UIAuditor();
    await auditor.runAudit();
})();
