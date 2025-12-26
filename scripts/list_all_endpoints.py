#!/usr/bin/env python3
"""
Extract all endpoints from all routers
"""

import re
from pathlib import Path

router_dir = Path("backend/api")
routers = list(router_dir.glob("*router.py"))

print(f"Scanning {len(routers)} routers...\n")

all_endpoints = []

for router_path in sorted(routers):
    content = router_path.read_text(encoding='utf-8')
    
    # Find router prefix
    prefix_match = re.search(r'router\s*=\s*APIRouter\([^)]*prefix=["\']([^"\']+)', content)
    prefix = prefix_match.group(1) if prefix_match else "/unknown"
    
    # Find all endpoints
    pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'
    matches = re.findall(pattern, content)
    
    if matches:
        print(f"\n## {router_path.name}")
        print(f"Prefix: {prefix}")
        print(f"Endpoints ({len(matches)}):")
        
        for method, path in matches:
            full_path = f"{prefix}{path}"
            all_endpoints.append((method.upper(), full_path, router_path.stem))
            print(f"  {method.upper():6} {full_path}")

print(f"\n\n{'='*70}")
print(f"Total: {len(all_endpoints)} endpoints across {len(routers)} routers")
print(f"{'='*70}")

# Save to file
output_path = Path("all_endpoints.txt")
with open(output_path, 'w') as f:
    for method, path, router in sorted(all_endpoints):
        f.write(f"{method:6} {path:60} # {router}\n")

print(f"\nSaved to: {output_path}")
