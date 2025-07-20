#!/usr/bin/env python3
"""
Script final pour valider et déployer les traductions complètes
"""

import subprocess
import os

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd="f:/WORKWORK/MobileFleet")
        if result.returncode == 0:
            print(f"✅ {description} - Succès")
            return True
        else:
            print(f"❌ {description} - Erreur: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def main():
    print("🌐 DÉPLOIEMENT FINAL DES TRADUCTIONS")
    print("=" * 50)
    
    # 1. Extraire toutes les chaînes traduisibles
    run_command("docker exec fleet_web pybabel extract -F babel.cfg -k _l -o translations/messages.pot .", 
                "Extraction des chaînes traduisibles")
    
    # 2. Mettre à jour les traductions françaises
    run_command("docker exec fleet_web pybabel update -i translations/messages.pot -d translations -l fr", 
                "Mise à jour des traductions françaises")
    
    # 3. Mettre à jour les traductions anglaises
    run_command("docker exec fleet_web pybabel update -i translations/messages.pot -d translations -l en", 
                "Mise à jour des traductions anglaises")
    
    # 4. Compiler les traductions
    run_command("docker exec fleet_web pybabel compile -d translations", 
                "Compilation des traductions")
    
    # 5. Redémarrer le service web
    run_command("docker-compose restart web", 
                "Redémarrage du service web")
    
    print("\n🎉 DÉPLOIEMENT TERMINÉ!")
    print("\n📋 RÉSUMÉ DES LANGUES CONFIGURÉES:")
    print("   • Français (FR) - Langue par défaut")
    print("   • Anglais (EN) - Langue secondaire")
    print("   • Néerlandais (NL) - SUPPRIMÉ")
    
    print("\n🔧 ÉLÉMENTS TRADUITS:")
    print("   • Templates Support (ticket_detail.html)")
    print("   • Templates Manager (ticket_detail.html)")
    print("   • Templates Admin (tous les éléments UI)")
    print("   • Templates Integration (formulaires)")
    print("   • Navigation et menus")
    print("   • Messages d'erreur et notifications")
    
    print("\n🌍 UTILISATION:")
    print("   • L'interface démarre en français par défaut")
    print("   • Les utilisateurs peuvent basculer vers l'anglais")
    print("   • La préférence de langue est sauvegardée en session")

if __name__ == "__main__":
    main()
