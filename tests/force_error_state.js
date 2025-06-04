// Thought into existence by Darbot
// Force Task List Error State - Create conditions to see the error message

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const screenshotsDir = path.join(__dirname, 'screenshots', 'forced_error');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

const getTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-');
};

(async () => {
  console.log('🚀 Forcing Task List Error State...');
  
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: null
  });
  
  const page = await context.newPage();
  
  // Monitor all console messages and requests
  const allErrors = [];
  page.on('console', msg => {
    console.log(`📝 Console [${msg.type()}]: ${msg.text()}`);
    if (msg.type() === 'error') {
      allErrors.push({ type: 'console', message: msg.text() });
    }
  });
  
  page.on('requestfailed', request => {
    console.log(`❌ Request failed: ${request.url()} - ${request.failure()?.errorText}`);
    allErrors.push({ type: 'request', url: request.url(), error: request.failure()?.errorText });
  });
  
  page.on('response', response => {
    if (!response.ok()) {
      console.log(`🚨 HTTP Error: ${response.status()} ${response.statusText()} - ${response.url()}`);
      allErrors.push({ type: 'http', status: response.status(), url: response.url() });
    }
  });
  
  try {
    console.log('🌐 Navigating to application...');
    await page.goto('http://localhost:3000', { 
      waitUntil: 'networkidle',
      timeout: 10000 
    });
    
    // Take initial screenshot
    await page.screenshot({ 
      path: path.join(screenshotsDir, `initial_state_${getTimestamp()}.png`),
      fullPage: true
    });
    
    // Wait for initial load
    await page.waitForTimeout(3000);
    
    console.log('🔍 Checking initial task list state...');
    let taskListState = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { type: 'no_element', content: 'not found' };
      return { 
        type: 'found', 
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim()
      };
    });
    
    console.log(`📊 Initial state: ${taskListState.textContent}`);
    
    // Now let's block the API and force a reload to create an error state
    console.log('🚫 Blocking API requests and forcing refresh...');
    
    await page.route('/api/**', route => {
      console.log(`🛑 Blocking API request: ${route.request().url()}`);
      route.abort();
    });
    
    // Force reload the page
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `blocked_api_state_${getTimestamp()}.png`),
      fullPage: true
    });
    
    taskListState = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { type: 'no_element', content: 'not found' };
      return { 
        type: 'found', 
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim()
      };
    });
    
    console.log(`📊 After blocking API: ${taskListState.textContent}`);
    
    // Let's also try stopping the backend server and testing
    console.log('⚠️ The backend may be down, let\'s test with 500 errors...');
    
    // Clear the route block and create 500 errors instead
    await page.unroute('/api/**');
    
    await page.route('/api/plans', route => {
      console.log('🔥 Simulating 500 error for /api/plans');
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Reload to trigger the 500 error
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `500_error_state_${getTimestamp()}.png`),
      fullPage: true
    });
    
    taskListState = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { type: 'no_element', content: 'not found' };
      return { 
        type: 'found', 
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim()
      };
    });
    
    console.log(`📊 After 500 error: ${taskListState.textContent}`);
    
    // Check if we can manually trigger the error by calling fetchTasksIfNeeded
    console.log('🔧 Manually triggering task fetch...');
    
    const manualFetchResult = await page.evaluate(async () => {
      try {
        // Manually call the fetch function
        if (window.fetchTasksIfNeeded) {
          await window.fetchTasksIfNeeded();
          await new Promise(resolve => setTimeout(resolve, 2000));
          
          const myTasksMenu = document.getElementById('myTasksMenu');
          return {
            success: true,
            content: myTasksMenu ? myTasksMenu.textContent.trim() : 'no menu found'
          };
        } else {
          return { success: false, error: 'fetchTasksIfNeeded not found' };
        }
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    console.log(`🔧 Manual fetch result:`, manualFetchResult);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `manual_fetch_result_${getTimestamp()}.png`),
      fullPage: true
    });
    
    // Save all the errors we captured
    fs.writeFileSync(
      path.join(screenshotsDir, 'error_analysis.json'), 
      JSON.stringify({
        errors: allErrors,
        finalState: taskListState,
        manualFetchResult
      }, null, 2)
    );
    
    console.log('📋 Error analysis complete');
    console.log(`📁 All screenshots saved to: ${screenshotsDir}`);
    console.log(`🚨 Total errors captured: ${allErrors.length}`);
    
  } catch (error) {
    console.error('❌ Error during test:', error.message);
  } finally {
    await browser.close();
  }
})();
