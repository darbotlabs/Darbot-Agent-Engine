// Thought into existence by Darbot
// Compare Task List States - Compare the different UI states between test scripts

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const screenshotsDir = path.join(__dirname, 'screenshots', 'comparison');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

const getTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-');
};

class TaskListStateComparator {
  constructor() {
    this.browser = null;
    this.context = null;
    this.results = {
      scenario1: { name: 'Fresh Load', state: null, screenshot: null },
      scenario2: { name: 'After Wait', state: null, screenshot: null },
      scenario3: { name: 'Backend Down', state: null, screenshot: null },
      analysis: null
    };
  }

  async init() {
    console.log('🚀 Initializing Task List State Comparator...');
    
    this.browser = await chromium.launch({
      headless: false,
      args: ['--start-maximized']
    });

    this.context = await this.browser.newContext({
      viewport: null
    });
    
    return true;
  }

  async captureTaskListState(page, scenario) {
    // Wait for page to load completely
    await page.waitForTimeout(3000);
    
    const taskListState = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) {
        return { type: 'no_element', content: 'myTasksMenu element not found' };
      }
      
      const content = myTasksMenu.innerHTML;
      const textContent = myTasksMenu.textContent.trim();
      
      // Check for different states
      if (content.includes('Error loading tasks')) {
        return { type: 'error', content: textContent, html: content };
      } else if (content.includes('No tasks found')) {
        return { type: 'no_tasks', content: textContent, html: content };
      } else if (content.includes('Loading tasks')) {
        return { type: 'loading', content: textContent, html: content };
      } else if (content.includes('menu-task')) {
        const taskCount = document.querySelectorAll('.menu-task').length;
        return { type: 'tasks_found', content: textContent, html: content, taskCount };
      } else {
        return { type: 'unknown', content: textContent, html: content };
      }
    });
    
    const screenshot = `${scenario}_${getTimestamp()}.png`;
    await page.screenshot({ 
      path: path.join(screenshotsDir, screenshot),
      fullPage: true
    });
    
    return { state: taskListState, screenshot };
  }

  async scenario1_FreshLoad() {
    console.log('\n📱 Scenario 1: Fresh App Load (like validate_ui_fixes.js)');
    
    const page = await this.context.newPage();
    
    // Monitor console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    page.on('requestfailed', request => {
      errors.push(`Request failed: ${request.url()}`);
    });
    
    try {
      // Navigate directly to main page (like validate_ui_fixes.js does)
      await page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle',
        timeout: 10000 
      });
      
      const result = await this.captureTaskListState(page, 'scenario1_fresh_load');
      this.results.scenario1 = { 
        ...this.results.scenario1, 
        ...result, 
        errors: errors.slice() 
      };
      
      console.log(`📊 Scenario 1 Result: ${this.results.scenario1.state.type}`);
      console.log(`📄 Content: ${this.results.scenario1.state.content}`);
      
    } catch (error) {
      console.error('❌ Scenario 1 failed:', error.message);
      this.results.scenario1.error = error.message;
    }
    
    await page.close();
  }

  async scenario2_AfterWait() {
    console.log('\n⏳ Scenario 2: After Extended Wait (simulating different timing)');
    
    const page = await this.context.newPage();
    
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    try {
      await page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle',
        timeout: 10000 
      });
      
      // Wait longer to see if state changes
      await page.waitForTimeout(8000);
      
      const result = await this.captureTaskListState(page, 'scenario2_after_wait');
      this.results.scenario2 = { 
        ...this.results.scenario2, 
        ...result, 
        errors: errors.slice() 
      };
      
      console.log(`📊 Scenario 2 Result: ${this.results.scenario2.state.type}`);
      console.log(`📄 Content: ${this.results.scenario2.state.content}`);
      
    } catch (error) {
      console.error('❌ Scenario 2 failed:', error.message);
      this.results.scenario2.error = error.message;
    }
    
    await page.close();
  }

  async scenario3_BackendDown() {
    console.log('\n🔌 Scenario 3: Simulating Backend Issues');
    
    const page = await this.context.newPage();
    
    // Block backend requests to simulate server issues
    await page.route('/api/**', route => {
      route.abort();
    });
    
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    
    try {
      await page.goto('http://localhost:3000', { 
        waitUntil: 'networkidle',
        timeout: 10000 
      });
      
      // Wait for error to manifest
      await page.waitForTimeout(5000);
      
      const result = await this.captureTaskListState(page, 'scenario3_backend_down');
      this.results.scenario3 = { 
        ...this.results.scenario3, 
        ...result, 
        errors: errors.slice() 
      };
      
      console.log(`📊 Scenario 3 Result: ${this.results.scenario3.state.type}`);
      console.log(`📄 Content: ${this.results.scenario3.state.content}`);
      
    } catch (error) {
      console.error('❌ Scenario 3 failed:', error.message);
      this.results.scenario3.error = error.message;
    }
    
    await page.close();
  }

  analyzeResults() {
    console.log('\n🔍 Analysis of Task List States:');
    console.log('=====================================');
    
    const scenarios = [this.results.scenario1, this.results.scenario2, this.results.scenario3];
    
    scenarios.forEach((scenario, index) => {
      console.log(`\n${scenario.name}:`);
      console.log(`  State: ${scenario.state?.type || 'N/A'}`);
      console.log(`  Content: ${scenario.state?.content || 'N/A'}`);
      console.log(`  Errors: ${scenario.errors?.length || 0}`);
      if (scenario.errors?.length > 0) {
        scenario.errors.forEach(err => console.log(`    - ${err}`));
      }
    });
    
    // Determine what causes different states
    const states = scenarios.map(s => s.state?.type).filter(Boolean);
    const uniqueStates = [...new Set(states)];
    
    if (uniqueStates.length > 1) {
      console.log('\n🎯 DIFFERENT STATES DETECTED:');
      console.log(`Found ${uniqueStates.length} different states: ${uniqueStates.join(', ')}`);
      
      this.results.analysis = {
        conclusion: 'Different timing and backend availability causes different UI states',
        states: uniqueStates,
        recommendation: 'Task list shows different messages based on backend connectivity and timing'
      };
    } else {
      console.log('\n✅ All scenarios show the same state');
      this.results.analysis = {
        conclusion: 'Consistent state across all scenarios',
        states: uniqueStates,
        recommendation: 'No timing-based differences detected'
      };
    }
  }

  async runComparison() {
    if (!(await this.init())) {
      console.error('❌ Failed to initialize. Aborting comparison.');
      return;
    }
    
    try {
      await this.scenario1_FreshLoad();
      await this.scenario2_AfterWait();
      await this.scenario3_BackendDown();
      
      this.analyzeResults();
      
      // Save results
      fs.writeFileSync(
        path.join(screenshotsDir, 'comparison_results.json'), 
        JSON.stringify(this.results, null, 2)
      );
      
      console.log('\n📋 Comparison complete. Results saved to comparison_results.json');
      console.log(`📸 Screenshots saved to: ${screenshotsDir}`);
      
    } catch (error) {
      console.error('❌ Error during comparison:', error.message);
    } finally {
      await this.browser.close();
    }
  }
}

// Run the comparison
const comparator = new TaskListStateComparator();
comparator.runComparison();
