# test_blueprints.py
# Script de test pour valider l'architecture Blueprints

import os
import sys

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test que tous les imports fonctionnent correctement"""
    try:
        print("🔍 Test des imports...")
        
        # Test import de l'app factory
        from app import create_app
        print("✅ Import app factory: OK")
        
        # Test import des modèles
        from app.models import User, Role, Worker
        print("✅ Import models: OK")
        
        # Test import des blueprints
        from app.blueprints.auth import auth_bp
        from app.blueprints.admin import admin_bp  
        from app.blueprints.manager import manager_bp
        from app.blueprints.support import support_bp
        from app.blueprints.api import api_bp
        print("✅ Import blueprints: OK")
        
        # Test import des utilitaires
        from app.utils.decorators import login_required, role_required
        print("✅ Import decorators: OK")
        
        print("\n🎉 Tous les imports sont valides!")
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_app_creation():
    """Test la création de l'application Flask"""
    try:
        print("\n🔍 Test de création de l'app...")
        
        from app import create_app
        app = create_app()
        
        print(f"✅ App créée: {app.name}")
        print(f"✅ Blueprints enregistrés: {len(app.blueprints)}")
        
        # Lister les blueprints
        for name, blueprint in app.blueprints.items():
            print(f"   - {name}: {blueprint.url_prefix or '/'}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'app: {e}")
        return False

def test_routes():
    """Test que les routes sont bien enregistrées"""
    try:
        print("\n🔍 Test des routes...")
        
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Compter les routes
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append((rule.rule, rule.endpoint, list(rule.methods)))
            
            print(f"✅ {len(routes)} routes enregistrées")
            
            # Afficher quelques routes importantes
            important_routes = ['/login', '/admin/dashboard', '/api/sectors']
            found_routes = [route for route in routes if route[0] in important_routes]
            
            for route, endpoint, methods in found_routes:
                print(f"   - {route} -> {endpoint} [{', '.join(methods)}]")
                
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test des routes: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de l'architecture Flask Blueprints")
    print("=" * 50)
    
    success = True
    
    # Test des imports
    success &= test_imports()
    
    # Test de création de l'app
    success &= test_app_creation()
    
    # Test des routes
    success &= test_routes()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Tous les tests sont passés! L'architecture Blueprints fonctionne.")
        print("\n📝 Prochaines étapes:")
        print("   1. Migrer les routes API restantes de main.py")
        print("   2. Tester l'intégration avec Docker")
        print("   3. Mettre à jour les références dans les templates")
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return success

if __name__ == "__main__":
    main()
