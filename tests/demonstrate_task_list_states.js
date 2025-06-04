// Thought into existence by Darbot
// Demonstrate the difference between "No tasks found" and "Error loading tasks" states

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const screenshotsDir = path.join(__dirname, 'screenshots', 'state_demonstration');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

const getTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-');
};

(async () => {
  console.log('🎭 Demonstrating Task List State Differences...\n');
  
  const browser = await chromium.launch({
    headless: false,
    args: ['--start-maximized']
  });

  const context = await browser.newContext({
    viewport: null
  });
  
  const page = await context.newPage();
  
  // Monitor console messages
  page.on('console', msg => {
    console.log(`📝 Console [${msg.type()}]: ${msg.text()}`);
  });

  try {
    // SCENARIO 1: Normal operation - "No tasks found" (API works, returns empty array)
    console.log('📋 SCENARIO 1: Backend healthy, no tasks exist');
    console.log('Expected: Blue "No tasks found. Create your first task!" message\n');
    
    await page.goto('http://localhost:3000', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `scenario1_no_tasks_${getTimestamp()}.png`),
      fullPage: true
    });
    
    const scenario1State = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { found: false };
      return { 
        found: true,
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim(),
        hasError: myTasksMenu.innerHTML.includes('notification is-danger'),
        hasInfo: myTasksMenu.innerHTML.includes('notification is-info')
      };
    });
    
    console.log(`✅ Scenario 1 Result: "${scenario1State.textContent}"`);
    console.log(`   Has error styling: ${scenario1State.hasError}`);
    console.log(`   Has info styling: ${scenario1State.hasInfo}\n`);

    // SCENARIO 2: API failure - "Error loading tasks" (500 error)
    console.log('🚨 SCENARIO 2: Simulating backend failure');
    console.log('Expected: Red "Error loading tasks" message\n');
    
    // Block the API to force an error
    await page.route('/api/plans', route => {
      console.log('🛑 Blocking API request to simulate backend failure');
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    // Reload to trigger the error
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `scenario2_error_loading_${getTimestamp()}.png`),
      fullPage: true
    });
    
    const scenario2State = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { found: false };
      return { 
        found: true,
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim(),
        hasError: myTasksMenu.innerHTML.includes('notification is-danger'),
        hasInfo: myTasksMenu.innerHTML.includes('notification is-info')
      };
    });
    
    console.log(`✅ Scenario 2 Result: "${scenario2State.textContent}"`);
    console.log(`   Has error styling: ${scenario2State.hasError}`);
    console.log(`   Has info styling: ${scenario2State.hasInfo}\n`);

    // SCENARIO 3: Network timeout - Force fetch to fail
    console.log('⏰ SCENARIO 3: Simulating network timeout');
    console.log('Expected: Red "Error loading tasks" message\n');
    
    // Clear previous route and add timeout
    await page.unroute('/api/plans');
    await page.route('/api/plans', route => {
      console.log('⏰ Timing out API request');
      // Just hang the request, don't respond
      // This will cause a timeout and error
    });
    
    // Manually trigger the fetch function
    await page.evaluate(() => {
      if (window.fetchTasksIfNeeded) {
        window.fetchTasksIfNeeded();
      }
    });
    
    await page.waitForTimeout(5000);
    
    await page.screenshot({ 
      path: path.join(screenshotsDir, `scenario3_timeout_${getTimestamp()}.png`),
      fullPage: true
    });
    
    const scenario3State = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (!myTasksMenu) return { found: false };
      return { 
        found: true,
        innerHTML: myTasksMenu.innerHTML,
        textContent: myTasksMenu.textContent.trim(),
        hasError: myTasksMenu.innerHTML.includes('notification is-danger'),
        hasInfo: myTasksMenu.innerHTML.includes('notification is-info')
      };
    });
    
    console.log(`✅ Scenario 3 Result: "${scenario3State.textContent}"`);
    console.log(`   Has error styling: ${scenario3State.hasError}`);
    console.log(`   Has info styling: ${scenario3State.hasInfo}\n`);

    // Summary
    console.log('📊 SUMMARY OF DIFFERENCES:');
    console.log('========================================');
    console.log('Scenario 1 (Backend healthy, no tasks):');
    console.log(`  Message: "${scenario1State.textContent}"`);
    console.log(`  Styling: ${scenario1State.hasInfo ? 'Blue info' : 'Other'}`);
    console.log('');
    console.log('Scenario 2 (Backend 500 error):');
    console.log(`  Message: "${scenario2State.textContent}"`);
    console.log(`  Styling: ${scenario2State.hasError ? 'Red danger' : 'Other'}`);
    console.log('');
    console.log('Scenario 3 (Network timeout):');
    console.log(`  Message: "${scenario3State.textContent}"`);
    console.log(`  Styling: ${scenario3State.hasError ? 'Red danger' : 'Other'}`);
    console.log('');
    console.log('🎯 EXPLANATION:');
    console.log('- "No tasks found" = API succeeds but returns empty array []');
    console.log('- "Error loading tasks" = API call fails (network error, 500, timeout)');
    console.log('');
    console.log('Your two test scripts see different states because:');
    console.log('1. comprehensive_ui_test.js runs when backend is healthy (empty array)');
    console.log('2. validate_ui_fixes.js runs when backend has issues (API error)');
    
  } catch (error) {
    console.error('❌ Error during demonstration:', error);
  } finally {
    await browser.close();
    console.log('\n🏁 Demonstration complete. Check screenshots in:', screenshotsDir);
  }
})();