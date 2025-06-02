# Thought into existence by Darbot
import os
import re

def fix_imports_in_file(file_path):
    """Fix imports in a single file by adding backend. prefix."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add backend. prefix to imports
        original_content = content
        # Replace 'from kernel_agents.' with 'from backend.kernel_agents.'
        content = re.sub(r'from kernel_agents\.', r'from backend.kernel_agents.', content)
        
        # Replace 'from models.' with 'from backend.models.'
        content = re.sub(r'from models\.', r'from backend.models.', content)
        
        # Replace 'from context.' with 'from backend.context.'
        content = re.sub(r'from context\.', r'from backend.context.', content)

        # Replace 'from utils_kernel import' with 'from backend.utils_kernel import'
        content = re.sub(r'from utils_kernel import', r'from backend.utils_kernel import', content)
        
        # Replace 'from kernel_tools.' with 'from backend.kernel_tools.'
        content = re.sub(r'from kernel_tools\.', r'from backend.kernel_tools.', content)

        # Replace 'from app_config import' with 'from backend.app_config import'
        content = re.sub(r'from app_config import', r'from backend.app_config import', content)

        # Replace 'from event_utils import' with 'from backend.event_utils import'
        content = re.sub(r'from event_utils import', r'from backend.event_utils import', content)
        
        # Replace 'from middleware.' with 'from backend.middleware.'
        content = re.sub(r'from middleware\.', r'from backend.middleware.', content)

        # Replace 'from auth.' with 'from backend.auth.'
        content = re.sub(r'from auth\.', r'from backend.auth.', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_all_backend_imports():
    """Add backend. prefix to all imports in the backend directory."""
    backend_dir = r"d:\0GH_PROD\Darbot-Agent-Engine\src\backend"
    fixed_count = 0
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path):
                    fixed_count += 1
    
    print(f"Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    fix_all_backend_imports()
