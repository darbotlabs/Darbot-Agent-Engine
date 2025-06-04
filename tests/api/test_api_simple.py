# Thought into existence by Darbot
import requests
import json

def test_task_creation():
    print("🧪 Testing Task Creation API...")
    
    # Test health endpoint first
    try:
        health_response = requests.get("http://localhost:8001/api/health")
        print(f"✅ Health Check: {health_response.status_code}")
        if health_response.status_code == 200:
            print(f"📋 Health Status: {health_response.json()['overall_status']}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return
    
    # Test task creation
    task_data = {
        "task": "Test task: Verify 400 error is fixed and multi-agent system works",
        "user_id": "test-user-debug"
    }
    
    try:
        print("📤 Sending task creation request...")
        response = requests.post(
            "http://localhost:8001/api/input_task",
            json=task_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Task Creation API Working!")
            try:
                response_data = response.json()
                print(f"📋 Response: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📄 Response Text: {response.text}")
        else:
            print(f"❌ ISSUE: Status {response.status_code}")
            print(f"📄 Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Task Creation Error: {e}")

if __name__ == "__main__":
    test_task_creation()
