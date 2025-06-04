// Thought into existence by Darbot
// Simple UI check script

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Create screenshots directory if it doesn't exist
const screenshotsDir = path.join(__dirname, 'screenshots', 'debug');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
}

// Get current timestamp for unique screenshot names
const getTimestamp = () => {
  return new Date().toISOString().replace(/[:.]/g, '-');
};

(async () => {
  console.log('Starting simple UI check...');
  
  // Launch browser
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
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
    
    // Print the page title
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for basic page elements
    console.log('Checking for basic page elements...');
    
    // Check if we have a textarea for task input
    const taskInputExists = await page.evaluate(() => {
      const textareas = Array.from(document.querySelectorAll('textarea'));
      console.log('Found textareas:', textareas.length);
      return textareas.map(t => ({
        placeholder: t.placeholder,
        id: t.id,
        className: t.className
      }));
    });
    
    console.log('Textarea elements:', taskInputExists);
    
    // Check page structure
    const pageStructure = await page.evaluate(() => {
      return {
        hasHeader: !!document.querySelector('header'),
        hasFooter: !!document.querySelector('footer'),
        hasMain: !!document.querySelector('main'),
        mainContent: document.querySelector('main')?.innerText,
        buttons: Array.from(document.querySelectorAll('button')).map(b => ({
          text: b.innerText,
          disabled: b.disabled,
          className: b.className
        }))
      };
    });
    
    console.log('Page structure:', pageStructure);
    
    // Log console messages from the page
    page.on('console', msg => {
      console.log(`PAGE CONSOLE: ${msg.type()}: ${msg.text()}`);
    });
    
    // Wait a bit to collect console logs
    await page.waitForTimeout(3000);
    
    // Take a final screenshot
    await page.screenshot({ 
      path: path.join(screenshotsDir, `final_state_${getTimestamp()}.png`),
      fullPage: true
    });
    
    console.log('Simple UI check completed.');
  } catch (error) {
    console.error('Test failed with error:', error);
    await page.screenshot({ 
      path: path.join(screenshotsDir, `error_${getTimestamp()}.png`),
      fullPage: true
    });
  } finally {
    await browser.close();
  }
})();
