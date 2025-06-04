// Thought into existence by Darbot
// Network debug script to identify API issues

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Create log directory if it doesn't exist
const logsDir = path.join(__dirname, 'logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Log file paths
const networkLogPath = path.join(logsDir, `network_debug_${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
const consoleLogPath = path.join(logsDir, `console_debug_${new Date().toISOString().replace(/[:.]/g, '-')}.json`);

(async () => {
  console.log('Starting network debug...');
  
  // Launch browser
  const browser = await chromium.launch({
    headless: false,
    slowMo: 50
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Store all network requests
  const networkRequests = [];
  
  // Listen to all network events
  page.on('request', request => {
    networkRequests.push({
      timestamp: new Date().toISOString(),
      url: request.url(),
      method: request.method(),
      headers: request.headers(),
      resourceType: request.resourceType(),
      isNavigationRequest: request.isNavigationRequest(),
      postData: request.postData() // This will capture the POST data
    });
  });
  
  // Listen for responses
  page.on('response', response => {
    const request = response.request();
    networkRequests.push({
      timestamp: new Date().toISOString(),
      type: 'response',
      url: request.url(),
      status: response.status(),
      statusText: response.statusText(),
      headers: response.headers()
    });
  });
  
  // Store console logs
  const consoleLogs = [];
  
  // Listen to console logs
  page.on('console', msg => {
    consoleLogs.push({
      timestamp: new Date().toISOString(),
      type: msg.type(),
      text: msg.text()
    });
    console.log(`PAGE CONSOLE: ${msg.type()}: ${msg.text()}`);
  });
  
  try {
    // Navigate to the application
    console.log('Navigating to the application...');
    await page.goto('http://localhost:3000');
    
    // Wait for page to load completely
    await page.waitForLoadState('networkidle');
    
    console.log('Page loaded. Waiting a bit to collect initial network activity...');
    await page.waitForTimeout(3000);
    
    // Find and check the apiEndpoint value
    const apiEndpoint = await page.evaluate(() => {
      return window.getStoredData ? window.getStoredData('apiEndpoint') : null;
    });
    
    console.log('API Endpoint from localStorage:', apiEndpoint);
    
    // Try to locate task input field and submit button
    const hasTaskInput = await page.evaluate(() => {
      const inputs = Array.from(document.querySelectorAll('textarea, input'));
      return inputs.map(input => ({
        type: input.tagName,
        id: input.id,
        placeholder: input.placeholder,
        visible: input.offsetParent !== null
      }));
    });
    
    console.log('Input fields found:', hasTaskInput);
    
    // Look for any error messages on the page
    const errorMessages = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('*'))
        .filter(el => el.textContent.toLowerCase().includes('error'))
        .map(el => ({
          tagName: el.tagName,
          className: el.className,
          text: el.textContent.trim()
        }));
    });
    
    console.log('Error messages found on page:', errorMessages);
    
    // Wait for more data
    await page.waitForTimeout(5000);
    
    // Save the collected data to files
    fs.writeFileSync(networkLogPath, JSON.stringify(networkRequests, null, 2));
    fs.writeFileSync(consoleLogPath, JSON.stringify(consoleLogs, null, 2));
    
    console.log(`Network requests saved to ${networkLogPath}`);
    console.log(`Console logs saved to ${consoleLogPath}`);
    
  } catch (error) {
    console.error('Error during network debug:', error);
  } finally {
    await browser.close();
  }
})();
