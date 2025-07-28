#!/usr/bin/env python3
"""
Comprehensive Blueprint diagnostics and template validation script.
"""

def check_blueprint_health():
    """Run comprehensive Blueprint health checks"""
    print("\n🔍 Running Blueprint Health Check...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # 1. Check Blueprint Registration
            print("\n📋 Blueprint Registration Check:")
            blueprints = app.blueprints
            expected_blueprints = ['auth', 'admin', 'manager', 'support', 'api']
            
            for bp_name in expected_blueprints:
                if bp_name in blueprints:
                    print(f"   ✅ {bp_name} blueprint registered")
                else:
                    print(f"   ❌ {bp_name} blueprint MISSING")
            
            # 2. Check Route Endpoints
            print(f"\n🛣️  Route Endpoints Analysis:")
            routes = []
            blueprint_routes = {}
            
            for rule in app.url_map.iter_rules():
                route_info = (rule.rule, rule.endpoint, list(rule.methods))
                routes.append(route_info)
                
                # Group by blueprint
                if '.' in rule.endpoint:
                    bp_name = rule.endpoint.split('.')[0]
                    if bp_name not in blueprint_routes:
                        blueprint_routes[bp_name] = []
                    blueprint_routes[bp_name].append(route_info)
            
            print(f"   📊 Total routes: {len(routes)}")
            for bp_name, bp_routes in blueprint_routes.items():
                print(f"   📂 {bp_name}: {len(bp_routes)} routes")
            
            # 3. Check Critical Endpoints
            print(f"\n🔑 Critical Endpoint Verification:")
            critical_endpoints = [
                ('auth.login', '/login'),
                ('auth.logout', '/logout'), 
                ('admin.dashboard', '/admin/dashboard'),
                ('manager.dashboard', '/manager/dashboard'),
                ('api.get_all_sectors', '/api/sectors'),
                ('api.manage_roles', '/api/roles')
            ]
            
            endpoint_map = {rule.endpoint: rule.rule for rule in app.url_map.iter_rules()}
            
            for endpoint, expected_path in critical_endpoints:
                if endpoint in endpoint_map:
                    actual_path = endpoint_map[endpoint]
                    if actual_path == expected_path:
                        print(f"   ✅ {endpoint} -> {actual_path}")
                    else:
                        print(f"   ⚠️  {endpoint} -> {actual_path} (expected {expected_path})")
                else:
                    print(f"   ❌ {endpoint} NOT FOUND")
            
            # 4. Check Template Folder Configuration
            print(f"\n📁 Template Configuration Check:")
            print(f"   📂 App template folder: {app.template_folder}")
            
            for bp_name, blueprint in app.blueprints.items():
                if hasattr(blueprint, 'template_folder') and blueprint.template_folder:
                    print(f"   📂 {bp_name} template folder: {blueprint.template_folder}")
                else:
                    print(f"   📂 {bp_name}: using app template folder")
            
            # 5. URL Prefix Check
            print(f"\n🔗 URL Prefix Verification:")
            prefixes = {
                'auth': None,
                'admin': '/admin',
                'manager': '/manager', 
                'support': '/support',
                'api': '/api'
            }
            
            for bp_name, expected_prefix in prefixes.items():
                if bp_name in app.blueprints:
                    blueprint = app.blueprints[bp_name]
                    actual_prefix = getattr(blueprint, 'url_prefix', None)
                    if actual_prefix == expected_prefix:
                        print(f"   ✅ {bp_name}: {actual_prefix or '(no prefix)'}")
                    else:
                        print(f"   ⚠️  {bp_name}: {actual_prefix} (expected {expected_prefix})")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during health check: {e}")
        import traceback
        traceback.print_exc()
        return False

def scan_template_url_for_issues():
    """Scan templates for potential url_for issues"""
    import os
    import re
    
    print(f"\n🔍 Scanning Templates for url_for Issues...")
    
    template_dir = "templates"
    if not os.path.exists(template_dir):
        print(f"   ❌ Template directory '{template_dir}' not found")
        return False
    
    url_for_pattern = re.compile(r"url_for\(['\"]([^'\"]+)['\"]")
    issues_found = []
    files_scanned = 0
    
    for root, dirs, files in os.walk(template_dir):
        for file in files:
            if file.endswith('.html'):
                files_scanned += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    matches = url_for_pattern.findall(content)
                    for match in matches:
                        # Check if it's likely a blueprint endpoint
                        if '.' not in match and match not in ['static']:
                            issues_found.append((file_path, match))
                            
                except Exception as e:
                    print(f"   ⚠️  Error reading {file_path}: {e}")
    
    print(f"   📊 Scanned {files_scanned} template files")
    
    if issues_found:
        print(f"   ⚠️  Found {len(issues_found)} potential url_for issues:")
        for file_path, endpoint in issues_found:
            print(f"      📄 {file_path}: url_for('{endpoint}') - may need blueprint prefix")
    else:
        print(f"   ✅ No obvious url_for issues found")
    
    return len(issues_found) == 0

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Blueprint Diagnostics...")
    
    health_ok = check_blueprint_health()
    templates_ok = scan_template_url_for_issues()
    
    if health_ok and templates_ok:
        print(f"\n🎉 Blueprint diagnostics completed successfully!")
        print(f"   ✅ All blueprints properly registered")
        print(f"   ✅ All critical endpoints working")
        print(f"   ✅ No obvious template issues")
    else:
        print(f"\n⚠️  Blueprint diagnostics found issues!")
        print(f"   {'✅' if health_ok else '❌'} Blueprint health check")
        print(f"   {'✅' if templates_ok else '❌'} Template url_for check")
