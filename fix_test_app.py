# Thought into existence by Darbot

# Read the app.py test file
test_app_path = "D:\\0GH_PROD\\Darbot-Agent-Engine\\src\\backend\\tests\\test_app.py"

try:
    with open(test_app_path, 'r') as file:
        content = file.read()
    
    # Check if we need to fix the import
    if "from app_kernel import app" in content:
        print("Fixing import in test_app.py...")
        content = content.replace("from app_kernel import app", "from backend.app_kernel import app")
        content = content.replace("import app_config", "from backend import app_config")
        
        # Write the updated content
        with open(test_app_path, 'w') as file:
            file.write(content)
        
        print("Imports fixed successfully in test_app.py")
    else:
        print("No import issues found in test_app.py or file has already been fixed.")
except FileNotFoundError:
    print(f"Test file not found: {test_app_path}")
except Exception as e:
    print(f"Error fixing test file: {str(e)}")
