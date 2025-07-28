#!/usr/bin/env python3
"""
Script pour remplacer automatiquement tous les tags d'internationalisation {{ _('...') }}
par le texte français correspondant basé sur le fichier de traduction messages.po
"""

import os
import re
import sys

# Dictionnaire des traductions depuis le fichier messages.po
translations = {
    "Fleet Management": "Gestion de Flotte",
    "Dashboard": "Tableau de Bord", 
    "Welcome": "Bienvenue",
    "Language": "Langue",
    "Account": "Compte",
    "Profile Settings": "Paramètres du Profil",
    "Sign out": "Se Déconnecter",
    "Admin Dashboard": "Tableau de Bord Équipe",
    "FleetAdmin": "Administration Flotte",
    "Phones": "Téléphones",
    "SIM Cards": "Cartes SIM",
    "Workers": "Travailleurs",
    "Users": "Utilisateurs",
    "Logout": "Déconnexion",
    "Phone Inventory": "Numéros de Téléphone",
    "Asset Tag": "Étiquette d'Actif",
    "Model": "Modèle",
    "IMEI": "IMEI",
    "Status": "Statut du Téléphone",
    "Login": "Connexion",
    "Sign in to your account": "Connectez-vous à votre compte",
    "Username": "Nom d'utilisateur",
    "Password": "Mot de passe",
    "Remember me for 30 days": "Se souvenir de moi pendant 30 jours",
    "Sign in": "Se Connecter",
    "Demo Credentials": "Identifiants de Démonstration",
    "Admin": "Administrateur",
    "Manager": "Gestionnaire",
    "Support": "Support",
    "Integration Manager": "Gestionnaire d'Intégration",
    "Profile": "Rôles",
    "Manage your account security and personal information": "Gérez la sécurité de votre compte et vos informations personnelles",
    "Personal Information": "Informations Personnelles",
    "Full Name": "Nom Complet",
    "Enter your full name": "Entrez le nom complet de l'employé",
    "Email Address": "Envoyer Email au Manager",
    "Enter your email address": "Entrez votre adresse email",
    "Update your personal information": "Gérez la sécurité de votre compte et vos informations personnelles",
    "Update Profile": "Rôles",
    "Account Details": "Étiquette d'Actif",
    "Role": "Rôles",
    "Not set": "Non défini",
    "Change Password": "Mot de passe",
    "Password must be at least 8 characters long": "Le mot de passe doit contenir au moins 8 caractères",
    "Confirm New Password": "Confirmer le Nouveau Mot de Passe",
    "Confirm your new password": "Confirmez votre nouveau mot de passe",
    "Your password will be encrypted": "Votre mot de passe sera chiffré",
    "Security Tips": "Conseils de Sécurité",
    "Use a unique password that you don't use elsewhere": "Utilisez un mot de passe unique que vous n'utilisez nulle part ailleurs",
    "Include a mix of uppercase, lowercase, numbers, and symbols": "Incluez un mélange de majuscules, minuscules, chiffres et symboles",
    "Avoid personal information like names or birthdays": "Évitez les informations personnelles comme les noms ou dates de naissance",
    "Consider using a password manager": "Considérez l'utilisation d'un gestionnaire de mots de passe",
    "Updating...": "Chargement...",
    "Network error. Please try again.": "",
    "New passwords do not match.": "",
    "New password must be at least 8 characters long.": "Le mot de passe doit contenir au moins 8 caractères",
    "Changing Password...": "Mot de passe",
    "An error occurred while changing your password.": "",
    "Passwords do not match": "",
    "Active Workers": "Travailleurs",
    "Phones In Use": "Numéros de Téléphone",
    "Phones In Stock": "Téléphones En Stock",
    "Open Tickets": "Mes Tickets",
    "Phones by Status": "Statut du Téléphone",
    "Open Tickets by Priority": "Tickets Ouverts par Priorité",
    "SIM Cards by Carrier": "Cartes SIM",
    "Workers by Sector": "Travailleurs par Secteur",
    "Assignment Trends (Last 6 Months)": "Tendances d'Attribution (6 Derniers Mois)",
    "Average Ticket Resolution Time by Priority": "Temps Moyen de Résolution des Tickets par Priorité",
    "Worker Assignments": "Nom du Travailleur",
    "Search by worker name, ID, asset...": "Rechercher par nom de travailleur, ID, actif...",
    "CSV Import Wizard": "Assistant d'Importation CSV",
    "Manage Phones": "Téléphone Assigné",
    "Provision Phone": "Téléphone Assigné",
    "Add New Phone": "Ajouter un Nouvel Utilisateur",
    "Actions": "Actions",
    "Manage Phone Requests": "Numéros de Téléphone",
    "Incoming Phone Requests": "Statut du Téléphone",
    "Worker": "Travailleurs",
    "Sector": "Secteur",
    "Date Required": "Requis",
    "Requested By": "Nouvelle Demande",
    "No phone requests found.": "Numéros de Téléphone",
    "No actions available": "Aucune action disponible",
    "Approve": "Approuver",
    "Deny": "Refuser",
    "Fulfill via Provisioning": "Réaliser via l'Approvisionnement",
    "Are you sure you want to approve this request?": "Êtes-vous sûr de vouloir approuver cette demande ?",
    "Are you sure you want to deny this request?": "Êtes-vous sûr de vouloir refuser cette demande ?",
    "Error:": "Erreur :",
    "Manage SIM Cards": "Cartes SIM",
    "SIM Card Inventory": "Numéros de Téléphone",
    "Add New SIM": "Ajouter un Nouvel Utilisateur",
    "ICCID": "ICCID",
    "Phone Number": "Numéros de Téléphone",
    "Carrier": "Opérateur",
    "Manage Users": "Gérer les Utilisateurs",
    "Manage System Users": "Gérer les Utilisateurs Système",
    "User Accounts": "Compte",
    "Add New User": "Ajouter un Nouvel Utilisateur",
    "Email": "Email",
    "Save": "Enregistrer",
    "Cancel": "Annuler",
    "Manage Workers": "Gérer les Utilisateurs",
    "Add New Worker": "Ajouter un Nouvel Utilisateur",
    "Worker ID": "Travailleurs",
    "Phone Numbers": "Numéros de Téléphone",
    "Phone Requests": "Statut du Téléphone",
    "Roles": "Rôles",
    "Assign Secteurs": "Téléphone Assigné",
    "Data Import": "Importation de Données",
    "Reports": "Rapports",
    "My Tickets": "Mes Tickets",
    "Phone Return": "Retour de Téléphone",
    "My Phone Requests": "Statut du Téléphone",
    "New Request": "Nouvelle Demande",
    "Employee Name": "Nom de l'Employé",
    "Department": "Département",
    "Position": "Poste",
    "Urgency": "Urgence",
    "Submitted": "Soumis",
    "New Phone Request": "Numéros de Téléphone",
    "Request a Phone for an Employee": "Demander un Téléphone pour un Employé",
    "Employee Full Name": "Nom Complet de l'Employé",
    "Enter employee's full name": "Entrez le nom complet de l'employé",
    "e.g., Sales, Engineering, Operations": "ex: Ventes, Ingénierie, Opérations",
    "Position/Role": "Poste/Rôle",
    "e.g., Sales Representative, Software Developer": "ex: Représentant des Ventes, Développeur de Logiciels",
    "Reason for Request": "Raison de la Demande",
    "Phone Type Preference": "Préférence de Type de Téléphone",
    "No preference": "Aucune préférence",
    "Any Android device": "N'importe quel appareil Android",
    "Basic phone": "Téléphone Assigné",
    "Urgency Level": "Niveau d'Urgence",
    "Select urgency level...": "Sélectionnez le niveau d'urgence...",
    "Low - Can wait 2+ weeks": "Faible - Peut attendre 2+ semaines",
    "Medium - Needed within 1-2 weeks": "Moyen - Nécessaire dans 1-2 semaines",
    "High - Needed within a few days": "Élevé - Nécessaire dans quelques jours",
    "Critical - Needed immediately": "Critique - Nécessaire immédiatement",
    "Submit Request": "Soumettre la Demande",
    "Create New Ticket": "Créer un Nouveau Ticket",
    "Back to My Tickets": "Mes Tickets",
    "Submit New Support Ticket": "Soumettre un Nouveau Ticket de Support",
    "Provide details about the issue you're experiencing with a device.": "Fournissez des détails sur le problème que vous rencontrez avec un appareil.",
    "Select Device": "Sélectionner l'Appareil",
    "Choose a device...": "Choisissez un appareil...",
    "Select the device that is experiencing issues.": "Sélectionnez l'appareil qui rencontre des problèmes.",
    "Ticket Title": "Titre du Ticket",
    "Brief description of the issue": "Brève description du problème",
    "Provide a clear, concise title for the issue.": "Fournissez un titre clair et concis pour le problème.",
    "Priority": "Priorité",
    "Manager Dashboard": "Tableau de Bord Manager",
    "Team Dashboard": "Tableau de Bord Équipe",
    "My Team's Status": "Statut de Mon Équipe",
    "Worker Name": "Nom du Travailleur",
    "Contract End": "Fin de Contrat",
    "ID Philia": "ID Philia",
    "Assigned Phone": "Téléphone Assigné",
    "Manager Notes": "Notes du Manager",
    "Create New Support Ticket": "Créer un Nouveau Ticket",
    "Search Worker / Phone": "Rechercher Travailleur / Téléphone",
    "Start typing worker name or asset tag...": "Commencez à taper le nom du travailleur ou le numéro d'actif...",
    "Issue Title": "Titre du Problème",
    "Low": "",
    "Medium": "IMEI",
    "High": "",
    "Urgent": "Urgence",
    "Full Description": "Description",
    "Submit Ticket": "Vos Tickets Soumis",
    "No workers found in your sectors.": "Travailleurs par Secteur",
    "N/A": "",
    "Add a note...": "Ajouter une note...",
    "Save Note": "Enregistrer Note",
    "No results found.": "Aucun résultat trouvé.",
    "Ticket Details": "Détails du Ticket",
    "Loading ticket details...": "Chargement...",
    "Error Loading Ticket": "Chargement...",
    "Device Information": "Informations du Compte",
    "Device": "Sélectionner l'Appareil",
    "Assigned To": "Téléphone Assigné",
    "Ticket Information": "Informations du Compte",
    "Created": "Créé",
    "Last Updated": "Lignes mises à jour :",
    "Description": "Description",
    "Loading your tickets...": "Chargement...",
    "Error Loading Tickets": "Erreur lors du Chargement des Tickets",
    "Filter by Status": "Filtrer par Statut",
    "All": "Tous",
    "New": "Nouveau",
    "Open": "Ouvert",
    "Pending": "En Attente",
    "On-Hold": "En Pause",
    "Solved": "Résolu",
    "Closed": "Fermé",
    "Statistics": "Statistiques",
    "Total": "Total",
    "Your Submitted Tickets": "Vos Tickets Soumis",
    "Ticket #": "Ticket #",
    "Title": "Titre",
    "No tickets found": "Aucun Ticket Trouvé",
    "You haven't submitted any tickets yet, or no tickets match the current filter.": "Vous n'avez encore soumis aucun ticket, ou aucun ticket ne correspond au filtre actuel.",
    "Create Your First Ticket": "Chargement...",
    "Support Helpdesk": "Statut du Support",
    "Active Support Tickets": "Tickets de Support Actifs",
    "Loading...": "Chargement...",
    "Refresh": "Actualiser",
    "ID": "ID",
    "Phone Asset": "Téléphones",
    "Back to Helpdesk": "Retour au Téléchargement",
    "Conversation": "Poste",
    "Add an Update": "Ajouter un Nouvel Utilisateur",
    "Your Message": "Votre Message",
    "Type your public reply or internal note here...": "Tapez votre réponse publique ou note interne ici...",
    "Make this an internal note": "Faire de ceci une note interne",
    "Post Update": "Publier la Mise à Jour",
    "Properties": "Mes Tickets",
    "Quick Actions": "Actions",
    "Log Phone Swap/Pickup": "Enregistrer Échange/Récupération de Téléphone",
    "Email Manager": "Envoyer Email au Manager",
    "Asset Details": "Étiquette d'Actif",
    "Worker History": "Travailleurs",
    "Phone Swap/Pickup Details": "Détails Échange/Récupération de Téléphone",
    "Enter details about the phone swap or pickup for the manager:": "Entrez les détails sur l'échange ou la récupération de téléphone pour le manager :",
    "Log Swap": "Enregistrer l'Échange",
    "Filters": "Filtres",
    "Filter by Sector": "Filtrer par Secteur",
    "All Sectors": "Tous les Secteurs",
    "Phone Status": "Statut du Téléphone",
    "All Statuses": "Tous les Statuts",
    "With Phone": "Avec Téléphone",
    "Without Phone": "Sans Téléphone",
    "Search Worker": "Rechercher un Travailleur",
    "Search by name...": "Rechercher par nom...",
    "Worker Status": "Statut du Travailleur",
    "Active": "Actif",
    "Inactive": "Inactif",
    "Arrêt": "Arrêt",
    "Congés": "Congés",
    "Change Status": "Changer le Statut",
    "Update": "Mettre à jour",
    "Status updated successfully!": "Statut mis à jour avec succès !"
}

def replace_translation_tags(content):
    """
    Remplace tous les tags {{ _('...') }} par les traductions françaises correspondantes
    """
    def replace_match(match):
        key = match.group(1)
        # Enlever les échappements pour les apostrophes
        key = key.replace("\\'", "'")
        
        if key in translations:
            return translations[key]
        else:
            print(f"ATTENTION: Traduction manquante pour: {key}")
            return match.group(0)  # Retourner le tag original si pas de traduction trouvée
    
    # Pattern pour capturer le contenu entre {{ _(' et ') }}
    pattern = r"{{\s*_\(['\"]([^'\"]*)['\"](?:,\s*[^)]*)*\)\s*}}"
    
    return re.sub(pattern, replace_match, content)

def process_template_file(filepath):
    """
    Traite un fichier template pour remplacer les tags d'internationalisation
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated_content = replace_translation_tags(content)
        
        if original_content != updated_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✓ Traité: {filepath}")
            return True
        else:
            print(f"- Aucun changement: {filepath}")
            return False
            
    except Exception as e:
        print(f"✗ Erreur avec {filepath}: {e}")
        return False

def main():
    templates_dir = "f:\\WORKWORK\\MobileFleet\\templates"
    processed_count = 0
    
    if not os.path.exists(templates_dir):
        print(f"Erreur: Le répertoire {templates_dir} n'existe pas")
        return
    
    print("Début du traitement des templates...")
    print("-" * 50)
    
    # Parcourir récursivement tous les fichiers .html
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if process_template_file(filepath):
                    processed_count += 1
    
    print("-" * 50)
    print(f"Traitement terminé. {processed_count} fichiers modifiés.")

if __name__ == "__main__":
    main()
