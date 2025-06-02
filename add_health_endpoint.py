# Thought into existence by Darbot
import re

def add_health_endpoint():
    """Add a health endpoint to app_kernel.py if it doesn't exist."""
    
    # Read the app_kernel.py file
    app_kernel_path = "D:\\0GH_PROD\\Darbot-Agent-Engine\\src\\backend\\app_kernel.py"
    with open(app_kernel_path, 'r') as file:
        content = file.read()
    
    # Check if health endpoint already exists
    if "@app.get(\"/health\"" in content or "@app.route(\"/health\"" in content:
        print("Health endpoint already exists.")
        return
    
    # Find a good place to insert the health endpoint
    # Look for the first endpoint definition after the app declaration
    match = re.search(r"app\s*=\s*FastAPI\(.*?\)[^\@]*", content, re.DOTALL)
    if match:
        insert_position = match.end()        health_endpoint = """
# Health check endpoint - Thought into existence by Darbot
@app.get("/health", tags=["system"])
async def health_check():
    \"\"\"Health check endpoint for the API.\"\"\"
    return {"status": "healthy"}

"""
        # Insert the health endpoint
        new_content = content[:insert_position] + health_endpoint + content[insert_position:]
        
        # Write the modified content back to the file
        with open(app_kernel_path, 'w') as file:
            file.write(new_content)
        
        print("Health endpoint added successfully.")
    else:
        print("Could not find a suitable location to insert health endpoint.")

# Run the function
if __name__ == "__main__":
    add_health_endpoint()
