// Frontend diagnostic script to help troubleshoot task creation issues
// Add this script to the browser console to diagnose problems

console.log('🔍 Starting Darbot Engine API Diagnostic...\n');

async function runDiagnostics() {
    const results = {
        apiEndpoint: null,
        authHeaders: null,
        backendConnectivity: null,
        plansEndpoint: null,
        inputTaskEndpoint: null,
        localStorage: null,
        iframe: null
    };

    // Test 1: Check API endpoint configuration
    console.log('1️⃣ Checking API endpoint configuration...');
    try {
        const apiEndpoint = getStoredData('apiEndpoint');
        if (apiEndpoint) {
            console.log(`✅ API endpoint configured: ${apiEndpoint}`);
            results.apiEndpoint = { status: 'OK', value: apiEndpoint };
        } else {
            console.log('❌ API endpoint not configured');
            results.apiEndpoint = { status: 'ERROR', value: null };
        }
    } catch (error) {
        console.log('❌ Error checking API endpoint:', error.message);
        results.apiEndpoint = { status: 'ERROR', error: error.message };
    }

    // Test 2: Check authentication headers
    console.log('\n2️⃣ Checking authentication headers...');
    try {
        const headers = await window.headers;
        console.log('✅ Auth headers resolved:', headers);
        results.authHeaders = { status: 'OK', headers: headers };
    } catch (error) {
        console.log('❌ Error getting auth headers:', error.message);
        results.authHeaders = { status: 'ERROR', error: error.message };
    }

    // Test 3: Test backend connectivity
    console.log('\n3️⃣ Testing backend connectivity...');
    if (results.apiEndpoint.status === 'OK' && results.authHeaders.status === 'OK') {
        try {
            // Test a simple endpoint first - try the plans endpoint
            const response = await fetch(results.apiEndpoint.value + '/plans', {
                method: 'GET',
                headers: results.authHeaders.headers
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Backend connectivity OK, plans endpoint responding');
                console.log(`   Retrieved ${Array.isArray(data) ? data.length : 'unknown'} plans`);
                results.backendConnectivity = { status: 'OK', plansCount: Array.isArray(data) ? data.length : 0 };
                results.plansEndpoint = { status: 'OK', data: data };
            } else {
                console.log(`❌ Backend connectivity failed: ${response.status} ${response.statusText}`);
                results.backendConnectivity = { status: 'ERROR', httpStatus: response.status, statusText: response.statusText };
                results.plansEndpoint = { status: 'ERROR', httpStatus: response.status };
            }
        } catch (error) {
            console.log('❌ Network error connecting to backend:', error.message);
            results.backendConnectivity = { status: 'ERROR', error: error.message };
            results.plansEndpoint = { status: 'ERROR', error: error.message };
        }
    } else {
        console.log('⏭️ Skipping backend test due to configuration issues');
        results.backendConnectivity = { status: 'SKIPPED', reason: 'Configuration issues' };
    }

    // Test 4: Test input_task endpoint
    console.log('\n4️⃣ Testing input_task endpoint...');
    if (results.backendConnectivity.status === 'OK') {
        try {
            const testPayload = {
                session_id: `diagnostic_${Date.now()}`,
                description: 'Diagnostic test task - ignore this'
            };
            
            const response = await fetch(results.apiEndpoint.value + '/input_task', {
                method: 'POST',
                headers: results.authHeaders.headers,
                body: JSON.stringify(testPayload)
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✅ Input task endpoint responding correctly');
                console.log('   Response:', data);
                results.inputTaskEndpoint = { status: 'OK', response: data };
            } else {
                const errorText = await response.text();
                console.log(`❌ Input task endpoint failed: ${response.status} ${response.statusText}`);
                console.log('   Error details:', errorText);
                results.inputTaskEndpoint = { status: 'ERROR', httpStatus: response.status, error: errorText };
            }
        } catch (error) {
            console.log('❌ Error testing input_task endpoint:', error.message);
            results.inputTaskEndpoint = { status: 'ERROR', error: error.message };
        }
    } else {
        console.log('⏭️ Skipping input_task test due to backend connectivity issues');
        results.inputTaskEndpoint = { status: 'SKIPPED', reason: 'Backend connectivity issues' };
    }

    // Test 5: Check localStorage functionality
    console.log('\n5️⃣ Checking localStorage functionality...');
    try {
        const testKey = 'diagnostic_test';
        const testValue = 'test_value_' + Date.now();
        setStoredData(testKey, testValue);
        const retrieved = getStoredData(testKey);
        if (retrieved === testValue) {
            console.log('✅ localStorage working correctly');
            results.localStorage = { status: 'OK' };
            // Clean up
            localStorage.removeItem(testKey);
        } else {
            console.log('❌ localStorage not working correctly');
            results.localStorage = { status: 'ERROR', expected: testValue, actual: retrieved };
        }
    } catch (error) {
        console.log('❌ Error testing localStorage:', error.message);
        results.localStorage = { status: 'ERROR', error: error.message };
    }

    // Test 6: Check iframe setup
    console.log('\n6️⃣ Checking iframe setup...');
    try {
        const iframe = document.getElementById('viewIframe');
        if (iframe) {
            console.log('✅ iframe element found');
            console.log(`   Current src: ${iframe.src || 'not set'}`);
            results.iframe = { status: 'OK', src: iframe.src };
        } else {
            console.log('❌ iframe element not found');
            results.iframe = { status: 'ERROR', error: 'iframe element not found' };
        }
    } catch (error) {
        console.log('❌ Error checking iframe:', error.message);
        results.iframe = { status: 'ERROR', error: error.message };
    }

    // Summary
    console.log('\n📋 DIAGNOSTIC SUMMARY');
    console.log('=====================');
    
    const allTests = [
        { name: 'API Endpoint', result: results.apiEndpoint },
        { name: 'Auth Headers', result: results.authHeaders },
        { name: 'Backend Connectivity', result: results.backendConnectivity },
        { name: 'Plans Endpoint', result: results.plansEndpoint },
        { name: 'Input Task Endpoint', result: results.inputTaskEndpoint },
        { name: 'localStorage', result: results.localStorage },
        { name: 'iframe Setup', result: results.iframe }
    ];
    
    allTests.forEach(test => {
        const status = test.result?.status || 'UNKNOWN';
        const icon = status === 'OK' ? '✅' : status === 'SKIPPED' ? '⏭️' : '❌';
        console.log(`${icon} ${test.name}: ${status}`);
    });

    const failedTests = allTests.filter(test => test.result?.status === 'ERROR');
    
    if (failedTests.length === 0) {
        console.log('\n🎉 All tests passed! The app should be working correctly.');
        console.log('   If you\'re still experiencing issues, try refreshing the page.');
    } else {
        console.log(`\n⚠️  ${failedTests.length} test(s) failed. Issues found:`);
        failedTests.forEach(test => {
            console.log(`   • ${test.name}: ${test.result.error || test.result.statusText || 'Unknown error'}`);
        });
        
        // Provide specific recommendations
        console.log('\n💡 RECOMMENDATIONS:');
        if (results.apiEndpoint.status === 'ERROR') {
            console.log('   • Refresh the page to reset API endpoint configuration');
        }
        if (results.backendConnectivity.status === 'ERROR') {
            console.log('   • Check if the backend server is running');
            console.log('   • Verify the BACKEND_API_URL environment variable');
            console.log('   • Check for CORS configuration issues');
        }
        if (results.authHeaders.status === 'ERROR') {
            console.log('   • Check authentication configuration');
            console.log('   • Verify AUTH_ENABLED environment variable');
        }
    }

    console.log('\n📄 Full diagnostic results:');
    console.log(JSON.stringify(results, null, 2));
    
    return results;
}

// Auto-run the diagnostics
runDiagnostics().catch(error => {
    console.log('❌ Diagnostic script failed:', error);
});