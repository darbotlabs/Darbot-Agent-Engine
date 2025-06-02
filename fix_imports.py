#!/usr/bin/env python3
"""
Script to fix backend import issues across all Python files
Thought into existence by Darbot
"""

import os
import re
from pathlib import Path

def fix_backend_imports(file_path):
    """Fix backend imports in a single file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace backend imports with relative imports
    patterns = [
        (r'from backend\.context\.', 'from context.'),
        (r'from backend\.kernel_agents\.', 'from kernel_agents.'),
        (r'from backend\.kernel_tools\.', 'from kernel_tools.'),
        (r'from backend\.models\.', 'from models.'),
        (r'from backend\.event_utils', 'from event_utils'),
        (r'from backend\.app_config', 'from app_config'),
        (r'from backend\.app_kernel', 'from app_kernel'),
        (r'from backend\.config_kernel', 'from config_kernel'),
        (r'from backend\.utils_kernel', 'from utils_kernel'),
        (r'from backend\.auth\.', 'from auth.'),
        (r'from backend\.handlers\.', 'from handlers.'),
        (r'from backend\.middleware\.', 'from middleware.'),
    ]
    
    original_content = content
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed imports in: {file_path}")
        return True
    
    return False

def main():
    """Fix all backend imports in the project."""
    backend_dir = Path("d:/0GH_PROD/Darbot-Agent-Engine/src/backend")
    
    if not backend_dir.exists():
        print(f"Backend directory not found: {backend_dir}")
        return
    
    fixed_files = []
    
    # Find all Python files in the backend directory
    for py_file in backend_dir.rglob("*.py"):
        if fix_backend_imports(py_file):
            fixed_files.append(py_file)
    
    print(f"\n✅ Fixed imports in {len(fixed_files)} files:")
    for file in fixed_files:
        print(f"   - {file.relative_to(backend_dir)}")

if __name__ == "__main__":
    main()
