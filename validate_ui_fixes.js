// Thought into existence by Darbot
// Validate UI fixes using Playwright

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Create screenshots directory if it doesn't exist
const screenshotsDir = path.join(__dirname, 'screenshots', 'validation');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// Get current timestamp for unique screenshot names
const getTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-');
};

(async () => {
  console.log('Starting UI validation test...');
  
  // Launch browser
  const browser = await chromium.launch({
    headless: false, // Run in non-headless mode to see what's happening
    slowMo: 100 // Slow down actions to see what's happening
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Step 1: Go to the application
    console.log('Navigating to the application...');
    await page.goto('http://localhost:3000');
    
    // Take a screenshot of the initial state
    await page.screenshot({ 
      path: path.join(screenshotsDir, `initial_state_${getTimestamp()}.png`),
      fullPage: true
    });
    
    // Step 2: Check for error messages
    console.log('Checking for error messages...');
    const errorElements = await page.$$('text="error loading tasks"');
    if (errorElements.length > 0) {
      console.error('❌ Found "error loading tasks" message on the page');
      await page.screenshot({ 
        path: path.join(screenshotsDir, `error_tasks_${getTimestamp()}.png`),
        fullPage: true
      });
    } else {
      console.log('✅ No "error loading tasks" message found');
    }
    
    // Step 3: Try to submit a quick task
    console.log('Attempting to submit a quick task...');
    
    // Wait for the page to fully load
    await page.waitForTimeout(2000);
    
    // Wait for any task prompt field to be available
    const taskPromptField = await page.waitForSelector('textarea[placeholder*="task"]', { timeout: 5000 });
    
    // Enter task description
    await taskPromptField.fill('Test task submission validation');
    
    // Take a screenshot before clicking submit
    await page.screenshot({ 
      path: path.join(screenshotsDir, `before_submit_${getTimestamp()}.png`),
      fullPage: true
    });
    
    // Click submit button
    const submitButton = await page.locator('button:has-text("Start")').first();
    await submitButton.click();
    
    // Wait for response (looking for loading indicator or result)
    await page.waitForTimeout(5000);
    
    // Take a screenshot after submission
    await page.screenshot({ 
      path: path.join(screenshotsDir, `after_submit_${getTimestamp()}.png`),
      fullPage: true
    });
    
    // Check for successful submission or error
    const errorAfterSubmit = await page.$$('text=/error|failed/i');
    if (errorAfterSubmit.length > 0) {
      console.error('❌ Task submission failed with error');
    } else {
      // Check if we got redirected to task details page
      const currentUrl = page.url();
      if (currentUrl.includes('task') || currentUrl.includes('plan')) {
        console.log('✅ Task submitted successfully! Redirected to task details page.');
      } else {
        console.log('⚠️ Task submission status unclear. Please check the screenshots.');
      }
    }
    
    // Open browser console to check for network errors
    console.log('Checking browser console logs...');
    const consoleLogs = [];
    page.on('console', msg => {
      consoleLogs.push({
        type: msg.type(),
        text: msg.text()
      });
    });
    
    // Wait to collect some console logs
    await page.waitForTimeout(2000);
    
    // Check for network errors in console logs
    const networkErrors = consoleLogs.filter(log => 
      log.type === 'error' && (log.text.includes('fetch') || log.text.includes('404') || log.text.includes('api'))
    );
    
    if (networkErrors.length > 0) {
      console.error('❌ Found network errors in console:', networkErrors);
    } else {
      console.log('✅ No network errors found in console');
    }
    
    // Print all console errors for debugging
    const errors = consoleLogs.filter(log => log.type === 'error');
    if (errors.length > 0) {
      console.error('Console errors:', errors);
    }
    
    console.log('Test completed. Check the screenshots in the screenshots/validation directory.');
    
  } catch (error) {
    console.error('Test failed with error:', error);
    // Take screenshot on error
    await page.screenshot({ 
      path: path.join(screenshotsDir, `error_${getTimestamp()}.png`),
      fullPage: true
    });
  } finally {
    // Close browser
    await browser.close();
  }
})();
