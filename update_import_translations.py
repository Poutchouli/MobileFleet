#!/usr/bin/env python3
"""
Update French and Dutch translations for the CSV Import Wizard.
This script adds comprehensive translations for all import-related strings.
"""

import os
import re

def update_translations():
    # Translation mappings: English -> French -> Dutch
    translations = {
        "-- Choose a table --": ["-- Choisissez une table --", "-- Kies een tabel --"],
        "Target Table Fields:": ["Champs de la Table Cible :", "Doeltabel Velden:"],
        "Field Name": ["Nom du Champ", "Veldnaam"],
        "Data Type": ["Type de Données", "Gegevenstype"],
        "Required": ["Requis", "Vereist"],
        "Notes": ["Notes", "Opmerkingen"],
        "Note:": ["Remarque :", "Opmerking:"],
        "Primary key fields are automatically generated and don't need to be included in your CSV.": [
            "Les champs de clé primaire sont générés automatiquement et ne doivent pas être inclus dans votre CSV.",
            "Primaire sleutelvelden worden automatisch gegenereerd en hoeven niet in uw CSV te worden opgenomen."
        ],
        "Data Preview (First 5 rows):": ["Aperçu des Données (5 premières lignes) :", "Gegevensvoorbeeld (Eerste 5 rijen):"],
        "Back to Upload": ["Retour au Téléchargement", "Terug naar Upload"],
        "Proceed to Column Mapping": ["Procéder au Mappage des Colonnes", "Doorgaan naar Kolomtoewijzing"],
        "Step 3: Map CSV Columns to Database Fields": [
            "Étape 3 : Mapper les Colonnes CSV aux Champs de Base de Données",
            "Stap 3: CSV-kolommen toewijzen aan databasevelden"
        ],
        "Map each CSV column to the corresponding database field. Select one column as the merge key for data updates.": [
            "Mappez chaque colonne CSV au champ de base de données correspondant. Sélectionnez une colonne comme clé de fusion pour les mises à jour de données.",
            "Wijs elke CSV-kolom toe aan het overeenkomstige databaseveld. Selecteer één kolom als samenvoegsleutel voor gegevensupdates."
        ],
        "Auto-mapping Tips": ["Conseils de Mappage Automatique", "Auto-toewijzing Tips"],
        "Columns with similar names have been automatically matched. Review and adjust as needed.": [
            "Les colonnes avec des noms similaires ont été automatiquement appariées. Vérifiez et ajustez si nécessaire.",
            "Kolommen met vergelijkbare namen zijn automatisch gekoppeld. Controleer en pas indien nodig aan."
        ],
        "Re-run Auto-mapping": ["Relancer le Mappage Automatique", "Auto-toewijzing opnieuw uitvoeren"],
        "CSV Column": ["Colonne CSV", "CSV Kolom"],
        "Database Field": ["Champ de Base de Données", "Database Veld"],
        "Field Info": ["Info du Champ", "Veld Info"],
        "Use as Merge Key": ["Utiliser comme Clé de Fusion", "Gebruiken als Samenvoegsleutel"],
        "Back to Preview": ["Retour à l'Aperçu", "Terug naar Voorbeeld"],
        "Run Import": ["Exécuter l'Importation", "Import Uitvoeren"],
        "Step 4: Import Results": ["Étape 4 : Résultats de l'Importation", "Stap 4: Import Resultaten"],
        "Importing data, please wait...": ["Importation des données, veuillez patienter...", "Gegevens importeren, even geduld..."],
        "Primary Key (auto-generated)": ["Clé Primaire (générée automatiquement)", "Primaire Sleutel (automatisch gegenereerd)"],
        "Has default value": ["A une valeur par défaut", "Heeft standaardwaarde"],
        "Optional": ["Optionnel", "Optioneel"],
        "Do not import": ["Ne pas importer", "Niet importeren"],
        "(auto-generated)": ["(généré automatiquement)", "(automatisch gegenereerd)"],
        "No field selected": ["Aucun champ sélectionné", "Geen veld geselecteerd"],
        "Error:": ["Erreur :", "Fout:"],
        "Error fetching schema:": ["Erreur lors de la récupération du schéma :", "Fout bij ophalen schema:"],
        "The selected merge key must be mapped to a database column.": [
            "La clé de fusion sélectionnée doit être mappée à une colonne de base de données.",
            "De geselecteerde samenvoegsleutel moet worden toegewezen aan een databasekolom."
        ],
        "Rows processed:": ["Lignes traitées :", "Rijen verwerkt:"],
        "Rows inserted:": ["Lignes insérées :", "Rijen ingevoegd:"],
        "Rows updated:": ["Lignes mises à jour :", "Rijen bijgewerkt:"],
        "Start New Import": ["Commencer une Nouvelle Importation", "Nieuwe Import Starten"],
        "Go Back": ["Retourner", "Terug Gaan"]
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
    
    print("Translation update complete!")

if __name__ == "__main__":
    update_translations()
