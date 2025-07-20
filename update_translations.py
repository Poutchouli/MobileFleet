#!/usr/bin/env python3
"""
Script to update French and Dutch translations for MobileFleet application
"""

# French translations for new strings
FRENCH_TRANSLATIONS = {
    "Profile": "Profil",
    "Profile Settings": "Paramètres du Profil",
    "Manage your account security and personal information": "Gérez la sécurité de votre compte et vos informations personnelles",
    "Account Information": "Informations du Compte",
    "Full Name": "Nom Complet",
    "Not set": "Non défini",
    "Email": "Email",
    "Role": "Rôle",
    "Change Password": "Changer le Mot de Passe",
    "Current Password": "Mot de Passe Actuel",
    "Enter your current password": "Entrez votre mot de passe actuel",
    "New Password": "Nouveau Mot de Passe",
    "Enter new password (min. 8 characters)": "Entrez le nouveau mot de passe (min. 8 caractères)",
    "Password must be at least 8 characters long": "Le mot de passe doit contenir au moins 8 caractères",
    "Confirm New Password": "Confirmer le Nouveau Mot de Passe",
    "Confirm your new password": "Confirmez votre nouveau mot de passe",
    "Your password will be encrypted": "Votre mot de passe sera chiffré",
    "Security Tips": "Conseils de Sécurité",
    "Use a unique password that you don't use elsewhere": "Utilisez un mot de passe unique que vous n'utilisez pas ailleurs",
    "Include a mix of uppercase, lowercase, numbers, and symbols": "Incluez un mélange de majuscules, minuscules, chiffres et symboles",
    "Avoid personal information like names or birthdays": "Évitez les informations personnelles comme les noms ou dates de naissance",
    "Consider using a password manager": "Considérez l'utilisation d'un gestionnaire de mots de passe",
    
    # Admin Dashboard
    "Admin Dashboard": "Tableau de Bord Administrateur",
    "Active Workers": "Travailleurs Actifs",
    "Phones In Use": "Téléphones En Utilisation",
    "Phones In Stock": "Téléphones En Stock",
    "Open Tickets": "Tickets Ouverts",
    "Phones by Status": "Téléphones par Statut",
    "Open Tickets by Priority": "Tickets Ouverts par Priorité",
    "SIM Cards by Carrier": "Cartes SIM par Opérateur",
    "Workers by Sector": "Travailleurs par Secteur",
    "Assignment Trends (Last 6 Months)": "Tendances d'Attribution (6 Derniers Mois)",
    "Average Ticket Resolution Time by Priority": "Temps Moyen de Résolution des Tickets par Priorité",
    "Worker Assignments": "Affectations des Travailleurs",
    "Search by worker name, ID, asset...": "Rechercher par nom de travailleur, ID, actif...",
    
    # Admin Users
    "Manage Users": "Gérer les Utilisateurs",
    "Admin": "Administrateur",
    "Manage System Users": "Gérer les Utilisateurs Système",
    "User Accounts": "Comptes Utilisateur",
    "Add New User": "Ajouter un Nouvel Utilisateur",
    "Actions": "Actions",
    "Save": "Enregistrer",
    "Cancel": "Annuler",
    
    # Main Dashboard
    "FleetAdmin": "AdministrationFlotte",
    "Admin Dashboard": "Tableau de Bord Admin",
    "Phones": "Téléphones",
    "SIM Cards": "Cartes SIM",
    "Workers": "Travailleurs",
    "Users": "Utilisateurs",
    "Welcome": "Bienvenue",
    "Logout": "Déconnexion",
    "Phone Inventory": "Inventaire des Téléphones",
    "Asset Tag": "Étiquette d'Actif",
    "Model": "Modèle",
    "IMEI": "IMEI",
    "Status": "Statut",
    
    # Integration
    "My Phone Requests": "Mes Demandes de Téléphone",
    "New Request": "Nouvelle Demande",
    "Employee Name": "Nom de l'Employé",
    "Department": "Département",
    "Position": "Poste",
    "Urgency": "Urgence",
    "Submitted": "Soumis",
    "New Phone Request": "Nouvelle Demande de Téléphone",
    "Request a Phone for an Employee": "Demander un Téléphone pour un Employé",
    "Employee Full Name": "Nom Complet de l'Employé",
    "Enter employee's full name": "Entrez le nom complet de l'employé",
    "e.g., Sales, Engineering, Operations": "ex: Ventes, Ingénierie, Opérations",
    "Position/Role": "Poste/Rôle",
    "e.g., Sales Representative, Software Developer": "ex: Représentant des Ventes, Développeur de Logiciels",
    "Reason for Request": "Raison de la Demande",
    "Please explain why this employee needs a phone (e.g., new hire, replacement, upgrade)": "Veuillez expliquer pourquoi cet employé a besoin d'un téléphone (ex: nouvelle embauche, remplacement, mise à niveau)",
    "Phone Type Preference": "Préférence de Type de Téléphone",
    "No preference": "Aucune préférence",
    "Any Android device": "N'importe quel appareil Android",
    "Basic phone": "Téléphone de base",
    "Urgency Level": "Niveau d'Urgence",
    "Select urgency level...": "Sélectionnez le niveau d'urgence...",
    "Low - Can wait 2+ weeks": "Faible - Peut attendre 2+ semaines",
    "Medium - Needed within 1-2 weeks": "Moyen - Nécessaire dans 1-2 semaines",
    "High - Needed within a few days": "Élevé - Nécessaire dans quelques jours",
    "Critical - Needed immediately": "Critique - Nécessaire immédiatement",
    "Submit Request": "Soumettre la Demande",
    
    # Support
    "Support Helpdesk": "Support Technique",
    "Active Support Tickets": "Tickets de Support Actifs",
    "Loading...": "Chargement...",
    "Refresh": "Actualiser",
    "ID": "ID",
    "Priority": "Priorité",
    "Title": "Titre",
    "Phone Asset": "Actif Téléphonique",
    
    # Manager
    "Create New Ticket": "Créer un Nouveau Ticket",
    "Back to My Tickets": "Retour à Mes Tickets",
    "Submit New Support Ticket": "Soumettre un Nouveau Ticket de Support",
    "Provide details about the issue you're experiencing with a device.": "Fournissez des détails sur le problème que vous rencontrez avec un appareil.",
    "Select Device": "Sélectionner l'Appareil",
    "Choose a device...": "Choisissez un appareil...",
    "Select the device that is experiencing issues.": "Sélectionnez l'appareil qui rencontre des problèmes.",
    "Ticket Title": "Titre du Ticket",
    "Brief description of the issue": "Brève description du problème",
    "Provide a clear, concise title for the issue.": "Fournissez un titre clair et concis pour le problème.",
    
    # Additional Admin features
    "Manage Phones": "Gérer les Téléphones",
    "Provision Phone": "Provisionner Téléphone",
    "Add New Phone": "Ajouter Nouveau Téléphone",
    "Manage Workers": "Gérer les Travailleurs",
    "Add New Worker": "Ajouter Nouveau Travailleur",
    "Worker ID": "ID Travailleur",
    "Sector": "Secteur",
    "Manage SIM Cards": "Gérer les Cartes SIM",
    "SIM Card Inventory": "Inventaire des Cartes SIM",
    "Add New SIM": "Ajouter Nouvelle SIM",
    "ICCID": "ICCID",
    "Phone Number": "Numéro de Téléphone",
    "Carrier": "Opérateur",
    
    # Loading and error states
    "Loading your tickets...": "Chargement de vos tickets...",
}

# Dutch translations for new strings  
DUTCH_TRANSLATIONS = {
    "Profile": "Profiel",
    "Profile Settings": "Profiel Instellingen",
    "Manage your account security and personal information": "Beheer uw accountbeveiliging en persoonlijke informatie",
    "Account Information": "Account Informatie",
    "Full Name": "Volledige Naam",
    "Not set": "Niet ingesteld",
    "Email": "E-mail",
    "Role": "Rol",
    "Change Password": "Wachtwoord Wijzigen",
    "Current Password": "Huidig Wachtwoord",
    "Enter your current password": "Voer uw huidige wachtwoord in",
    "New Password": "Nieuw Wachtwoord",
    "Enter new password (min. 8 characters)": "Voer nieuw wachtwoord in (min. 8 tekens)",
    "Password must be at least 8 characters long": "Wachtwoord moet minstens 8 tekens lang zijn",
    "Confirm New Password": "Bevestig Nieuw Wachtwoord",
    "Confirm your new password": "Bevestig uw nieuwe wachtwoord",
    "Your password will be encrypted": "Uw wachtwoord wordt versleuteld",
    "Security Tips": "Beveiligingstips",
    "Use a unique password that you don't use elsewhere": "Gebruik een uniek wachtwoord dat u elders niet gebruikt",
    "Include a mix of uppercase, lowercase, numbers, and symbols": "Gebruik een mix van hoofdletters, kleine letters, cijfers en symbolen",
    "Avoid personal information like names or birthdays": "Vermijd persoonlijke informatie zoals namen of verjaardagen",
    "Consider using a password manager": "Overweeg het gebruik van een wachtwoordbeheerder",
    
    # Admin Dashboard
    "Admin Dashboard": "Beheer Dashboard",
    "Active Workers": "Actieve Werknemers",
    "Phones In Use": "Telefoons in Gebruik",
    "Phones In Stock": "Telefoons op Voorraad",
    "Open Tickets": "Open Tickets",
    "Phones by Status": "Telefoons per Status",
    "Open Tickets by Priority": "Open Tickets per Prioriteit",
    "SIM Cards by Carrier": "SIM-kaarten per Provider",
    "Workers by Sector": "Werknemers per Sector",
    "Assignment Trends (Last 6 Months)": "Toewijzingstrends (Laatste 6 Maanden)",
    "Average Ticket Resolution Time by Priority": "Gemiddelde Ticket Oplossingstijd per Prioriteit",
    "Worker Assignments": "Werknemer Toewijzingen",
    "Search by worker name, ID, asset...": "Zoek op werknemersnaam, ID, middel...",
    
    # Admin Users
    "Manage Users": "Gebruikers Beheren",
    "Admin": "Beheerder",
    "Manage System Users": "Systeemgebruikers Beheren",
    "User Accounts": "Gebruikersaccounts",
    "Add New User": "Nieuwe Gebruiker Toevoegen",
    "Actions": "Acties",
    "Save": "Opslaan",
    "Cancel": "Annuleren",
    
    # Main Dashboard
    "FleetAdmin": "VlootBeheer",
    "Admin Dashboard": "Beheer Dashboard",
    "Phones": "Telefoons",
    "SIM Cards": "SIM-kaarten",
    "Workers": "Werknemers",
    "Users": "Gebruikers",
    "Welcome": "Welkom",
    "Logout": "Uitloggen",
    "Phone Inventory": "Telefoon Inventaris",
    "Asset Tag": "Middel Tag",
    "Model": "Model",
    "IMEI": "IMEI",
    "Status": "Status",
    
    # Integration
    "My Phone Requests": "Mijn Telefoon Aanvragen",
    "New Request": "Nieuwe Aanvraag",
    "Employee Name": "Werknemersnaam",
    "Department": "Afdeling",
    "Position": "Positie",
    "Urgency": "Urgentie",
    "Submitted": "Ingediend",
    "New Phone Request": "Nieuwe Telefoon Aanvraag",
    "Request a Phone for an Employee": "Vraag een Telefoon aan voor een Werknemer",
    "Employee Full Name": "Volledige Naam Werknemer",
    "Enter employee's full name": "Voer de volledige naam van de werknemer in",
    "e.g., Sales, Engineering, Operations": "bijv. Verkoop, Engineering, Operaties",
    "Position/Role": "Positie/Rol",
    "e.g., Sales Representative, Software Developer": "bijv. Vertegenwoordiger, Software Ontwikkelaar",
    "Reason for Request": "Reden voor Aanvraag",
    "Please explain why this employee needs a phone (e.g., new hire, replacement, upgrade)": "Leg uit waarom deze werknemer een telefoon nodig heeft (bijv. nieuwe werknemer, vervanging, upgrade)",
    "Phone Type Preference": "Telefoon Type Voorkeur",
    "No preference": "Geen voorkeur",
    "Any Android device": "Elk Android apparaat",
    "Basic phone": "Basis telefoon",
    "Urgency Level": "Urgentieniveau",
    "Select urgency level...": "Selecteer urgentieniveau...",
    "Low - Can wait 2+ weeks": "Laag - Kan 2+ weken wachten",
    "Medium - Needed within 1-2 weeks": "Gemiddeld - Nodig binnen 1-2 weken",
    "High - Needed within a few days": "Hoog - Nodig binnen enkele dagen",
    "Critical - Needed immediately": "Kritiek - Onmiddellijk nodig",
    "Submit Request": "Aanvraag Indienen",
    
    # Support
    "Support Helpdesk": "Support Helpdesk",
    "Active Support Tickets": "Actieve Support Tickets",
    "Loading...": "Laden...",
    "Refresh": "Vernieuwen",
    "ID": "ID",
    "Priority": "Prioriteit",
    "Title": "Titel",
    "Phone Asset": "Telefoon Middel",
    
    # Manager
    "Create New Ticket": "Nieuw Ticket Aanmaken",
    "Back to My Tickets": "Terug naar Mijn Tickets",
    "Submit New Support Ticket": "Nieuw Support Ticket Indienen",
    "Provide details about the issue you're experiencing with a device.": "Geef details over het probleem dat u ervaart met een apparaat.",
    "Select Device": "Selecteer Apparaat",
    "Choose a device...": "Kies een apparaat...",
    "Select the device that is experiencing issues.": "Selecteer het apparaat dat problemen ondervindt.",
    "Ticket Title": "Ticket Titel",
    "Brief description of the issue": "Korte beschrijving van het probleem",
    "Provide a clear, concise title for the issue.": "Geef een duidelijke, beknopte titel voor het probleem.",
    
    # Additional Admin features
    "Manage Phones": "Telefoons Beheren",
    "Provision Phone": "Telefoon Inrichten",
    "Add New Phone": "Nieuwe Telefoon Toevoegen",
    "Manage Workers": "Werknemers Beheren", 
    "Add New Worker": "Nieuwe Werknemer Toevoegen",
    "Worker ID": "Werknemer ID",
    "Sector": "Sector",
    "Manage SIM Cards": "SIM-kaarten Beheren",
    "SIM Card Inventory": "SIM-kaart Inventaris",
    "Add New SIM": "Nieuwe SIM Toevoegen",
    "ICCID": "ICCID",
    "Phone Number": "Telefoonnummer",
    "Carrier": "Provider",
    
    # Loading and error states
    "Loading your tickets...": "Uw tickets laden...",
}

def update_po_file(filepath, translations):
    """Update a .po file with new translations"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for english, translation in translations.items():
        # Look for the English msgid and replace the empty msgstr
        english_escaped = english.replace('"', '\\"').replace("'", "\\'")
        pattern = f'msgid "{english_escaped}"\nmsgstr ""'
        replacement = f'msgid "{english_escaped}"\nmsgstr "{translation}"'
        content = content.replace(pattern, replacement)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated {filepath}")

if __name__ == "__main__":
    # Update French translations
    update_po_file("translations/fr/LC_MESSAGES/messages.po", FRENCH_TRANSLATIONS)
    
    # Update Dutch translations  
    update_po_file("translations/nl/LC_MESSAGES/messages.po", DUTCH_TRANSLATIONS)
    
    print("Translation files updated successfully!")
