# Thought into existence by Darbot

# Read the app_kernel.py file
app_kernel_path = "D:\\0GH_PROD\\Darbot-Agent-Engine\\src\\backend\\app_kernel.py"
with open(app_kernel_path, 'r') as file:
    content = file.read()

# Check if health endpoint already exists
if "@app.get(\"/health\"" in content or "@app.route(\"/health\"" in content:
    print("Health endpoint already exists.")
else:
    # Find a good spot to insert the health endpoint - after app initialization
    app_init_index = content.find("app = FastAPI(")
    if app_init_index >= 0:
        # Find the end of the app initialization statement
        app_init_end = content.find(")", app_init_index)
        if app_init_end >= 0:
            # Move to after the closing parenthesis
            insert_position = app_init_end + 1
            
            # Define the health endpoint code
            health_endpoint = """

# Health check endpoint - Thought into existence by Darbot
@app.get("/health", tags=["system"])
async def health_check():
    # Health check endpoint for the API
    return {"status": "healthy"}
"""
            
            # Insert the health endpoint
            new_content = content[:insert_position] + health_endpoint + content[insert_position:]
            
            # Write the modified content back to the file
            with open(app_kernel_path, 'w') as file:
                file.write(new_content)
            
            print("Health endpoint added successfully.")
        else:
            print("Could not find end of FastAPI initialization.")
    else:
        print("Could not find FastAPI app initialization.")
