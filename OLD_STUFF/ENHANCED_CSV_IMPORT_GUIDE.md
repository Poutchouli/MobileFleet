# Enhanced CSV Import Guide

## Access the Import Page
- **URL**: `http://localhost:5000/admin/csv-import`
- **Required Role**: Administrator
- **Login**: Use admin credentials (username: `admin`, password: `adminpass`)

## CSV File Format

### Required Headers (in exact order):
```
Num SAL;Nom;Domaine d'Intervention;Contrat;Date Dernier contrat;N° SIM;OP;PUK;NUMERO;RIO;IMEI Téléphone (*#06#);Matèriel
```

### Field Descriptions:
- **Num SAL**: Worker ID (unique identifier)
- **Nom**: Worker full name
- **Domaine d'Intervention**: Sector/Department name
- **Contrat**: Contract type (CDI, CDD, etc.)
- **Date Dernier contrat**: Last contract date (YYYY-MM-DD format)
- **N° SIM**: SIM card ICCID (unique)
- **OP**: Carrier/Operator name
- **PUK**: SIM card PUK code
- **NUMERO**: Phone number
- **RIO**: RIO code (optional)
- **IMEI Téléphone (*#06#)**: Phone IMEI (unique)
- **Matèriel**: Phone model/material

### File Requirements:
- **Delimiter**: Semicolon (;)
- **Encoding**: UTF-8
- **Extension**: .csv

## What Gets Created:

### 1. Secteurs (Departments)
- Creates or finds sectors by name
- Links workers to appropriate sectors

### 2. Workers 
- Creates workers with contract information
- Links to sectors
- Stores contract type and last contract date

### 3. SIM Cards
- Creates SIM cards with carrier and PUK information
- Stores in proper `puk` column (not plan_details)

### 4. Phone Numbers
- Creates phone numbers linked to SIM cards
- Stores RIO codes when provided

### 5. Phones
- Creates phones with model information
- Links to workers and SIM cards via foreign keys
- Auto-generates asset tags and serial numbers if not provided

### 6. Relationships
- Automatically creates proper foreign key relationships
- Updates phone status to 'In Use' when assigned
- Updates SIM status to 'In Use' when assigned

## Test File
Use the provided `test_enhanced_import.csv` for testing:
- Contains 3 test records
- Demonstrates all field types including optional RIO
- Shows different contract types and sectors

## Import Process
1. Select your CSV file
2. Click "Import CSV Data" 
3. Wait for processing (shows progress)
4. Review results summary:
   - New records created
   - Existing records updated  
   - Any errors encountered

## Error Handling
- Each row processed in its own transaction
- Failed rows don't affect successful ones
- Detailed error messages provided for troubleshooting
- Duplicate detection via unique constraints (worker_id, iccid, imei, phone_number)

## Post-Import Verification
Check the following admin pages to verify import:
- `/admin/workers` - Worker records
- `/admin/phones` - Phone inventory
- `/admin/sims` - SIM card inventory
- Database relationships will be automatically established
