// Thought into existence by Darbot
// Comprehensive UI Audit with Playwright using Microsoft Edge
// This script performs a full functionality audit of the Darbot Agent Engine

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

class DarbotUIAuditor {
    constructor() {
        this.browser = null;
        this.context = null;
        this.page = null;
        this.screenshotsDir = './screenshots';
        this.results = {
            backend: { status: 'unknown', tests: [] },
            frontend: { status: 'unknown', tests: [] },
            authentication: { status: 'unknown', tests: [] },
            taskCreation: { status: 'unknown', tests: [] },
            navigation: { status: 'unknown', tests: [] },
            errors: []
        };
    }    async init() {
        console.log('🚀 Initializing Darbot UI Auditor with Chromium...');
        
        // Create screenshots directory
        if (!fs.existsSync(this.screenshotsDir)) {
            fs.mkdirSync(this.screenshotsDir, { recursive: true });
        }

        try {
            this.browser = await chromium.launch({
                headless: false,
                args: [
                    '--start-maximized',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-blink-features=AutomationControlled'
                ]
            });

            this.context = await this.browser.newContext({
                viewport: null, // Use full screen
                userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59'
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

    async testBackendConnectivity() {
        console.log('\n🔍 Testing Backend Connectivity...');
        
        try {
            // Test FastAPI docs
            await this.page.goto('http://localhost:8001/docs', { 
                waitUntil: 'load',
                timeout: 10000 
            });
            
            const title = await this.page.title();
            if (title.includes('FastAPI') || title.includes('API')) {
                this.results.backend.tests.push({ name: 'FastAPI Docs', status: 'pass', details: `Title: ${title}` });
                console.log('✅ Backend API documentation accessible');
                await this.takeScreenshot('backend_api_docs');
            } else {
                this.results.backend.tests.push({ name: 'FastAPI Docs', status: 'fail', details: 'Unexpected page content' });
                console.log('❌ Backend API docs page unexpected');
            }

            // Test API endpoints directly
            const response = await this.page.evaluate(async () => {
                try {
                    const res = await fetch('http://localhost:8001/openapi.json');
                    return { status: res.status, ok: res.ok };
                } catch (error) {
                    return { error: error.message };
                }
            });

            if (response.ok) {
                this.results.backend.tests.push({ name: 'OpenAPI Endpoint', status: 'pass', details: `Status: ${response.status}` });
                console.log('✅ OpenAPI endpoint responding');
            } else {
                this.results.backend.tests.push({ name: 'OpenAPI Endpoint', status: 'fail', details: response.error || 'HTTP error' });
                console.log('❌ OpenAPI endpoint failed');
            }

            this.results.backend.status = 'pass';
            
        } catch (error) {
            this.results.backend.status = 'fail';
            this.results.backend.tests.push({ name: 'Backend Connection', status: 'fail', details: error.message });
            console.log('❌ Backend connectivity test failed:', error.message);
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
            await this.page.waitForSelector('#app', { timeout: 5000 });
            await this.page.waitForSelector('.menu-logo', { timeout: 5000 });
            
            this.results.frontend.tests.push({ name: 'Page Load', status: 'pass', details: `Title: ${title}` });
            console.log('✅ Frontend loaded successfully');
            
            // Check for main UI elements
            const elements = {
                'App Container': '#app',
                'Menu Logo': '.menu-logo',
                'New Task Button': '#newTaskButton',
                'View Iframe': '#viewIframe'
            };
            
            for (const [name, selector] of Object.entries(elements)) {
                try {
                    await this.page.waitForSelector(selector, { timeout: 3000 });
                    this.results.frontend.tests.push({ name: `Element: ${name}`, status: 'pass', details: `Selector: ${selector}` });
                    console.log(`✅ Found: ${name}`);
                } catch (error) {
                    this.results.frontend.tests.push({ name: `Element: ${name}`, status: 'fail', details: `Missing selector: ${selector}` });
                    console.log(`❌ Missing: ${name}`);
                }
            }
            
            await this.takeScreenshot('frontend_main_page');
            this.results.frontend.status = 'pass';
            
        } catch (error) {
            this.results.frontend.status = 'fail';
            this.results.frontend.tests.push({ name: 'Frontend Load', status: 'fail', details: error.message });
            console.log('❌ Frontend loading failed:', error.message);
            await this.takeScreenshot('frontend_error');
        }
    }

    async testNavigation() {
        console.log('\n🧭 Testing Navigation...');
        
        try {
            // Test "New Task" button
            await this.page.click('#newTaskButton');
            await this.page.waitForTimeout(2000);
            
            // Check if we're on the home page
            const currentUrl = this.page.url();
            if (currentUrl.includes('v=home')) {
                this.results.navigation.tests.push({ name: 'New Task Navigation', status: 'pass', details: 'Successfully navigated to home' });
                console.log('✅ New Task button works');
                await this.takeScreenshot('navigation_home_page');
            } else {
                this.results.navigation.tests.push({ name: 'New Task Navigation', status: 'fail', details: `Unexpected URL: ${currentUrl}` });
                console.log('❌ New Task navigation failed');
            }
            
            // Test theme toggle
            try {
                await this.page.click('#themeToggle');
                await this.page.waitForTimeout(1000);
                
                const theme = await this.page.getAttribute('html', 'data-theme');
                this.results.navigation.tests.push({ name: 'Theme Toggle', status: 'pass', details: `Theme: ${theme}` });
                console.log(`✅ Theme toggle works - Current theme: ${theme}`);
                await this.takeScreenshot(`theme_${theme}`);
            } catch (error) {
                this.results.navigation.tests.push({ name: 'Theme Toggle', status: 'fail', details: error.message });
                console.log('❌ Theme toggle failed');
            }
            
            this.results.navigation.status = 'pass';
            
        } catch (error) {
            this.results.navigation.status = 'fail';
            this.results.navigation.tests.push({ name: 'Navigation Test', status: 'fail', details: error.message });
            console.log('❌ Navigation test failed:', error.message);
        }
    }

    async testTaskCreation() {
        console.log('\n📝 Testing Task Creation...');
        
        try {
            // Ensure we're on the home page
            await this.page.goto('http://localhost:3000?v=home', { 
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
            
            const testTask = "Draft a press release about our products and services for immediate distribution.";
            
            // Fill in task description
            await iframe.locator('#newTaskPrompt').fill(testTask);
            await this.page.waitForTimeout(1000);
            
            console.log('✅ Task description entered successfully');
            await this.takeScreenshot('task_creation_filled');
              // Click start task button - check for multiple possible selectors
            try {
                await iframe.locator('#startTaskButton').click();
            } catch (e) {
                // Try alternative selector (.send-button is used in some versions)
                await iframe.locator('.send-button').click();
            }
            console.log('✅ Start task button clicked');
            
            // Wait for task creation response
            await this.page.waitForTimeout(5000);
            await this.takeScreenshot('task_creation_processing');
            
            // Check for success indicators
            const pageContent = await this.page.content();
            if (pageContent.includes('Task created successfully') || pageContent.includes('AI agents are on it')) {
                this.results.taskCreation.tests.push({ name: 'Task Creation', status: 'pass', details: 'Task created successfully' });
                console.log('✅ Task creation successful');
            } else {
                this.results.taskCreation.tests.push({ name: 'Task Creation', status: 'partial', details: 'Task submitted but success unclear' });
                console.log('⚠️ Task creation status unclear');
            }
            
            // Test quick task functionality
            try {
                await iframe.locator('.quick-task').first().click();
                await this.page.waitForTimeout(1000);
                
                const taskValue = await iframe.locator('#newTaskPrompt').inputValue();
                if (taskValue.length > 0) {
                    this.results.taskCreation.tests.push({ name: 'Quick Task', status: 'pass', details: 'Quick task populates textarea' });
                    console.log('✅ Quick task functionality works');
                } else {
                    this.results.taskCreation.tests.push({ name: 'Quick Task', status: 'fail', details: 'Quick task did not populate textarea' });
                    console.log('❌ Quick task functionality failed');
                }
            } catch (error) {
                this.results.taskCreation.tests.push({ name: 'Quick Task', status: 'fail', details: error.message });
                console.log('❌ Quick task test failed:', error.message);
            }
            
            this.results.taskCreation.status = 'pass';
            
        } catch (error) {
            this.results.taskCreation.status = 'fail';
            this.results.taskCreation.tests.push({ name: 'Task Creation Test', status: 'fail', details: error.message });
            console.log('❌ Task creation test failed:', error.message);
            await this.takeScreenshot('task_creation_error');
        }
    }

    async testTaskManagement() {
        console.log('\n📋 Testing Task Management...');
        
        try {
            // Go back to main app view
            await this.page.goto('http://localhost:3000', { 
                waitUntil: 'networkidle',
                timeout: 10000 
            });
            
            // Wait for tasks to load
            await this.page.waitForTimeout(3000);
            
            // Check if tasks are listed in the sidebar
            const taskElements = await this.page.locator('#myTasksMenu .menu-task').count();
            
            if (taskElements > 0) {
                this.results.taskCreation.tests.push({ name: 'Task List', status: 'pass', details: `Found ${taskElements} tasks` });
                console.log(`✅ Found ${taskElements} tasks in sidebar`);
                
                // Click on the first task
                await this.page.locator('#myTasksMenu .menu-task').first().click();
                await this.page.waitForTimeout(2000);
                
                // Check if task details loaded
                const currentUrl = this.page.url();
                if (currentUrl.includes('v=task')) {
                    this.results.taskCreation.tests.push({ name: 'Task Details View', status: 'pass', details: 'Task details view loaded' });
                    console.log('✅ Task details view loaded');
                    await this.takeScreenshot('task_details_view');
                } else {
                    this.results.taskCreation.tests.push({ name: 'Task Details View', status: 'fail', details: 'Task details view not loaded' });
                    console.log('❌ Task details view failed to load');
                }
            } else {
                this.results.taskCreation.tests.push({ name: 'Task List', status: 'fail', details: 'No tasks found in sidebar' });
                console.log('❌ No tasks found in sidebar');
            }
            
        } catch (error) {
            this.results.taskCreation.tests.push({ name: 'Task Management Test', status: 'fail', details: error.message });
            console.log('❌ Task management test failed:', error.message);
        }
    }

    async runDiagnostics() {
        console.log('\n🔬 Running Frontend Diagnostics...');
        
        try {
            // Run the diagnostic script
            const diagnosticResults = await this.page.evaluate(() => {
                // Inject diagnostic functions if not available
                if (typeof getStoredData === 'undefined') {
                    window.getStoredData = (key) => localStorage.getItem(key);
                    window.setStoredData = (key, value) => localStorage.setItem(key, value);
                }
                
                const results = {};
                
                // Check API endpoint configuration
                try {
                    const apiEndpoint = getStoredData('apiEndpoint');
                    results.apiEndpoint = apiEndpoint ? 'configured' : 'missing';
                    results.apiEndpointValue = apiEndpoint;
                } catch (error) {
                    results.apiEndpoint = 'error';
                    results.apiEndpointError = error.message;
                }
                
                // Check localStorage functionality
                try {
                    const testKey = 'diagnostic_test';
                    const testValue = 'test_value_' + Date.now();
                    localStorage.setItem(testKey, testValue);
                    const retrieved = localStorage.getItem(testKey);
                    results.localStorage = retrieved === testValue ? 'working' : 'failed';
                    localStorage.removeItem(testKey);
                } catch (error) {
                    results.localStorage = 'error';
                    results.localStorageError = error.message;
                }
                
                // Check iframe setup
                const iframe = document.getElementById('viewIframe');
                results.iframe = iframe ? 'found' : 'missing';
                results.iframeSrc = iframe?.src || 'none';
                
                return results;
            });
            
            console.log('🔍 Diagnostic Results:', diagnosticResults);
            this.results.frontend.tests.push({ name: 'Diagnostics', status: 'pass', details: JSON.stringify(diagnosticResults) });
            
        } catch (error) {
            console.log('❌ Diagnostics failed:', error.message);
            this.results.frontend.tests.push({ name: 'Diagnostics', status: 'fail', details: error.message });
        }
    }

    async generateReport() {
        console.log('\n📊 Generating Audit Report...');
        
        const report = {
            timestamp: new Date().toISOString(),
            summary: {
                backend: this.results.backend.status,
                frontend: this.results.frontend.status,
                navigation: this.results.navigation.status,
                taskCreation: this.results.taskCreation.status,
                totalErrors: this.results.errors.length
            },
            details: this.results,
            recommendations: []
        };
        
        // Generate recommendations
        if (this.results.backend.status === 'fail') {
            report.recommendations.push('Backend server is not running or accessible. Start the backend service and ensure it\'s listening on port 8001.');
        }
        
        if (this.results.frontend.status === 'fail') {
            report.recommendations.push('Frontend has loading issues. Check console errors and ensure all dependencies are properly loaded.');
        }
        
        if (this.results.errors.length > 0) {
            report.recommendations.push(`${this.results.errors.length} errors detected. Review console errors and fix JavaScript issues.`);
        }
        
        if (this.results.taskCreation.status === 'fail') {
            report.recommendations.push('Task creation is not working. Check backend API connectivity and authentication.');
        }
        
        // Save report
        const reportPath = './audit_report.json';
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log(`📋 Audit report saved to: ${reportPath}`);
        
        // Print summary
        console.log('\n🎯 AUDIT SUMMARY');
        console.log('================');
        console.log(`Backend Status: ${report.summary.backend.toUpperCase()}`);
        console.log(`Frontend Status: ${report.summary.frontend.toUpperCase()}`);
        console.log(`Navigation Status: ${report.summary.navigation.toUpperCase()}`);
        console.log(`Task Creation Status: ${report.summary.taskCreation.toUpperCase()}`);
        console.log(`Total Errors: ${report.summary.totalErrors}`);
        
        if (report.recommendations.length > 0) {
            console.log('\n💡 RECOMMENDATIONS:');
            report.recommendations.forEach((rec, index) => {
                console.log(`${index + 1}. ${rec}`);
            });
        }
    }

    async runFullAudit() {
        console.log('🏁 Starting Full UI Functionality Audit...');
        
        if (!await this.init()) {
            console.error('❌ Failed to initialize browser');
            return false;
        }
        
        try {
            await this.testBackendConnectivity();
            await this.testFrontendLoading();
            await this.testNavigation();
            await this.testTaskCreation();
            await this.testTaskManagement();
            await this.runDiagnostics();
            
            await this.generateReport();
            
            console.log('\n✅ Full audit completed!');
            console.log('📸 Screenshots saved in:', this.screenshotsDir);
            console.log('📋 Report saved as: audit_report.json');
            
            // Keep browser open for manual inspection
            console.log('\n🔍 Browser remains open for manual inspection...');
            console.log('Press Ctrl+C to close and exit');
            
            return true;
            
        } catch (error) {
            console.error('❌ Audit failed:', error.message);
            await this.takeScreenshot('audit_failure');
            return false;
        }
    }

    async cleanup() {
        if (this.browser) {
            await this.browser.close();
            console.log('🔒 Browser closed');
        }
    }
}

// Main execution
async function main() {
    const auditor = new DarbotUIAuditor();
    
    // Handle graceful shutdown
    process.on('SIGINT', async () => {
        console.log('\n👋 Shutting down auditor...');
        await auditor.cleanup();
        process.exit(0);
    });
    
    const success = await auditor.runFullAudit();
    
    if (success) {
        // Keep running for manual inspection
        console.log('\n⏳ Keeping browser open for manual inspection...');
        while (true) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    } else {
        await auditor.cleanup();
        process.exit(1);
    }
}

main().catch(console.error);
