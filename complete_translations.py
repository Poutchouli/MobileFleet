#!/usr/bin/env python3
"""
Script pour compléter automatiquement les traductions françaises manquantes
"""

import re

# Dictionnaire des traductions anglais -> français
translations = {
    "Remember me for 30 days": "Se souvenir de moi pendant 30 jours",
    "Use a unique password that you don't use elsewhere": "Utilisez un mot de passe unique que vous n'utilisez nulle part ailleurs",
    "CSV Import Wizard": "Assistant d'Importation CSV",
    "Duplicate column mapping:": "Mappage de colonne en double :",
    "All columns are set to \"Do not import\". Please map at least one column.": "Toutes les colonnes sont définies comme \"Ne pas importer\". Veuillez mapper au moins une colonne.",
    "Error during import:": "Erreur pendant l'importation :",
    "Import started...": "Importation démarrée...",
    "Import completed!": "Importation terminée !",
    "Processing rows...": "Traitement des lignes...",
    "Import Results": "Résultats de l'Importation",
    "Import was successful!": "L'importation a réussi !",
    "Import was partially successful": "L'importation a partiellement réussi",
    "Rows skipped:": "Lignes ignorées :",
    "Errors:": "Erreurs :",
    "No errors encountered.": "Aucune erreur rencontrée.",
    "Error Details:": "Détails de l'erreur :",
    "Ticket Details": "Détails du Ticket",
    "Back to Helpdesk": "Retour au Support",
    "Loading ticket details...": "Chargement des détails du ticket...",
    "Conversation": "Conversation",
    "Add an Update": "Ajouter une Mise à Jour",
    "Your Message": "Votre Message",
    "Type your public reply or internal note here...": "Tapez votre réponse publique ou note interne ici...",
    "Make this an internal note": "Faire de ceci une note interne",
    "Post Update": "Publier la Mise à Jour",
    "Properties": "Propriétés",
    "Quick Actions": "Actions Rapides",
    "Log Phone Swap/Pickup": "Enregistrer Échange/Récupération de Téléphone",
    "Email Manager": "Envoyer Email au Manager",
    "Asset Details": "Détails de l'Actif",
    "Worker History": "Historique du Travailleur",
    "Phone Swap/Pickup Details": "Détails Échange/Récupération de Téléphone",
    "Enter details about the phone swap or pickup for the manager:": "Entrez les détails sur l'échange ou la récupération de téléphone pour le manager :",
    "e.g., Replacement phone sent via courier XYZ-123 or Phone picked up by John D.": "ex: Téléphone de remplacement envoyé par coursier XYZ-123 ou Téléphone récupéré par John D.",
    "Log Swap": "Enregistrer l'Échange",
    "Error Loading Ticket": "Erreur de Chargement du Ticket",
    "Device Information": "Informations de l'Appareil",
    "Device": "Appareil",
    "Ticket Information": "Informations du Ticket",
    "Created": "Créé",
    "Last Updated": "Dernière Mise à Jour",
    "Description": "Description",
    "Enter employee's full name": "Entrez le nom complet de l'employé",
    "Please explain why this employee needs a phone (e.g., new hire, replacement, upgrade)": "Veuillez expliquer pourquoi cet employé a besoin d'un téléphone (ex: nouvelle embauche, remplacement, mise à niveau)",
    "Provide details about the issue you're experiencing with a device.": "Fournissez des détails sur le problème que vous rencontrez avec un appareil."
}

def update_translations_file(filepath):
    """Met à jour le fichier de traductions avec les nouvelles traductions"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parcourir les traductions et remplacer les msgstr vides
    for english, french in translations.items():
        # Pattern pour trouver msgid "english" suivi de msgstr ""
        pattern = fr'msgid "{re.escape(english)}"\nmsgstr ""'
        replacement = f'msgid "{english}"\nmsgstr "{french}"'
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fichier de traductions mis à jour : {filepath}")

if __name__ == "__main__":
    # Mettre à jour le fichier de traductions françaises
    update_translations_file("translations/fr/LC_MESSAGES/messages.po")
    print("Traductions françaises complétées !")
