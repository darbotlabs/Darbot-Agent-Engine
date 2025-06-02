# Thought into existence by Darbot
# API endpoint test script

import requests
import json
import os
from colorama import Fore, Style, init
import time

# Initialize colorama for colored output
init()

# Base URLs
BACKEND_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:3000"

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an endpoint and return the result"""
    print(f"{Fore.YELLOW}Testing {method} {url}{Style.RESET_ALL}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            print(f"{Fore.RED}Unsupported method: {method}{Style.RESET_ALL}")
            return None
        
        status_color = Fore.GREEN if response.status_code < 400 else Fore.RED
        print(f"{status_color}Status: {response.status_code}{Style.RESET_ALL}")
        
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            try:
                json_response = response.json()
                print(f"{Fore.CYAN}Response:{Style.RESET_ALL}")
                print(json.dumps(json_response, indent=2))
                return json_response
            except json.JSONDecodeError:
                print(f"{Fore.RED}Failed to parse JSON response{Style.RESET_ALL}")
                print(response.text[:500])  # Show first 500 chars
        else:
            print(f"{Fore.CYAN}Response content type: {content_type}{Style.RESET_ALL}")
            print(response.text[:500] if response.text else "[No content]")  # Show first 500 chars
            
        return response
        
    except requests.RequestException as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        return None

def generate_session_id():
    """Generate a unique session ID"""
    return f"test_session_{int(time.time())}"

def main():
    session_id = generate_session_id()
    print(f"{Fore.CYAN}Using session ID: {session_id}{Style.RESET_ALL}")
    
    # Testing backend health
    print(f"\n{Fore.BLUE}=== Testing Backend Health ==={Style.RESET_ALL}")
    test_endpoint(f"{BACKEND_URL}/health")
    
    # Testing backend API endpoints with the /api prefix
    print(f"\n{Fore.BLUE}=== Testing Backend API Endpoints (with /api prefix) ==={Style.RESET_ALL}")
    
    # Create a task
    task_data = {
        "session_id": session_id,
        "description": "Test task from API script"
    }
    test_endpoint(f"{BACKEND_URL}/api/input_task", method="POST", data=task_data)
    
    # Wait a bit for the task to be processed
    time.sleep(2)
    
    # Get plans
    test_endpoint(f"{BACKEND_URL}/api/plans?session_id={session_id}")
    
    # Testing backend API endpoints without the /api prefix
    print(f"\n{Fore.BLUE}=== Testing Backend API Endpoints (without /api prefix) ==={Style.RESET_ALL}")
    
    # Create another task
    task_data = {
        "session_id": f"{session_id}_2",
        "description": "Test task without api prefix"
    }
    test_endpoint(f"{BACKEND_URL}/input_task", method="POST", data=task_data)
    
    # Testing frontend API endpoints
    print(f"\n{Fore.BLUE}=== Testing Frontend API Endpoints ==={Style.RESET_ALL}")
    test_endpoint(f"{FRONTEND_URL}/config.js")
    
    print(f"\n{Fore.GREEN}All tests completed!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
