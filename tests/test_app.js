// Thought into existence by Darbot
const { chromium, firefox, webkit, devices } = require('playwright');

async function runTest() {
  // Launch Microsoft Edge browser
  const browser = await chromium.launch({
    channel: 'msedge', // Specify Edge as the browser channel
    headless: false, // Run in non-headless mode to see what's happening
  });
  
  const context = await browser.newContext();
  
  // Enable console logging to catch any JavaScript errors
  context.on('console', message => {
    console.log(`[Browser Console] ${message.type().toUpperCase()}: ${message.text()}`);
  });

  // Create a new page
  const page = await context.newPage();
  
  // Navigate to the app
  console.log('Navigating to the application...');
  try {
    await page.goto('http://localhost:3000');
    console.log('Successfully navigated to the application');
  } catch (error) {
    console.error('Failed to navigate to the application:', error);
    await browser.close();
    return;
  }

  // Wait for the page to load
  await page.waitForLoadState('networkidle');
  
  // Analyze the page to find where "My tasks" or "Error loading tasks" might be
  console.log('Analyzing the page...');
  const content = await page.content();
  
  // Take a screenshot for later analysis
  await page.screenshot({ path: 'app-screenshot.png' });
  
  // Check for network requests to find API calls related to tasks
  console.log('Checking network requests...');
  const requests = [];
  page.on('request', request => {
    if (request.url().includes('api')) {
      requests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers(),
        resourceType: request.resourceType()
      });
    }
  });
  
  page.on('response', response => {
    const request = response.request();
    if (request.url().includes('api')) {
      console.log(`API Response: ${request.method()} ${request.url()} - Status: ${response.status()}`);
      response.text().then(body => {
        try {
          const jsonBody = JSON.parse(body);
          console.log('Response body:', JSON.stringify(jsonBody, null, 2));
        } catch (e) {
          console.log('Response body (not JSON):', body.substring(0, 200)); // Show first 200 chars
        }
      }).catch(e => console.error('Error getting response body:', e));
    }
  });
  
  // Check if there's a tasks tab or link and click on it
  try {
    console.log('Looking for tasks section...');
    // Try different selectors that might lead to tasks
    const taskSelectors = [
      'a:text("Tasks")', 
      'a:text("My tasks")', 
      'button:text("Tasks")',
      'div:text("Tasks")',
      'div:text("My tasks")'
    ];
    
    for (const selector of taskSelectors) {
      const element = await page.$(selector);
      if (element) {
        console.log(`Found tasks element with selector: ${selector}`);
        await element.click();
        console.log('Clicked on tasks element');
        
        // Wait for any potential error messages to appear
        await page.waitForTimeout(2000);
        
        // Check for error message
        const errorText = await page.textContent('text="Error loading tasks"');
        if (errorText) {
          console.log('Found error message:', errorText);
        }
        break;
      }
    }
  } catch (error) {
    console.error('Error while interacting with tasks section:', error);
  }
  
  // Look for potential error messages on the page
  try {
    const errorElements = await page.$$('text/Error/i');
    for (const errorElement of errorElements) {
      const text = await errorElement.textContent();
      console.log('Found error message on page:', text);
    }
  } catch (error) {
    console.error('Error while searching for error messages:', error);
  }
  
  // Get all API calls made
  console.log('API Requests made:', requests);
  
  // Check backend connection
  try {
    console.log('Testing backend connection...');
    const response = await page.evaluate(async () => {
      try {
        const res = await fetch('http://localhost:8001/health');
        if (res.ok) {
          return { ok: true, status: res.status, body: await res.text() };
        } else {
          return { ok: false, status: res.status, body: await res.text() };
        }
      } catch (e) {
        return { ok: false, error: e.toString() };
      }
    });
    console.log('Backend health check result:', response);
  } catch (error) {
    console.error('Error testing backend connection:', error);
  }
  
  // Wait for any further interaction
  console.log('Test completed. Please review the output.');
  
  // Keep browser open for manual inspection
  // await browser.close(); // Uncomment to close browser automatically
}

// Run the test
runTest().catch(error => {
  console.error('Test failed with error:', error);
});
