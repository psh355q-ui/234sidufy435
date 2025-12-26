#!/usr/bin/env python3
"""
Fix syntax errors caused by auto-applier inserting imports in wrong places
"""

import re
from pathlib import Path

def fix_router_imports(file_path):
    """Fix import order in a router file"""
    content = file_path.read_text(encoding='utf-8')
    original = content
    
    # Pattern: logging_decorator import inserted in middle of multi-line import
    # Look for cases where logging_decorator is followed by indented lines (continuation of previous import)
    pattern = r'from backend\.ai\.skills\.common\.logging_decorator import log_endpoint\n(\s+\w+.*\n)+\)'
    
    if re.search(pattern, content):
        print(f"⚠️  {file_path.name}: Found bad import placement")
        
        # Extract the misplaced import and following lines
        match = re.search(pattern, content)
        if match:
            # Remove the logging_decorator import from wrong location
            content = content.replace('from backend.ai.skills.common.logging_decorator import log_endpoint\n', '', 1)
            
            # Add it after the closing paren of the previous import
            # Find the next standalone import or router definition
            insert_pattern = r'(\)\s*\n)'
            
            def replacer(m):
                return m.group(1) + '\nfrom backend.ai.skills.common.logging_decorator import log_endpoint\n'
            
            content = re.sub(insert_pattern, replacer, content, count=1)
            
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed {file_path.name}")
            return True
    
    return False

# Find all router files
router_dir = Path("backend/api")
routers = list(router_dir.glob("*router.py"))

print(f"Checking {len(routers)} router files...")
print("="*60)

fixed_count = 0

for router_path in routers:
    try:
        if fix_router_imports(router_path):
            fixed_count += 1
    except Exception as e:
        print(f"❌ Error in {router_path.name}: {e}")

print("="*60)
print(f"✅ Fixed {fixed_count} files")
