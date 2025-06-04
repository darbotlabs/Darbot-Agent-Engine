# Thought into existence by Darbot
# Test script to validate task creation functionality
import requests
import json
import uuid
import time

def test_task_creation():
    """Test the task creation endpoint."""
    print("🚀 Testing Task Creation Functionality...")
    
    # Generate a unique session ID
    session_id = f"test-session-{uuid.uuid4().hex[:8]}"
    
    # Task data
    task_data = {
        "session_id": session_id,
        "description": "Create a comprehensive project plan for building a new mobile app"
    }
    
    print(f"📝 Session ID: {session_id}")
    print(f"📝 Task Description: {task_data['description']}")
    
    try:
        # Test the input_task endpoint
        print("🔗 Sending task to backend...")
        response = requests.post(
            "http://localhost:8001/api/input_task",
            json=task_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Content: {response.text}")
        
        if response.status_code == 200:
            print("✅ Task creation successful!")
            
            # Wait a moment for processing
            time.sleep(2)
            
            # Check if plans were created
            print("🔍 Checking for created plans...")
            plans_response = requests.get(
                f"http://localhost:8001/api/plans?session_id={session_id}",
                timeout=5
            )
            
            print(f"📊 Plans Response Status: {plans_response.status_code}")
            if plans_response.status_code == 200:
                plans = plans_response.json()
                print(f"📋 Number of plans found: {len(plans)}")
                if plans:
                    for plan in plans:
                        print(f"  📌 Plan ID: {plan['id']}")
                        print(f"  📝 Goal: {plan['initial_goal']}")
                        print(f"  📊 Status: {plan['overall_status']}")
                        print(f"  🔢 Total Steps: {plan['total_steps']}")
                else:
                    print("⚠️ No plans found yet (may still be processing)")
            else:
                print(f"❌ Failed to retrieve plans: {plans_response.text}")
                
        else:
            print(f"❌ Task creation failed: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_task_creation()
