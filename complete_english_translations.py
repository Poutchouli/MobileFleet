#!/usr/bin/env python3
"""
Script pour préparer les traductions anglaises (les termes restent en anglais)
"""

import re

def update_english_translations(filepath):
    """Met à jour le fichier de traductions anglaises (termes identiques)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern pour trouver msgid suivi de msgstr ""
    pattern = r'msgid "([^"]+)"\nmsgstr ""'
    
    def replacement(match):
        msgid_text = match.group(1)
        return f'msgid "{msgid_text}"\nmsgstr "{msgid_text}"'
    
    content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fichier de traductions anglaises mis à jour : {filepath}")

if __name__ == "__main__":
    # Mettre à jour le fichier de traductions anglaises
    update_english_translations("translations/en/LC_MESSAGES/messages.po")
    print("Traductions anglaises préparées !")
