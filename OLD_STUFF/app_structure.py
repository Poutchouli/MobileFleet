#!/usr/bin/env python3
"""
Flask App Structure Manager
Helps organize and track functions in the large Flask application
"""

import re
import os
from typing import Dict, List, Tuple

class FlaskAppAnalyzer:
    def __init__(self, app_file_path: str):
        self.app_file_path = app_file_path
        self.routes = {}
        self.functions = {}
        self.imports = []
        self.globals = []
        
    def analyze_app(self):
        """Analyze the app.py file and extract structure information"""
        with open(self.app_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._extract_imports(content)
        self._extract_routes(content)
        self._extract_functions(content)
        self._extract_globals(content)
        
    def _extract_imports(self, content: str):
        """Extract all import statements"""
        import_pattern = r'^(from .+ import .+|import .+)$'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            self.imports.append(match.group(0))
    
    def _extract_routes(self, content: str):
        """Extract all Flask routes with their details"""
        route_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)\s*\n(?:@[^\n]+\s*\n)*def\s+([^(]+)\([^)]*\):'
        
        for match in re.finditer(route_pattern, content, re.MULTILINE):
            route_path = match.group(1)
            methods = match.group(2) if match.group(2) else "['GET']"
            function_name = match.group(3)
            
            # Find function body
            start_pos = match.end()
            func_body = self._extract_function_body(content, start_pos)
            
            self.routes[function_name] = {
                'path': route_path,
                'methods': methods,
                'function_name': function_name,
                'start_line': content[:match.start()].count('\n') + 1,
                'body_preview': func_body[:200] + '...' if len(func_body) > 200 else func_body
            }
    
    def _extract_functions(self, content: str):
        """Extract all function definitions"""
        func_pattern = r'^def\s+([^(]+)\([^)]*\):'
        
        for match in re.finditer(func_pattern, content, re.MULTILINE):
            function_name = match.group(1)
            if function_name not in self.routes:  # Don't duplicate route functions
                start_pos = match.end()
                func_body = self._extract_function_body(content, start_pos)
                
                self.functions[function_name] = {
                    'function_name': function_name,
                    'start_line': content[:match.start()].count('\n') + 1,
                    'body_preview': func_body[:200] + '...' if len(func_body) > 200 else func_body
                }
    
    def _extract_function_body(self, content: str, start_pos: int) -> str:
        """Extract function body with proper indentation handling"""
        lines = content[start_pos:].split('\n')
        body_lines = []
        base_indent = None
        
        for line in lines:
            if not line.strip():  # Empty line
                body_lines.append(line)
                continue
                
            current_indent = len(line) - len(line.lstrip())
            
            if base_indent is None and line.strip():
                base_indent = current_indent
            
            if line.strip() and base_indent is not None and current_indent <= base_indent and body_lines:
                break  # End of function
                
            body_lines.append(line)
            
            if len(body_lines) > 50:  # Limit preview size
                break
        
        return '\n'.join(body_lines)
    
    def _extract_globals(self, content: str):
        """Extract global variables and configurations"""
        global_patterns = [
            r'^app\s*=\s*Flask',
            r'^app\.config\[',
            r'^[A-Z_][A-Z0-9_]*\s*=',  # Constants
        ]
        
        for pattern in global_patterns:
            for match in re.finditer(pattern, content, re.MULTILINE):
                line = content.split('\n')[content[:match.start()].count('\n')]
                self.globals.append(line.strip())
    
    def generate_structure_report(self) -> str:
        """Generate a comprehensive structure report"""
        report = []
        report.append("=" * 80)
        report.append("FLASK APPLICATION STRUCTURE ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Imports section
        report.append("IMPORTS:")
        report.append("-" * 40)
        for imp in self.imports[:10]:  # Show first 10
            report.append(f"  {imp}")
        if len(self.imports) > 10:
            report.append(f"  ... and {len(self.imports) - 10} more imports")
        report.append("")
        
        # Routes section
        report.append("ROUTES:")
        report.append("-" * 40)
        for func_name, details in self.routes.items():
            report.append(f"  {details['path']} [{details['methods']}]")
            report.append(f"    Function: {func_name}() [Line {details['start_line']}]")
            report.append(f"    Preview: {details['body_preview'][:100]}...")
            report.append("")
        
        # Functions section
        report.append("UTILITY FUNCTIONS:")
        report.append("-" * 40)
        for func_name, details in self.functions.items():
            report.append(f"  {func_name}() [Line {details['start_line']}]")
            report.append(f"    Preview: {details['body_preview'][:100]}...")
            report.append("")
        
        # Summary
        report.append("SUMMARY:")
        report.append("-" * 40)
        report.append(f"  Total Routes: {len(self.routes)}")
        report.append(f"  Total Functions: {len(self.functions)}")
        report.append(f"  Total Imports: {len(self.imports)}")
        report.append(f"  Total Global Configs: {len(self.globals)}")
        
        return '\n'.join(report)
    
    def find_route_by_path(self, path: str) -> Dict | None:
        """Find route details by path"""
        for func_name, details in self.routes.items():
            if path in details['path']:
                return details
        return None
    
    def find_function_by_name(self, name: str) -> Dict | None:
        """Find function details by name"""
        if name in self.routes:
            return self.routes[name]
        if name in self.functions:
            return self.functions[name]
        return None
    
    def get_routes_by_category(self) -> Dict[str, List]:
        """Categorize routes by their purpose"""
        categories = {
            'admin': [],
            'api': [],
            'manager': [],
            'support': [],
            'integration': [],
            'auth': [],
            'other': []
        }
        
        for func_name, details in self.routes.items():
            path = details['path']
            if '/admin' in path:
                categories['admin'].append(details)
            elif '/api' in path:
                categories['api'].append(details)
            elif '/manager' in path:
                categories['manager'].append(details)
            elif '/support' in path:
                categories['support'].append(details)
            elif '/integration' in path:
                categories['integration'].append(details)
            elif any(auth_term in path for auth_term in ['login', 'logout', 'profile']):
                categories['auth'].append(details)
            else:
                categories['other'].append(details)
        
        return categories

def main():
    """Main function to analyze the Flask app"""
    app_path = "f:\\WORKWORK\\MobileFleet\\app.py"
    
    if not os.path.exists(app_path):
        print(f"App file not found: {app_path}")
        return
    
    analyzer = FlaskAppAnalyzer(app_path)
    analyzer.analyze_app()
    
    # Generate and save structure report
    report = analyzer.generate_structure_report()
    
    with open("f:\\WORKWORK\\MobileFleet\\app_structure_report.txt", "w", encoding='utf-8') as f:
        f.write(report)
    
    print("Structure analysis complete!")
    print(f"Total routes found: {len(analyzer.routes)}")
    print(f"Total functions found: {len(analyzer.functions)}")
    
    # Show categorized routes
    categories = analyzer.get_routes_by_category()
    print("\nRoutes by category:")
    for category, routes in categories.items():
        if routes:
            print(f"  {category.upper()}: {len(routes)} routes")

if __name__ == "__main__":
    main()
