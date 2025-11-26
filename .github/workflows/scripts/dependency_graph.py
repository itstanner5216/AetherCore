#!/usr/bin/env python3
"""
Dependency Graph Builder
Builds a dependency graph by analyzing imports, requires, and references across files.

Part of AetherCore Repository Cleanup System
"""

import re
import ast
import logging
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class DependencyGraphBuilder:
    """
    Builds dependency graphs by analyzing code imports and references.
    Supports Python, JavaScript/TypeScript, and config file references.
    """
    
    def __init__(self, repo_path: Path):
        self.repo_path = Path(repo_path)
        self.file_index: Dict[str, Path] = {}  # basename -> full path
        self.module_index: Dict[str, Path] = {}  # module name -> full path
        
    def _build_file_index(self, files: List[Path]):
        """Build index of all files for resolution"""
        for file_path in files:
            rel_path = file_path.relative_to(self.repo_path)
            
            # Index by basename
            self.file_index[file_path.name] = str(rel_path)
            
            # Index by stem (without extension)
            self.file_index[file_path.stem] = str(rel_path)
            
            # Index by module path (for Python)
            if file_path.suffix == '.py':
                module_parts = list(rel_path.parts[:-1]) + [file_path.stem]
                module_name = '.'.join(module_parts)
                self.module_index[module_name] = str(rel_path)
                
                # Also index partial module paths
                for i in range(len(module_parts)):
                    partial = '.'.join(module_parts[i:])
                    if partial not in self.module_index:
                        self.module_index[partial] = str(rel_path)
                        
    def build_graph(self, files: List[Path]) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        """
        Build dependency graph from list of files.
        
        Returns:
            Tuple of (forward_graph, reverse_graph)
            - forward_graph: file -> set of files it imports
            - reverse_graph: file -> set of files that import it
        """
        self._build_file_index(files)
        
        forward_graph: Dict[str, Set[str]] = defaultdict(set)
        reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        
        for file_path in files:
            rel_path = str(file_path.relative_to(self.repo_path))
            ext = file_path.suffix.lower()
            
            try:
                if ext == '.py':
                    deps = self._analyze_python_imports(file_path)
                elif ext in {'.js', '.jsx', '.ts', '.tsx', '.mjs'}:
                    deps = self._analyze_js_imports(file_path)
                elif ext == '.json':
                    deps = self._analyze_json_references(file_path)
                elif ext in {'.yaml', '.yml'}:
                    deps = self._analyze_yaml_references(file_path)
                elif ext == '.md':
                    deps = self._analyze_markdown_links(file_path)
                else:
                    deps = set()
                    
                # Resolve dependencies to actual files
                resolved_deps = self._resolve_dependencies(deps, file_path)
                
                forward_graph[rel_path] = resolved_deps
                
                # Build reverse graph
                for dep in resolved_deps:
                    reverse_graph[dep].add(rel_path)
                    
            except Exception as e:
                logger.warning(f"Error analyzing {rel_path}: {e}")
                forward_graph[rel_path] = set()
                
        return dict(forward_graph), dict(reverse_graph)
    
    def _analyze_python_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from Python file using AST"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                        imports.add(alias.name)
                        
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
                        imports.add(node.module.split('.')[0])
                        
                    # Handle relative imports
                    if node.level > 0:
                        # Relative import - need to resolve based on file location
                        current_dir = file_path.parent
                        for _ in range(node.level - 1):
                            current_dir = current_dir.parent
                        if node.module:
                            imports.add(f"_relative:{current_dir.name}.{node.module}")
                            
        except SyntaxError:
            # Fall back to regex for files with syntax errors
            imports = self._regex_python_imports(file_path)
            
        return imports
    
    def _regex_python_imports(self, file_path: Path) -> Set[str]:
        """Fallback regex-based Python import detection"""
        imports = set()
        
        patterns = [
            r'^import\s+(\w+)',
            r'^from\s+([\w.]+)\s+import',
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    for pattern in patterns:
                        match = re.match(pattern, line.strip())
                        if match:
                            imports.add(match.group(1).split('.')[0])
        except Exception:
            pass
            
        return imports
    
    def _analyze_js_imports(self, file_path: Path) -> Set[str]:
        """Extract imports from JavaScript/TypeScript files"""
        imports = set()
        
        patterns = [
            # ES6 imports
            r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
            # CommonJS require
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            # Dynamic imports
            r'import\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    imports.add(match)
                    
        except Exception:
            pass
            
        return imports
    
    def _analyze_json_references(self, file_path: Path) -> Set[str]:
        """Extract file references from JSON config files"""
        references = set()
        
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Recursively find string values that look like file paths
            self._extract_path_references(data, references)
            
        except Exception:
            pass
            
        return references
    
    def _analyze_yaml_references(self, file_path: Path) -> Set[str]:
        """Extract file references from YAML files"""
        references = set()
        
        try:
            import yaml
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if data:
                self._extract_path_references(data, references)
                
        except Exception:
            pass
            
        return references
    
    def _analyze_markdown_links(self, file_path: Path) -> Set[str]:
        """Extract file links from Markdown files"""
        references = set()
        
        patterns = [
            # Standard markdown links
            r'\[.*?\]\(([^)]+)\)',
            # Reference-style links
            r'^\[.*?\]:\s*(\S+)',
            # Code blocks with file names
            r'```\w*\s*#?\s*(\S+\.\w+)',
        ]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    # Filter to local file references
                    if not match.startswith(('http://', 'https://', 'mailto:', '#')):
                        references.add(match)
                        
        except Exception:
            pass
            
        return references
    
    def _extract_path_references(self, data, references: Set[str], depth: int = 0):
        """Recursively extract path-like strings from nested data"""
        if depth > 10:  # Prevent infinite recursion
            return
            
        if isinstance(data, str):
            # Check if string looks like a file path
            if self._looks_like_path(data):
                references.add(data)
                
        elif isinstance(data, dict):
            for key, value in data.items():
                # Check keys that commonly hold file paths
                if key in {'path', 'file', 'entry_point', 'main', 'source', 'config', 'include'}:
                    if isinstance(value, str):
                        references.add(value)
                self._extract_path_references(value, references, depth + 1)
                
        elif isinstance(data, list):
            for item in data:
                self._extract_path_references(item, references, depth + 1)
    
    def _looks_like_path(self, s: str) -> bool:
        """Check if a string looks like a file path"""
        if not s or len(s) > 200:
            return False
            
        # Check for file extensions
        path_patterns = [
            r'\.\w{1,5}$',  # Has extension
            r'^\./',        # Relative path starting with ./
            r'^\.\./',      # Parent directory reference
            r'/',           # Contains directory separator
        ]
        
        return any(re.search(p, s) for p in path_patterns)
    
    def _resolve_dependencies(self, deps: Set[str], source_file: Path) -> Set[str]:
        """Resolve dependency references to actual file paths"""
        resolved = set()
        source_rel = source_file.relative_to(self.repo_path)
        
        for dep in deps:
            resolved_path = self._resolve_single_dep(dep, source_file)
            if resolved_path and resolved_path != str(source_rel):
                resolved.add(resolved_path)
                
        return resolved
    
    def _resolve_single_dep(self, dep: str, source_file: Path) -> Optional[str]:
        """Resolve a single dependency to a file path"""
        
        # Handle relative imports (Python)
        if dep.startswith('_relative:'):
            module_path = dep.replace('_relative:', '')
            if module_path in self.module_index:
                return self.module_index[module_path]
                
        # Handle relative paths (./foo, ../bar)
        if dep.startswith('.'):
            try:
                resolved = (source_file.parent / dep).resolve()
                # Try with various extensions
                for ext in ['', '.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md']:
                    candidate = Path(str(resolved) + ext)
                    if candidate.exists():
                        try:
                            return str(candidate.relative_to(self.repo_path))
                        except ValueError:
                            pass
            except Exception:
                pass
                
        # Check module index (Python modules)
        if dep in self.module_index:
            return self.module_index[dep]
            
        # Check file index
        if dep in self.file_index:
            return self.file_index[dep]
            
        # Try adding common extensions
        for ext in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md']:
            if dep + ext in self.file_index:
                return self.file_index[dep + ext]
                
        # Handle node_modules style imports (just record as external)
        # We don't resolve these as they're external dependencies
        
        return None
    
    def get_orphaned_files(
        self,
        forward_graph: Dict[str, Set[str]],
        reverse_graph: Dict[str, Set[str]],
        entry_points: Set[str]
    ) -> Set[str]:
        """
        Find orphaned files that are not reachable from any entry point.
        """
        # BFS from entry points
        visited = set()
        queue = list(entry_points)
        
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            
            # Add files this one imports
            for dep in forward_graph.get(current, set()):
                if dep not in visited:
                    queue.append(dep)
                    
        # Orphaned = all files - reachable files
        all_files = set(forward_graph.keys())
        orphaned = all_files - visited
        
        return orphaned
    
    def find_circular_dependencies(
        self,
        forward_graph: Dict[str, Set[str]]
    ) -> List[List[str]]:
        """Find circular dependencies in the graph"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in forward_graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                    return False
                    
            path.pop()
            rec_stack.remove(node)
            return False
            
        for node in forward_graph:
            if node not in visited:
                dfs(node, [])
                
        return cycles
    
    def generate_dot_graph(
        self,
        forward_graph: Dict[str, Set[str]],
        orphaned: Set[str] = None
    ) -> str:
        """Generate DOT format graph for visualization"""
        lines = ['digraph dependencies {', '  rankdir=LR;', '  node [shape=box];', '']
        
        # Add nodes with styling
        for node in forward_graph:
            style = ''
            if orphaned and node in orphaned:
                style = ' [style=filled, fillcolor=red]'
            elif node.endswith(('.py', '.js', '.ts')):
                style = ' [style=filled, fillcolor=lightblue]'
            elif node.endswith('.md'):
                style = ' [style=filled, fillcolor=lightyellow]'
            elif node.endswith('.json'):
                style = ' [style=filled, fillcolor=lightgreen]'
                
            safe_name = node.replace('/', '_').replace('.', '_').replace('-', '_')
            lines.append(f'  {safe_name} [label="{node}"]{style};')
            
        lines.append('')
        
        # Add edges
        for source, targets in forward_graph.items():
            source_safe = source.replace('/', '_').replace('.', '_').replace('-', '_')
            for target in targets:
                target_safe = target.replace('/', '_').replace('.', '_').replace('-', '_')
                lines.append(f'  {source_safe} -> {target_safe};')
                
        lines.append('}')
        return '\n'.join(lines)


if __name__ == '__main__':
    # Test the dependency graph builder
    import sys
    
    repo_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    builder = DependencyGraphBuilder(repo_path)
    
    # Find all files
    files = list(repo_path.rglob('*.py')) + list(repo_path.rglob('*.js'))
    
    forward, reverse = builder.build_graph(files)
    
    print("Forward dependencies:")
    for file, deps in sorted(forward.items()):
        if deps:
            print(f"  {file} -> {deps}")
            
    print("\nReverse dependencies:")
    for file, importers in sorted(reverse.items()):
        if importers:
            print(f"  {file} <- {importers}")
