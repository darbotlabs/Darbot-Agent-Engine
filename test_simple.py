import requests
import json

print("🚀 Testing Darbot Agent Engine Setup...")

# Test backend health
try:
    print("🔍 Testing backend health...")
    response = requests.get("http://localhost:8001/api/health", timeout=10)
    if response.status_code == 200:
        health_data = response.json()
        print(f"✅ Backend health: {health_data.get('overall_status', 'unknown')}")
    else:
        print(f"❌ Backend health failed: {response.status_code}")
except Exception as e:
    print(f"❌ Backend health error: {e}")

# Test frontend
try:
    print("🌐 Testing frontend...")
    response = requests.get("http://localhost:3000", timeout=10)
    if response.status_code in [200, 307]:  # 307 is redirect which is expected
        print("✅ Frontend accessible")
    else:
        print(f"❌ Frontend failed: {response.status_code}")
except Exception as e:
    print(f"❌ Frontend error: {e}")

# Test task creation
try:
    print("📝 Testing task creation...")
    headers = {
        "Content-Type": "application/json",
        "X-Ms-Client-Principal-Id": "test-user-12345",
        "X-Ms-Client-Principal-Name": "Test User"
    }
    
    task_data = {
        "description": "Test task for validation",
        "session_id": "test_session_123"
    }
    
    response = requests.post(
        "http://localhost:8001/api/input_task",
        json=task_data,
        headers=headers,
        timeout=30
    )
    
    print(f"📥 Task creation response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Task created: {result}")
    else:
        print(f"❌ Task creation failed: {response.text}")
        
except Exception as e:
    print(f"❌ Task creation error: {e}")

print("🏁 Test completed!")
