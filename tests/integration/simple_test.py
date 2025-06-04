# Thought into existence by Darbot
# Simple task submission test script
import requests
import time
import sys
import os

print("Task Submission Test Script - Darbot Agent Engine")
print("-" * 80)

# Configuration
BACKEND_URL = os.environ.get("BACKEND_API_URL", "http://localhost:8001")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
TEST_TASK = "Create a project plan for website redesign"

def check_backend_health():
    """Check if the backend server is running and healthy."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend server is running. Status: {response.text}")
            return True
        else:
            print(f"❌ Backend server returned status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to backend server: {e}")
        return False

def check_frontend_server():
    """Check if the frontend server is running."""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend server is running. Status: {response.status_code}")
            return True
        else:
            print(f"❌ Frontend server returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to frontend server: {e}")
        return False

def submit_task():
    """Submit a task to the backend and return the result."""
    print("\nSubmitting task: '{}'".format(TEST_TASK))
    
    headers = {
        "Content-Type": "application/json",
        "X-MS-CLIENT-PRINCIPAL-NAME": "Test User",
        "X-MS-CLIENT-PRINCIPAL-ID": "test-user-id-12345"
    }
    data = {
        "session_id": f"test_{int(time.time())}",
        "description": TEST_TASK
    }
    try:
        print("Attempting direct backend submission...")
        response = requests.post(
            f"{BACKEND_URL}/api/input_task",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            print("✅ Task submitted successfully!")
            print(f"Session ID: {result.get('session_id')}")
            print(f"Plan ID: {result.get('plan_id')}")
            return result
        else:
            print("❌ Task submission failed with status code {}".format(response.status_code))
            print("Response: {}".format(response.text))
            return None
    except requests.exceptions.RequestException as e:
        print("❌ Request exception: {}".format(e))
        return None

def check_plan_status(session_id):
    """Check the status of the submitted plan."""
    if not session_id:
        print("❌ No session ID available to check plan status")
        return
    print("\nChecking status for session {}...".format(session_id))
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/plans?session_id={session_id}",
            timeout=10
        )
        if response.status_code == 200:
            plans = response.json()
            if plans and isinstance(plans, list):
                plan_data = plans[0]
                print("✅ Plan retrieved successfully!")
                print(f"Status: {plan_data.get('overall_status', 'unknown')}")
                print(f"Goal: {plan_data.get('initial_goal', 'unknown')}")
                steps = plan_data.get('total_steps', 0)
                completed = plan_data.get('completed', 0)
                print(f"Progress: {completed}/{steps} steps completed")
                return plan_data
            else:
                print("❌ No plan data returned for session {}".format(session_id))
                return None
        else:
            print("❌ Failed to retrieve plan with status code {}".format(response.status_code))
            print("Response: {}".format(response.text))
            return None
    except requests.exceptions.RequestException as e:
        print("❌ Request exception: {}".format(e))
        return None

def main():
    """Run the complete test flow."""
    print("\n[1/4] Checking backend server health...")
    backend_ok = check_backend_health()
    if not backend_ok:
        print("⚠️ Backend server health check failed, but continuing with the test...")
    
    print("\n[2/4] Checking frontend server availability...")
    frontend_ok = check_frontend_server()
    if not frontend_ok:
        print("⚠️ Frontend server check failed, but continuing with the test...")
    
    print("\n[3/4] Submitting test task...")
    result = submit_task()
    
    if result:
        session_id = result.get('session_id')
        
        print("\n[4/4] Checking plan status...")
        # Wait a bit for the plan to be processed
        time.sleep(2)
        plan_data = check_plan_status(session_id)
        
        if plan_data:
            print("\n✅ Test completed successfully!")
            return 0
        else:
            print("\n❌ Failed to retrieve plan status")
            return 1
    else:
        print("\n❌ Task submission failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
