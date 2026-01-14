import os
import re
from datetime import datetime

def generate_directory_tree(root_dir, prefix=""):
    """Generate a visual directory tree string."""
    tree_str = ""
    contents = sorted([c for c in os.listdir(root_dir) if c not in ['__pycache__', 'venv', '.git', '.pytest_cache', '.env']])
    
    # Filter files to show only relevant ones (e.g., .py, .md) to keep tree clean
    # But for structure map, maybe we want to see structure. Let's keep directories and .py files mainly.
    filtered_contents = []
    for c in contents:
        path = os.path.join(root_dir, c)
        if os.path.isdir(path):
            filtered_contents.append(c)
        elif c.endswith('.py') or c.endswith('.md'):
            filtered_contents.append(c)
            
    pointers = [('├── ', '│   ')] * (len(filtered_contents) - 1) + [('└── ', '    ')]
    
    for pointer, content in zip(pointers, filtered_contents):
        path = os.path.join(root_dir, content)
        name = content
        
        if os.path.isdir(path):
            tree_str += f"{prefix}{pointer[0]}📂 {name}/\n"
            tree_str += generate_directory_tree(path, prefix + pointer[1])
        else:
            tree_str += f"{prefix}{pointer[0]}📄 {name}\n"
            
    return tree_str

def scan_dependencies(root_dir):
    """Scan Python files for imports to build dependency graph."""
    dependencies = {}
    
    project_root_name = os.path.basename(root_dir) # backend
    
    for root, dirs, files in os.walk(root_dir):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                # module_name: api/routers/trading_router
                rel_path = os.path.relpath(file_path, root_dir)
                module_name = rel_path.replace('\\', '/').replace('.py', '')
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    imports = []
                    # Simple regex for 'import x' and 'from x import y'
                    # Catch 'from backend.api import x' or 'import backend.utils'
                    import_lines = re.findall(r'^(?:from|import)\s+([\w\.]+)', content, re.MULTILINE)
                    
                    for imp in import_lines:
                        # Filter only internal modules (starting with backend)
                        if imp.startswith('backend'):
                            # backend.api.routers -> api/routers
                            imp_clean = imp.replace('backend.', '').replace('.', '/')
                            imports.append(imp_clean)
                    
                    if imports:
                        dependencies[module_name] = imports
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    
    return dependencies

def generate_mermaid_graph(dependencies):
    """Generate Mermaid graph with subgraphs for directories."""
    lines = ["graph TD"]
    
    # Organize modules by top-level directory
    # structure = { 'api': ['api/routers/x', ...], 'ai': [...] }
    structure = {}
    
    for module in dependencies.keys():
        parts = module.split('/')
        top_dir = parts[0] if len(parts) > 1 else 'root'
        
        if top_dir not in structure:
            structure[top_dir] = []
        structure[top_dir].append(module)
        
    # Create Subgraphs
    for folder, modules in structure.items():
        if folder == 'root': continue
        
        lines.append(f"    subgraph {folder.upper()} [{folder.upper()}]")
        for mod in modules:
            # node id: filename without path to save space, but make unique?
            # actually better to use full path as id, but display name as filename
            node_id = mod.replace('/', '_')
            node_label = mod.split('/')[-1]
            lines.append(f"        {node_id}[{node_label}]")
        lines.append("    end")
        
    # Edges
    # Limit to prevent mess
    count = 0
    max_rels = 200 
    
    for module, imports in dependencies.items():
        src_id = module.replace('/', '_')
        
        for imp in imports:
            # We only draw edge if target exists in our dependencies (meaning it's a scanned file)
            # OR if it looks like a valid backend module
            target_id = imp.replace('/', '_')
            
            # Draw edge
            lines.append(f"    {src_id} --> {target_id}")
            count += 1
            if count > max_rels: break
    
    return "\n".join(lines)

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
    project_root = os.path.dirname(root_dir)
    
    print(f"Scanning {root_dir}...")
    
    # 1. Directory Tree
    tree_view = generate_directory_tree(root_dir)
    
    # 2. Dependency Graph
    deps = scan_dependencies(root_dir)
    mermaid_graph = generate_mermaid_graph(deps)
    
    output_path = os.path.join(project_root, 'docs', 'architecture', 'structure-map.md')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    content = f"""# System Structure Map
Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Directory Structure

```text
backend/
{tree_view}
```

## 2. Module Dependency Graph

```mermaid
{mermaid_graph}
```

## Note
This map is auto-generated by `backend/utils/structure_mapper.py`.
Run the script to update this file before development.
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Structure map generated at: {output_path}")

if __name__ == "__main__":
    main()
