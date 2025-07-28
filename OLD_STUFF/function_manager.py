#!/usr/bin/env python3
"""
Flask Function Manager - Advanced function tracking and modification system
"""

import re
import os
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class FunctionInfo:
    name: str
    route_path: Optional[str]
    methods: List[str]
    line_start: int
    line_end: int
    category: str
    role_required: Optional[str]
    description: str
    parameters: List[str]
    returns: str
    
class FunctionManager:
    def __init__(self, app_file_path: str):
        self.app_file_path = app_file_path
        self.functions: Dict[str, FunctionInfo] = {}
        self.categories = {
            'auth': ['login', 'logout', 'profile', 'change_password'],
            'admin': ['admin_', 'handle_', 'provision_', 'import_'],
            'manager': ['manager_', 'get_manager_'],
            'support': ['support_', 'get_all_', 'get_ticket_', 'add_ticket_'],
            'integration': ['integration_', 'get_integration_', 'create_phone_request'],
            'api': ['api/', 'handle_', 'get_', 'create_', 'update_', 'delete_'],
            'reports': ['get_.*_report', 'get_.*_stats', 'get_dashboard_'],
            'utils': ['get_db', 'log_event', 'role_required', 'login_required']
        }
        
    def analyze_functions(self):
        """Analyze all functions in the app file"""
        with open(self.app_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find all route decorators and their functions
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check for route decorator
            route_match = re.match(r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)', line)
            if route_match:
                route_path = route_match.group(1)
                methods_str = route_match.group(2) if route_match.group(2) else "'GET'"
                methods = [m.strip().strip("'\"") for m in methods_str.split(',')]
                
                # Look for decorators and function definition
                j = i + 1
                role_required = None
                while j < len(lines) and not lines[j].strip().startswith('def '):
                    decorator_line = lines[j].strip()
                    role_match = re.match(r'@role_required\([\'"]([^\'"]+)[\'"]\)', decorator_line)
                    if role_match:
                        role_required = role_match.group(1)
                    j += 1
                
                # Find function definition
                if j < len(lines):
                    func_match = re.match(r'def\s+([^(]+)\([^)]*\):', lines[j].strip())
                    if func_match:
                        func_name = func_match.group(1)
                        line_start = j + 1
                        
                        # Find function end
                        line_end = self._find_function_end(lines, j)
                        
                        # Extract function details
                        description = self._extract_docstring(lines, j)
                        parameters = self._extract_parameters(lines[j])
                        returns = self._extract_return_type(lines, j, line_end)
                        category = self._categorize_function(func_name, route_path)
                        
                        func_info = FunctionInfo(
                            name=func_name,
                            route_path=route_path,
                            methods=methods,
                            line_start=line_start,
                            line_end=line_end,
                            category=category,
                            role_required=role_required,
                            description=description,
                            parameters=parameters,
                            returns=returns
                        )
                        
                        self.functions[func_name] = func_info
                
                i = j
            else:
                # Check for standalone functions (no route decorator)
                func_match = re.match(r'def\s+([^(]+)\([^)]*\):', line)
                if func_match and not line.startswith(' '):  # Top-level function
                    func_name = func_match.group(1)
                    line_start = i + 1
                    line_end = self._find_function_end(lines, i)
                    
                    description = self._extract_docstring(lines, i)
                    parameters = self._extract_parameters(lines[i])
                    returns = self._extract_return_type(lines, i, line_end)
                    category = self._categorize_function(func_name, None)
                    
                    func_info = FunctionInfo(
                        name=func_name,
                        route_path=None,
                        methods=[],
                        line_start=line_start,
                        line_end=line_end,
                        category=category,
                        role_required=None,
                        description=description,
                        parameters=parameters,
                        returns=returns
                    )
                    
                    self.functions[func_name] = func_info
                
                i += 1
    
    def _find_function_end(self, lines: List[str], start_idx: int) -> int:
        """Find the end line of a function"""
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                return i - 1
        
        return len(lines) - 1
    
    def _extract_docstring(self, lines: List[str], func_start: int) -> str:
        """Extract function docstring"""
        for i in range(func_start + 1, min(func_start + 5, len(lines))):
            line = lines[i].strip()
            if line.startswith('"""') or line.startswith("'''"):
                # Found docstring start
                if line.count('"""') == 2 or line.count("'''") == 2:
                    # Single line docstring
                    return line.strip('"""').strip("'''").strip()
                else:
                    # Multi-line docstring
                    docstring_lines = [line.strip('"""').strip("'''")]
                    quote_type = '"""' if '"""' in line else "'''"
                    
                    for j in range(i + 1, min(i + 10, len(lines))):
                        doc_line = lines[j].strip()
                        if quote_type in doc_line:
                            docstring_lines.append(doc_line.replace(quote_type, ''))
                            break
                        docstring_lines.append(doc_line)
                    
                    return ' '.join(docstring_lines).strip()
        
        return "No description available"
    
    def _extract_parameters(self, func_line: str) -> List[str]:
        """Extract function parameters"""
        match = re.match(r'def\s+[^(]+\(([^)]*)\):', func_line)
        if match:
            params_str = match.group(1)
            if params_str.strip():
                params = [p.strip() for p in params_str.split(',')]
                return [p for p in params if p and p != 'self']
        return []
    
    def _extract_return_type(self, lines: List[str], start: int, end: int) -> str:
        """Extract return type information"""
        for i in range(start, min(end, start + 20)):
            line = lines[i]
            if 'return ' in line:
                if 'jsonify' in line:
                    return 'JSON'
                elif 'render_template' in line:
                    return 'HTML'
                elif 'redirect' in line:
                    return 'Redirect'
        return 'Unknown'
    
    def _categorize_function(self, func_name: str, route_path: Optional[str]) -> str:
        """Categorize function based on name and route"""
        func_lower = func_name.lower()
        path_lower = route_path.lower() if route_path else ''
        
        for category, patterns in self.categories.items():
            for pattern in patterns:
                if re.search(pattern.lower(), func_lower) or re.search(pattern.lower(), path_lower):
                    return category
        
        return 'other'
    
    def get_functions_by_category(self, category: str) -> List[FunctionInfo]:
        """Get all functions in a specific category"""
        return [func for func in self.functions.values() if func.category == category]
    
    def get_function_by_name(self, name: str) -> Optional[FunctionInfo]:
        """Get function info by name"""
        return self.functions.get(name)
    
    def find_functions_by_route(self, route_pattern: str) -> List[FunctionInfo]:
        """Find functions by route pattern"""
        pattern = re.compile(route_pattern, re.IGNORECASE)
        return [func for func in self.functions.values() 
                if func.route_path and pattern.search(func.route_path)]
    
    def get_function_source(self, func_name: str) -> Optional[str]:
        """Get the source code of a function"""
        func_info = self.get_function_by_name(func_name)
        if not func_info:
            return None
        
        with open(self.app_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get function lines (accounting for 0-based indexing)
        start_idx = func_info.line_start - 1
        end_idx = func_info.line_end
        
        return ''.join(lines[start_idx:end_idx])
    
    def replace_function(self, func_name: str, new_source: str) -> bool:
        """Replace a function with new source code"""
        func_info = self.get_function_by_name(func_name)
        if not func_info:
            return False
        
        with open(self.app_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the start of the function (including decorators)
        actual_start = func_info.line_start - 1
        
        # Look backwards for decorators
        for i in range(func_info.line_start - 2, -1, -1):
            line = lines[i].strip()
            if line.startswith('@') or line == '':
                actual_start = i
            else:
                break
        
        # Replace the function
        new_lines = lines[:actual_start] + [new_source + '\n'] + lines[func_info.line_end:]
        
        # Backup original file
        backup_path = f"{self.app_file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Write new content
        with open(self.app_file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        # Re-analyze to update line numbers
        self.analyze_functions()
        
        return True
    
    def generate_function_index(self) -> str:
        """Generate a comprehensive function index"""
        report = []
        report.append("=" * 100)
        report.append("FLASK APPLICATION FUNCTION INDEX")
        report.append("=" * 100)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Functions: {len(self.functions)}")
        report.append("")
        
        # Group by category
        categories = {}
        for func in self.functions.values():
            if func.category not in categories:
                categories[func.category] = []
            categories[func.category].append(func)
        
        for category, funcs in sorted(categories.items()):
            report.append(f"\n{category.upper()} FUNCTIONS ({len(funcs)} functions)")
            report.append("-" * 80)
            
            for func in sorted(funcs, key=lambda x: x.name):
                report.append(f"📍 {func.name}() [Lines {func.line_start}-{func.line_end}]")
                
                if func.route_path:
                    methods_str = ', '.join(func.methods)
                    report.append(f"   🌐 Route: {func.route_path} [{methods_str}]")
                
                if func.role_required:
                    report.append(f"   🔒 Role: {func.role_required}")
                
                if func.parameters:
                    params_str = ', '.join(func.parameters)
                    report.append(f"   📝 Params: {params_str}")
                
                report.append(f"   📄 Description: {func.description}")
                report.append(f"   📤 Returns: {func.returns}")
                report.append("")
        
        # Quick reference section
        report.append("\nQUICK REFERENCE")
        report.append("-" * 80)
        report.append("Route Functions:")
        for func in sorted(self.functions.values(), key=lambda x: x.route_path or ''):
            if func.route_path:
                report.append(f"  {func.route_path:40} -> {func.name}()")
        
        return '\n'.join(report)
    
    def save_index(self, output_path: str):
        """Save function index to file"""
        index_content = self.generate_function_index()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
    
    def export_json(self, output_path: str):
        """Export function data as JSON"""
        data = {
            'generated': datetime.now().isoformat(),
            'total_functions': len(self.functions),
            'functions': {name: asdict(func) for name, func in self.functions.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

def main():
    """Main function to run the function manager"""
    app_path = "f:\\WORKWORK\\MobileFleet\\app.py"
    
    if not os.path.exists(app_path):
        print(f"App file not found: {app_path}")
        return
    
    manager = FunctionManager(app_path)
    manager.analyze_functions()
    
    # Generate comprehensive index
    manager.save_index("f:\\WORKWORK\\MobileFleet\\function_index.txt")
    manager.export_json("f:\\WORKWORK\\MobileFleet\\function_index.json")
    
    print(f"✅ Function analysis complete!")
    print(f"📊 Found {len(manager.functions)} functions")
    
    # Show category breakdown
    categories = {}
    for func in manager.functions.values():
        categories[func.category] = categories.get(func.category, 0) + 1
    
    print("\n📋 Functions by category:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} functions")
    
    # Show some examples
    print("\n🔍 Example function lookup:")
    admin_funcs = manager.get_functions_by_category('admin')
    if admin_funcs:
        func = admin_funcs[0]
        print(f"   Function: {func.name}")
        print(f"   Route: {func.route_path}")
        print(f"   Lines: {func.line_start}-{func.line_end}")

if __name__ == "__main__":
    main()
