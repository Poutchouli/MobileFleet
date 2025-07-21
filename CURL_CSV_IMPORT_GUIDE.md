# 📤 CURL CSV IMPORT - GUIDE COMPLET

## ✅ PROBLÈME RÉSOLU

L'import CSV fonctionne parfaitement ! Le problème était lié aux **contraintes de validation** des statuts.

## 🔧 UTILISATION DE CURL.EXE

### 1. **Connexion et Authentification**
```bash
# Se connecter et sauvegarder les cookies de session
curl.exe -c cookies.txt -d "username=admin&password=adminpass" -X POST http://localhost:5000/login
```

### 2. **Import CSV avec Fichier**
```bash
# Importer un fichier CSV (phones, sim_cards, ou workers)
curl.exe -b cookies.txt -F "csv_file=@test_phones.csv" -F "target_table=phones" http://localhost:5000/api/admin/import_csv
```

### 3. **Vérification des Données**
```bash
# Consulter les téléphones importés
curl.exe -b cookies.txt http://localhost:5000/api/phones
```

## 📋 FORMAT CSV REQUIS

### **Téléphones** (`target_table=phones`)
```csv
asset_tag,imei,serial_number,manufacturer,model,status
PHONE001,123456789012345,SN123456,Samsung,Galaxy S21,In Stock
PHONE002,123456789012346,SN123457,Apple,iPhone 13,In Stock
PHONE003,123456789012347,SN123458,Samsung,Galaxy Note 20,In Repair
```

### **Cartes SIM** (`target_table=sim_cards`)
```csv
iccid,carrier,plan_details,status
1234567890123456789,Verizon,Unlimited Data Plan,In Stock
1234567890123456790,AT&T,5GB Monthly Plan,In Stock
```

### **Travailleurs** (`target_table=workers`)
```csv
worker_id,full_name,secteur_id,status
WRK001,John Doe,1,Active
WRK002,Jane Smith,1,Active
```

## ⚠️ CONTRAINTES IMPORTANTES

### **Statuts Valides pour Téléphones**
- ✅ `In Stock` - Disponible en stock
- ✅ `In Use` - En cours d'utilisation
- ✅ `In Repair` - En réparation
- ❌ ~~`Defective`~~ - Non autorisé (cause d'erreur)

### **Champs Obligatoires**
- **Téléphones** : `asset_tag`, `imei`, `serial_number`, `status`
- **SIM Cards** : `iccid`, `status`
- **Workers** : `worker_id`, `full_name`, `status`

## 🚨 RÉSOLUTION D'ERREURS

### **Erreur de Contrainte**
```json
{
  "details": "new row for relation \"phones\" violates check constraint \"phones_status_check\"",
  "error": "An error occurred during CSV processing."
}
```
**Solution** : Utiliser uniquement les statuts valides (`In Stock`, `In Use`, `In Repair`)

### **Erreur d'Authentification**
```json
{
  "error": "Authentication required"
}
```
**Solution** : Vérifier que les cookies sont correctement sauvegardés et utilisés

### **Erreur de Fichier**
```json
{
  "error": "No file part"
}
```
**Solution** : Vérifier le chemin du fichier et utiliser `@` devant le nom de fichier

## 🔒 SÉCURITÉ

### **Authentification Requise**
- ✅ Connexion obligatoire avec rôle `Administrator`
- ✅ Cookies de session pour maintenir l'authentification
- ✅ Protection CSRF via session

### **Validation des Données**
- ✅ Vérification des contraintes de base de données
- ✅ Validation des champs obligatoires
- ✅ UPSERT automatique (mise à jour si existe, insertion sinon)

## 📊 RÉPONSES DE L'API

### **Succès**
```json
{
  "message": "Successfully processed 3 rows."
}
```

### **Erreur de Validation**
```json
{
  "error": "An error occurred during CSV processing.",
  "details": "Detailed PostgreSQL error message"
}
```

### **Erreur d'Autorisation**
```json
{
  "error": "Forbidden"
}
```

## 🎯 COMMANDES COMPLÈTES TESTÉES

### **Workflow Complet**
```bash
# 1. Connexion
curl.exe -c cookies.txt -d "username=admin&password=adminpass" -X POST http://localhost:5000/login

# 2. Import CSV
curl.exe -b cookies.txt -F "csv_file=@test_phones.csv" -F "target_table=phones" http://localhost:5000/api/admin/import_csv

# 3. Vérification
curl.exe -b cookies.txt http://localhost:5000/api/phones | findstr "PHONE"
```

### **Résultat Attendu**
```
{
  "message": "Successfully processed 3 rows."
}
```

## 🎉 STATUT

**L'IMPORT CSV FONCTIONNE PARFAITEMENT !**

- ✅ **Authentification** : Gestion correcte des sessions
- ✅ **Validation** : Contraintes de base de données respectées
- ✅ **Format** : CSV correctement parsé et traité
- ✅ **Sécurité** : Accès restreint aux administrateurs
- ✅ **Feedback** : Messages d'erreur et de succès clairs

Le problème n'était pas dans le code mais dans le **format des données** (statut "Defective" non autorisé).
