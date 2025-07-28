#!/usr/bin/env python3
"""
Test script to verify all Blueprint API endpoints are properly registered.
"""

def test_blueprint_endpoints():
    """Test that all Blueprint endpoints are properly registered"""
    try:
        print("\n🔍 Testing Blueprint API endpoints...")
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Get all registered routes
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append((rule.rule, rule.endpoint, list(rule.methods)))
            
            print(f"✅ Total routes registered: {len(routes)}")
            
            # Filter API routes
            api_routes = [route for route in routes if route[0].startswith('/api/')]
            print(f"✅ API routes registered: {len(api_routes)}")
            
            # Group by category
            admin_apis = [r for r in api_routes if '/admin/' in r[0] or r[1].startswith('api.') and 'admin' in r[1]]
            manager_apis = [r for r in api_routes if '/manager/' in r[0]]
            auth_apis = [r for r in api_routes if '/profile/' in r[0]]
            general_apis = [r for r in api_routes if r[0] in ['/api/sectors']]
            
            print(f"\n📊 API Endpoints by Category:")
            print(f"   🔐 Admin APIs: {len(admin_apis)}")
            print(f"   👔 Manager APIs: {len(manager_apis)}")  
            print(f"   👤 Auth APIs: {len(auth_apis)}")
            print(f"   🌐 General APIs: {len(general_apis)}")
            
            # Display key endpoints
            print(f"\n🔑 Key API Endpoints:")
            
            key_endpoints = [
                '/api/roles',
                '/api/users', 
                '/api/admin/import_csv',
                '/api/admin/all_workers_status',
                '/api/manager/team_status',
                '/api/manager/tickets',
                '/api/profile/info',
                '/api/sectors'
            ]
            
            for endpoint in key_endpoints:
                found = any(route[0] == endpoint for route in api_routes)
                status = "✅" if found else "❌"
                print(f"   {status} {endpoint}")
            
            # Test Blueprint structure
            print(f"\n🏗️  Blueprint Structure:")
            blueprints = ['auth', 'admin', 'manager', 'support', 'api']
            for bp in blueprints:
                bp_routes = [r for r in routes if r[1].startswith(f'{bp}.')]
                print(f"   📋 {bp}: {len(bp_routes)} routes")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

if __name__ == "__main__":
    success = test_blueprint_endpoints()
    if success:
        print(f"\n🎉 Blueprint API endpoints test completed successfully!")
    else:
        print(f"\n💥 Blueprint API endpoints test failed!")
