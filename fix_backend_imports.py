#!/usr/bin/env python3
"""
Fix backend import issues - convert relative imports properly
"""
import os
import re
import glob

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    print(f"Processing: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Common import patterns to fix
        patterns = [
            # app_config imports
            (r'from app_config import', 'from .app_config import'),
            (r'import app_config', 'from . import app_config'),
            
            # auth imports
            (r'from auth\.', 'from .auth.'),
            
            # context imports  
            (r'from context\.', 'from .context.'),
            
            # kernel_agents imports
            (r'from kernel_agents\.', 'from .kernel_agents.'),
            
            # middleware imports
            (r'from middleware\.', 'from .middleware.'),
            
            # models imports
            (r'from models\.', 'from .models.'),
            
            # utils imports
            (r'from utils\.', 'from .utils.'),
            (r'from utils_kernel import', 'from .utils_kernel import'),
            
            # config_kernel imports
            (r'from config_kernel import', 'from .config_kernel import'),
            
            # event_utils imports
            (r'from event_utils import', 'from .event_utils import'),
        ]
        
        # Apply fixes
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Fixed imports in {file_path}")
            return True
        else:
            print(f"  ⏭️ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """Fix all import issues in the backend"""
    backend_dir = "src/backend"
    
    if not os.path.exists(backend_dir):
        print("Backend directory not found!")
        return
    
    # Find all Python files in backend
    python_files = []
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"Found {len(python_files)} Python files to process")
    
    fixed_count = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n📊 Summary: Fixed imports in {fixed_count} files")

if __name__ == "__main__":
    main()
