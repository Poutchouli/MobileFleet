#!/usr/bin/env python3
"""
Update French and Dutch translations for the Phone Request Management feature.
This script adds comprehensive translations for all phone request related strings.
"""

import os
import re

def update_phone_request_translations():
    # Translation mappings: English -> French -> Dutch
    translations = {
        "Manage Phone Requests": ["Gérer les Demandes de Téléphone", "Telefoonverzoeken Beheren"],
        "Phone Requests": ["Demandes de Téléphone", "Telefoonverzoeken"],
        "Incoming Phone Requests": ["Demandes de Téléphone Entrantes", "Binnenkomende Telefoonverzoeken"],
        "Worker": ["Travailleur", "Werknemer"],
        "Sector": ["Secteur", "Sector"],
        "Date Required": ["Date Requise", "Vereiste Datum"],
        "Requested By": ["Demandé Par", "Aangevraagd Door"],
        "Status": ["Statut", "Status"],
        "Actions": ["Actions", "Acties"],
        "No phone requests found.": ["Aucune demande de téléphone trouvée.", "Geen telefoonverzoeken gevonden."],
        "No actions available": ["Aucune action disponible", "Geen acties beschikbaar"],
        "Approve": ["Approuver", "Goedkeuren"],
        "Deny": ["Refuser", "Weigeren"],
        "Fulfill via Provisioning": ["Réaliser via l'Approvisionnement", "Uitvoeren via Provisioning"],
        "Are you sure you want to approve this request?": [
            "Êtes-vous sûr de vouloir approuver cette demande ?",
            "Weet u zeker dat u dit verzoek wilt goedkeuren?"
        ],
        "Are you sure you want to deny this request?": [
            "Êtes-vous sûr de vouloir refuser cette demande ?",
            "Weet u zeker dat u dit verzoek wilt weigeren?"
        ]
    }
    
    # Update French translations
    fr_file = "translations/fr/LC_MESSAGES/messages.po"
    nl_file = "translations/nl/LC_MESSAGES/messages.po"
    
    for lang_idx, file_path in enumerate([fr_file, nl_file]):
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found")
            continue
            
        print(f"Updating {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update translations
        for english, translations_list in translations.items():
            if lang_idx < len(translations_list):
                translated = translations_list[lang_idx]
                
                # Find the msgid and update the corresponding msgstr
                pattern = rf'msgid "{re.escape(english)}"\s*msgstr ""'
                replacement = f'msgid "{english}"\nmsgstr "{translated}"'
                content = re.sub(pattern, replacement, content)
                
                # Also handle already existing translations that might be empty
                pattern = rf'(msgid "{re.escape(english)}"\s*msgstr) ""'
                replacement = rf'\1 "{translated}"'
                content = re.sub(pattern, replacement, content)
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {len(translations)} translations in {file_path}")
    
    print("Phone request translation update complete!")

if __name__ == "__main__":
    update_phone_request_translations()
