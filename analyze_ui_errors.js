// Thought into existence by Darbot
const { chromium } = require('playwright');

// Configuration
const url = 'http://localhost:3000';
const backendApiUrl = 'http://localhost:8001';

async function analyzeUI() {
  console.log('Starting UI analysis...');
  
  // Launch browser
  const browser = await chromium.launch({ 
    headless: false,
    executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE_PATH || undefined
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log(`Navigating to ${url}`);
    await page.goto(url, { timeout: 30000 });
    console.log('Page loaded');

    // Wait for some elements to load
    await page.waitForSelector('body', { state: 'visible', timeout: 5000 });
    console.log('Body loaded');

    // Check if there are any error messages on the page
    const errorText = await page.evaluate(() => {
      const errorElements = Array.from(document.querySelectorAll('.notification.is-danger, .error-message, .error'));
      return errorElements.map(el => el.innerText).join('\n');
    });

    if (errorText) {
      console.log('Found error messages on the page:');
      console.log(errorText);
    } else {
      console.log('No visible error messages found on the page');
    }

    // Check for network errors related to API calls
    const client = await page.context().newCDPSession(page);
    await client.send('Network.enable');

    console.log('Checking network requests...');
    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/api/')) {
        console.log(`API request to: ${url}, status: ${response.status()}`);
        if (!response.ok()) {
          console.log(`Failed API request: ${url}, status: ${response.status()}`);
          try {
            const text = await response.text();
            console.log(`Response body: ${text.substring(0, 200)}${text.length > 200 ? '...' : ''}`);
          } catch (e) {
            console.log('Could not get response body');
          }
        }
      }
    });

    // Test the backend health endpoint
    console.log('Testing backend health endpoint...');
    try {
      const healthResponse = await page.evaluate(async (api) => {
        try {
          const response = await fetch(`${api}/health`);
          const status = response.status;
          let text = '';
          try {
            text = await response.text();
          } catch (e) {}
          return { status, text };
        } catch (e) {
          return { status: 'error', text: e.toString() };
        }
      }, backendApiUrl);
      
      console.log(`Health endpoint status: ${healthResponse.status}`);
      console.log(`Health endpoint response: ${healthResponse.text}`);
    } catch (e) {
      console.error('Error testing health endpoint:', e);
    }

    // Check console errors
    console.log('Checking console errors...');
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
        console.log(`Console error: ${msg.text()}`);
      }
    });

    // Try to click on elements to reproduce the error
    console.log('Attempting to navigate the UI to trigger errors...');
    
    // Check if tasks are loaded
    const tasksLoaded = await page.evaluate(() => {
      const myTasksMenu = document.getElementById('myTasksMenu');
      if (myTasksMenu) {
        const errorMsg = myTasksMenu.innerText.includes('Error loading tasks');
        const tasks = myTasksMenu.querySelectorAll('a.menu-task').length;
        return { 
          hasError: errorMsg,
          taskCount: tasks
        };
      }
      return { hasError: false, taskCount: 0 };
    });
    
    console.log(`Tasks loaded status: ${JSON.stringify(tasksLoaded)}`);
      // Test API endpoints directly
    console.log('Testing API endpoints directly...');
    const endpoints = [
      '/api/plans',
      '/api/server-info'
    ];
    
    for (const endpoint of endpoints) {
      const apiResponse = await page.evaluate(async (params) => {
        try {
          const response = await fetch(`${params.api}${params.path}`);
          const status = response.status;
          let json = null;
          try {
            json = await response.json();
          } catch (e) {}
          return { status, json };
        } catch (e) {
          return { status: 'error', error: e.toString() };
        }
      }, { api: backendApiUrl, path: endpoint });
      
      console.log(`API endpoint ${endpoint} status: ${apiResponse.status}`);
      if (apiResponse.json) {
        console.log(`API endpoint ${endpoint} response: ${JSON.stringify(apiResponse.json).substring(0, 200)}`);
      } else if (apiResponse.error) {
        console.log(`API endpoint ${endpoint} error: ${apiResponse.error}`);
      }
    }
    
    // Check if frontend is properly configured to connect to backend
    console.log('Checking frontend configuration...');
    const frontendConfig = await page.evaluate(async () => {
      try {
        const response = await fetch('/config.js');
        const text = await response.text();
        return text;
      } catch (e) {
        return `Error: ${e.toString()}`;
      }
    });
    
    console.log('Frontend configuration:');
    console.log(frontendConfig);

    // Wait for some time to observe any async errors
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Summary
    console.log('\n========= ANALYSIS SUMMARY =========');
    console.log(`Page loaded: ${url}`);
    console.log(`Visible errors found: ${errorText ? 'Yes' : 'No'}`);
    console.log(`Console errors found: ${consoleErrors.length}`);
    console.log(`Task loading error: ${tasksLoaded.hasError ? 'Yes' : 'No'}`);
    console.log(`Tasks found: ${tasksLoaded.taskCount}`);
    console.log('==================================\n');

  } catch (error) {
    console.error('Error during analysis:', error);
  } finally {
    await browser.close();
    console.log('Analysis completed');
  }
}

analyzeUI().catch(console.error);
