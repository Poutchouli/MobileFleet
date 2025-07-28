#!/usr/bin/env python3
"""
Function Search and Management CLI Tool
Quick way to find, view, and modify functions in the Flask app
"""

import sys
import json
from function_manager import FunctionManager

def print_help():
    """Print help information"""
    print("""
🔧 Flask Function Manager CLI

Commands:
  search <pattern>     - Search for functions by name or route
  show <function>      - Show function details and source
  list <category>      - List all functions in a category
  categories          - Show all categories
  routes              - List all routes
  stats               - Show function statistics
  help                - Show this help

Categories: admin, api, auth, integration, manager, support, utils, other

Examples:
  python cli.py search login
  python cli.py show get_manager_tickets
  python cli.py list admin
  python cli.py routes
    """)

def search_functions(manager, pattern):
    """Search for functions by pattern"""
    pattern_lower = pattern.lower()
    matches = []
    
    for func_name, func_info in manager.functions.items():
        if (pattern_lower in func_name.lower() or 
            (func_info.route_path and pattern_lower in func_info.route_path.lower()) or
            pattern_lower in func_info.description.lower()):
            matches.append(func_info)
    
    if matches:
        print(f"\n🔍 Found {len(matches)} matches for '{pattern}':")
        print("-" * 60)
        for func in sorted(matches, key=lambda x: x.name):
            role_str = f" [{func.role_required}]" if func.role_required else ""
            route_str = f" -> {func.route_path}" if func.route_path else ""
            print(f"📍 {func.name}(){role_str}{route_str}")
            print(f"   📄 {func.description[:80]}...")
            print(f"   📍 Lines {func.line_start}-{func.line_end}")
            print()
    else:
        print(f"❌ No functions found matching '{pattern}'")

def show_function(manager, func_name):
    """Show detailed function information"""
    func_info = manager.get_function_by_name(func_name)
    if not func_info:
        print(f"❌ Function '{func_name}' not found")
        return
    
    print(f"\n📍 Function: {func_info.name}")
    print("=" * 60)
    print(f"📂 Category: {func_info.category}")
    print(f"📍 Lines: {func_info.line_start}-{func_info.line_end}")
    
    if func_info.route_path:
        methods_str = ', '.join(func_info.methods)
        print(f"🌐 Route: {func_info.route_path} [{methods_str}]")
    
    if func_info.role_required:
        print(f"🔒 Role Required: {func_info.role_required}")
    
    if func_info.parameters:
        params_str = ', '.join(func_info.parameters)
        print(f"📝 Parameters: {params_str}")
    
    print(f"📤 Returns: {func_info.returns}")
    print(f"📄 Description: {func_info.description}")
    
    # Show source code
    print("\n💻 Source Code:")
    print("-" * 60)
    source = manager.get_function_source(func_name)
    if source:
        lines = source.split('\n')
        for i, line in enumerate(lines[:30], func_info.line_start):  # Show first 30 lines
            print(f"{i:4d}: {line}")
        if len(lines) > 30:
            print(f"     ... ({len(lines) - 30} more lines)")
    else:
        print("❌ Could not retrieve source code")

def list_category(manager, category):
    """List all functions in a category"""
    funcs = manager.get_functions_by_category(category)
    if funcs:
        print(f"\n📂 {category.upper()} Functions ({len(funcs)} total):")
        print("-" * 60)
        for func in sorted(funcs, key=lambda x: x.name):
            route_str = f" -> {func.route_path}" if func.route_path else ""
            role_str = f" [{func.role_required}]" if func.role_required else ""
            print(f"📍 {func.name}(){role_str}{route_str}")
            print(f"   📍 Lines {func.line_start}-{func.line_end}")
            print(f"   📄 {func.description[:60]}...")
            print()
    else:
        print(f"❌ No functions found in category '{category}'")

def show_categories(manager):
    """Show all categories with counts"""
    categories = {}
    for func in manager.functions.values():
        categories[func.category] = categories.get(func.category, 0) + 1
    
    print("\n📂 Function Categories:")
    print("-" * 30)
    for category, count in sorted(categories.items()):
        print(f"📁 {category:12} {count:3d} functions")

def show_routes(manager):
    """Show all routes"""
    routes = [(func.route_path, func.name, func.methods, func.role_required) 
              for func in manager.functions.values() if func.route_path]
    
    print(f"\n🌐 All Routes ({len(routes)} total):")
    print("-" * 80)
    for route_path, func_name, methods, role in sorted(routes):
        methods_str = ', '.join(methods)
        role_str = f" [{role}]" if role else ""
        print(f"{route_path:40} {methods_str:15} -> {func_name}(){role_str}")

def show_stats(manager):
    """Show function statistics"""
    total = len(manager.functions)
    routes = len([f for f in manager.functions.values() if f.route_path])
    utils = len([f for f in manager.functions.values() if not f.route_path])
    
    # Count by role
    roles = {}
    for func in manager.functions.values():
        role = func.role_required or 'Public'
        roles[role] = roles.get(role, 0) + 1
    
    # Count by category
    categories = {}
    for func in manager.functions.values():
        categories[func.category] = categories.get(func.category, 0) + 1
    
    print(f"\n📊 Function Statistics:")
    print("=" * 40)
    print(f"📈 Total Functions: {total}")
    print(f"🌐 Route Functions: {routes}")
    print(f"🔧 Utility Functions: {utils}")
    print()
    
    print("👥 By Role:")
    for role, count in sorted(roles.items()):
        print(f"   {role:20} {count:3d}")
    print()
    
    print("📂 By Category:")
    for category, count in sorted(categories.items()):
        print(f"   {category:20} {count:3d}")

def main():
    """Main CLI function"""
    if len(sys.argv) < 2:
        print_help()
        return
    
    # Initialize function manager
    app_path = "f:\\WORKWORK\\MobileFleet\\app.py"
    manager = FunctionManager(app_path)
    manager.analyze_functions()
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        print_help()
    
    elif command == 'search':
        if len(sys.argv) < 3:
            print("❌ Please provide a search pattern")
            return
        search_functions(manager, sys.argv[2])
    
    elif command == 'show':
        if len(sys.argv) < 3:
            print("❌ Please provide a function name")
            return
        show_function(manager, sys.argv[2])
    
    elif command == 'list':
        if len(sys.argv) < 3:
            print("❌ Please provide a category name")
            return
        list_category(manager, sys.argv[2])
    
    elif command == 'categories':
        show_categories(manager)
    
    elif command == 'routes':
        show_routes(manager)
    
    elif command == 'stats':
        show_stats(manager)
    
    else:
        print(f"❌ Unknown command: {command}")
        print_help()

if __name__ == "__main__":
    main()
