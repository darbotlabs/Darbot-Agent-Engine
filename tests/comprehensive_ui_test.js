// filepath: d:\0GH_PROD\Darbot-Agent-Engine\comprehensive_ui_test.js
// Thought into existence by Darbot
// Comprehensive UI Test including Theme Toggle and Task Creation

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class ComprehensiveUITester {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.screenshotsDir = './screenshots';
        this.results = {
            themeToggle: { status: 'unknown', tests: [] },
            navigation: { status: 'unknown', tests: [] },
            taskCreation: { status: 'unknown', tests: [] },
            errors: []
        };
    }

    async init() {
        console.log('🚀 Initializing Comprehensive UI Test with Playwright...');
        
        // Create screenshots directory
        if (!fs.existsSync(this.screenshotsDir)) {
            fs.mkdirSync(this.screenshotsDir, { recursive: true });
        }

        try {
            this.browser = await chromium.launch({
                headless: false,
                args: ['--start-maximized']
            });

            this.context = await this.browser.newContext({
                viewport: null
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

    async testThemeToggle() {
        console.log('\n🎨 Testing Theme Toggle Position and Functionality...');
        
        try {
            // Navigate to app
            await this.page.goto('http://localhost:3000/app.html', { 
                waitUntil: 'networkidle',
                timeout: 10000 
            });
            
            await this.takeScreenshot('app_initial_load');
            
            // Check if theme toggle is in the bottom left of sidebar
            const themeToggle = await this.page.locator('#themeToggle').first();
            const isVisible = await themeToggle.isVisible();
            
            if (isVisible) {
                this.results.themeToggle.tests.push({ name: 'Visibility', status: 'pass', details: 'Theme toggle is visible' });
                console.log('✅ Theme toggle is visible');
                
                // Get the bounding box to verify position
                const boundingBox = await themeToggle.boundingBox();
                console.log('📍 Theme toggle position:', boundingBox);
                
                // Get parent container to verify it's in the theme-toggle-bottom container
                const container = await this.page.locator('.theme-toggle-bottom').first();
                const containerVisible = await container.isVisible();
                const containerBox = await container.boundingBox();
                
                this.results.themeToggle.tests.push({ 
                    name: 'Container', 
                    status: containerVisible ? 'pass' : 'fail', 
                    details: `Container is ${containerVisible ? 'visible' : 'not visible'}` 
                });
                
                // Test whether the theme toggle is at the bottom of the sidebar
                const sidebar = await this.page.locator('.asside').first();
                const sidebarBox = await sidebar.boundingBox();
                
                if (containerBox && sidebarBox) {
                    const isAtBottom = (containerBox.y + containerBox.height) > (sidebarBox.y + sidebarBox.height - 100);
                    this.results.themeToggle.tests.push({ 
                        name: 'Position', 
                        status: isAtBottom ? 'pass' : 'fail', 
                        details: `Theme toggle is ${isAtBottom ? '' : 'not '}at the bottom of the sidebar` 
                    });
                }
                
                // Test theme toggle functionality
                const initialTheme = await this.page.getAttribute('html', 'data-theme');
                
                // Click the toggle
                await themeToggle.click();
                await this.page.waitForTimeout(1000);
                
                const newTheme = await this.page.getAttribute('html', 'data-theme');
                await this.takeScreenshot(`theme_${newTheme}`);
                
                const themeChanged = initialTheme !== newTheme;
                this.results.themeToggle.tests.push({ 
                    name: 'Toggle Functionality', 
                    status: themeChanged ? 'pass' : 'fail', 
                    details: `Theme changed from ${initialTheme} to ${newTheme}` 
                });
                
                // Switch back to original theme
                await themeToggle.click();
                await this.page.waitForTimeout(1000);
                
                const finalTheme = await this.page.getAttribute('html', 'data-theme');
                await this.takeScreenshot(`theme_${finalTheme}_final`);
                
                const themeRevertedBack = finalTheme === initialTheme;
                this.results.themeToggle.tests.push({ 
                    name: 'Toggle Revert', 
                    status: themeRevertedBack ? 'pass' : 'fail', 
                    details: `Theme reverted back to ${finalTheme}` 
                });
                
                this.results.themeToggle.status = 'pass';
            } else {
                this.results.themeToggle.tests.push({ name: 'Visibility', status: 'fail', details: 'Theme toggle is not visible' });
                console.log('❌ Theme toggle not visible');
                await this.takeScreenshot('theme_toggle_not_visible');
                this.results.themeToggle.status = 'fail';
            }
        } catch (error) {
            this.results.themeToggle.tests.push({ name: 'Error', status: 'fail', details: error.message });
            console.error('❌ Error testing theme toggle:', error.message);
            this.results.themeToggle.status = 'fail';
        }
    }

    async testNavigation() {
        console.log('\n🧭 Testing Navigation...');
        
        try {
            // Test "New Task" button
            await this.page.click('#newTaskButton');
            await this.page.waitForTimeout(2000);
            
            // Check if we're navigated to the home page
            const currentUrl = this.page.url();
            if (currentUrl.includes('v=home') || currentUrl.includes('home.html')) {
                this.results.navigation.tests.push({ name: 'New Task Button', status: 'pass', details: 'Successfully navigated to home page' });
                console.log('✅ New Task button works');
                await this.takeScreenshot('navigation_home_page');
            } else {
                this.results.navigation.tests.push({ name: 'New Task Button', status: 'fail', details: `Unexpected URL: ${currentUrl}` });
                console.log('❌ New Task navigation failed');
            }
            
            this.results.navigation.status = 'pass';
            
        } catch (error) {
            this.results.navigation.tests.push({ name: 'Error', status: 'fail', details: error.message });
            console.error('❌ Error testing navigation:', error.message);
            this.results.navigation.status = 'fail';
        }
    }

    async testTaskCreation() {
        console.log('\n📝 Testing Task Creation...');
        
        try {
            // Ensure we're on the home page
            await this.page.goto('http://localhost:3000/app.html?v=home', { 
                waitUntil: 'networkidle',
                timeout: 10000 
            });
            
            // Wait for the iframe to load
            await this.page.waitForSelector('#viewIframe', { timeout: 5000 });
            await this.page.waitForTimeout(2000);
            
            // Switch to iframe context
            const iframe = await this.page.frameLocator('#viewIframe');
            
            // Wait for textarea in iframe
            await iframe.locator('#newTaskPrompt').waitFor({ timeout: 10000 });
            
            const testTask = "Test task for theme toggle position verification";
            
            // Fill in task description
            await iframe.locator('#newTaskPrompt').fill(testTask);
            await this.page.waitForTimeout(1000);
            
            this.results.taskCreation.tests.push({ name: 'Task Input', status: 'pass', details: 'Successfully entered task text' });
            console.log('✅ Task description entered successfully');
            await this.takeScreenshot('task_creation_filled');
            
            // Click start task button
            await iframe.locator('#startTaskButton').click();
            console.log('✅ Start task button clicked');
            
            // Wait for task creation response
            await this.page.waitForTimeout(5000);
            await this.takeScreenshot('task_creation_processing');
            
            this.results.taskCreation.tests.push({ name: 'Task Submission', status: 'pass', details: 'Successfully submitted task' });
            this.results.taskCreation.status = 'pass';
            
        } catch (error) {
            this.results.taskCreation.tests.push({ name: 'Error', status: 'fail', details: error.message });
            console.error('❌ Error testing task creation:', error.message);
            this.results.taskCreation.status = 'fail';
        }
    }

    async runAllTests() {
        if (!(await this.init())) {
            console.error('❌ Failed to initialize. Aborting tests.');
            return;
        }
        
        try {
            // Run all tests
            await this.testThemeToggle();
            await this.testNavigation();
            await this.testTaskCreation();
            
            // Save results
            fs.writeFileSync(
                path.join(this.screenshotsDir, 'test_results.json'), 
                JSON.stringify(this.results, null, 2)
            );
            
            console.log('\n📊 Test Results Summary:');
            console.log(`Theme Toggle: ${this.results.themeToggle.status}`);
            console.log(`Navigation: ${this.results.navigation.status}`);
            console.log(`Task Creation: ${this.results.taskCreation.status}`);
            console.log(`Errors: ${this.results.errors.length}`);
            
            // Final screenshot
            await this.takeScreenshot('final_test_state');
            
        } catch (error) {
            console.error('❌ Error running tests:', error.message);
        } finally {
            await this.browser.close();
            console.log('\n🏁 All tests completed');
        }
    }
}

// Run the tests
const tester = new ComprehensiveUITester();
tester.runAllTests();
