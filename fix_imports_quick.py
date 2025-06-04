# Thought into existence by Darbot
import os
import re

def fix_relative_imports(file_path):
    """Fix relative imports in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix specific problematic imports
        replacements = [
            (r'from backend\.app_config import', 'from ..app_config import'),
            (r'from backend\.context\.', 'from ..context.'),
            (r'from backend\.kernel_agents\.', 'from ..kernel_agents.'),
            (r'from backend\.models\.', 'from ..models.'),
            (r'from backend\.event_utils import', 'from ..event_utils import'),
            (r'from backend\.kernel_tools\.', 'from ..kernel_tools.'),
            (r'from backend\.middleware\.', 'from ..middleware.'),
            (r'from backend\.auth\.', 'from ..auth.'),
            (r'from backend\.utils_kernel import', 'from ..utils_kernel import')
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def fix_imports_in_directory(directory):
    """Fix imports in all Python files in a directory"""
    fixed_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_relative_imports(file_path):
                    fixed_count += 1
    return fixed_count

if __name__ == "__main__":
    backend_dir = r"d:\0GH_PROD\Darbot-Agent-Engine\src\backend"
    print(f"Fixing imports in: {backend_dir}")
    fixed = fix_imports_in_directory(backend_dir)
    print(f"Fixed imports in {fixed} files")
