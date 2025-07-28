# Multi-Table CSV Import System

## Overview

The updated CSV import system now supports importing denormalized CSV data into the normalized database structure. Instead of importing into a single table, the system intelligently distributes data across multiple related tables within database transactions.

## How It Works

### Multi-Table Transactional Import Process

For each CSV row, the system performs the following operations within a single database transaction:

1. **Worker Management**: Finds or creates the worker record and gets their ID
2. **SIM Card Management**: Finds or creates the SIM card record and gets its ID  
3. **Phone Management**: Creates or updates the phone record
4. **Assignment Creation**: Links the phone, SIM, and worker together via the assignments table

If any step fails, the entire transaction is rolled back, ensuring data consistency.

## Expected CSV Format

Your CSV should contain denormalized data with columns for worker information, SIM details, and phone information all in one row:

### Example CSV Structure:
```csv
Nom,N° SIM,PIN,PUK,IMEI,Matériel,Asset Tag,Carrier
John Smith,1234567890123456789,1234,12345678,123456789012345,Samsung Galaxy S21,PHONE001,Verizon
Jane Doe,1234567890123456790,5678,87654321,123456789012346,iPhone 13,PHONE002,AT&T
```

## Column Mapping

When using the import wizard, you'll map your CSV columns to the following database fields:

### Worker Fields
- `name` - Worker's full name (will be stored in workers.full_name)
- `worker_id` - Optional worker ID (auto-generated if not provided)

### SIM Card Fields  
- `iccid` - The SIM card's ICCID (N° SIM in your CSV)
- `pin` - SIM PIN code
- `puk` - SIM PUK code  
- `carrier` - Mobile carrier name

### Phone Fields
- `imei` - Phone's IMEI number
- `model` - Phone model/material (Matériel in your CSV)
- `asset_tag` - Asset tag (auto-generated if not provided)
- `manufacturer` - Phone manufacturer
- `serial_number` - Phone serial number (auto-generated if not provided)
- `status` - Phone status (defaults to 'In Stock')

## Intelligent Data Handling

### Auto-Creation and Linking
- **Workers**: If a worker doesn't exist, they're automatically created
- **SIM Cards**: SIM cards are upserted (created or updated) by ICCID
- **Phones**: Phones are upserted by IMEI
- **Assignments**: Automatically created to link phone, SIM, and worker

### Default Values
- **Secteur**: Workers are assigned to a default sector if none exists
- **Asset Tags**: Auto-generated from IMEI if not provided
- **Serial Numbers**: Auto-generated from IMEI if not provided  
- **Status**: Phones default to 'In Stock', but become 'In Use' when assigned

### Conflict Resolution
- **Duplicate Workers**: Matched by full name
- **Duplicate SIMs**: Matched by ICCID, updated with new info
- **Duplicate Phones**: Matched by IMEI, updated with new info
- **Existing Assignments**: Checked to prevent duplicate assignments

## Error Handling

### Row-Level Transactions
Each CSV row is processed in its own transaction. If one row fails:
- That row is skipped and logged
- Processing continues with the next row
- No partial data corruption occurs

### Validation
- Required fields are validated
- Database constraints are enforced
- Foreign key relationships are maintained

## Usage Tips

1. **Prepare Your CSV**: Ensure your CSV has all the necessary columns with worker names, SIM ICCIDs, and phone IMEIs
2. **Column Headers**: Use clear, descriptive column headers that you can easily map
3. **Data Quality**: Clean your data beforehand - remove duplicates and ensure consistent formatting
4. **Test Small**: Start with a small CSV file to test your column mappings
5. **Review Results**: Check the import results to see how many records were inserted vs updated

## Benefits

- **No Data Loss**: All information from your denormalized CSV is preserved
- **Proper Relationships**: Data is correctly linked across tables
- **Consistency**: Database referential integrity is maintained
- **Efficiency**: Single import process handles complex multi-table operations
- **Reliability**: Transaction-based approach ensures data consistency

## Troubleshooting

### Common Issues
1. **Missing Workers**: Workers will be auto-created, but ensure names are consistent
2. **Invalid ICCIDs**: Check that SIM card ICCIDs are properly formatted
3. **Duplicate IMEIs**: Phones with duplicate IMEIs will be updated, not duplicated
4. **Missing Sectors**: A default sector will be created if none exist

### Log Files
Check the application logs for detailed error information if imports fail.
