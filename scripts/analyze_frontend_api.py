"""
Frontend API Usage Analysis

Extract all unique API endpoints called by frontend
"""

import re
from pathlib import Path

frontend_src = Path("frontend/src")
api_calls = set()

# Patterns to match
patterns = [
    r"fetch\(['\"]([^'\"]+)['\"]",
    r"fetch\(`[^`]*?(/api/[^`]+)`",
    r"fetch\(`\$\{[^}]+\}(/api/[^`]+)`",
]

for ts_file in frontend_src.rglob("*.tsx"):
    content = ts_file.read_text(encoding='utf-8', errors='ignore')
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            if '/api/' in match or match.startswith('/'):
                # Clean up the path
                path = match.split('?')[0]  # Remove query params
                path = re.sub(r'\$\{[^}]+\}', '{param}', path)  # Replace template vars
                api_calls.add(path)

# Sort and print
print("Frontend API Calls Found:")
print("="*70)
for call in sorted(api_calls):
    print(call)

print(f"\nTotal unique API paths: {len(api_calls)}")
