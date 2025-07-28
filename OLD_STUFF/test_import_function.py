#!/usr/bin/env python3
"""Test script to verify the import_process function logic"""

import psycopg2
import psycopg2.extras
import csv
import io
import json

# Database connection
def get_test_db():
    return psycopg2.connect(
        host="localhost",
        port="5433",
        database="fleet_db", 
        user="postgres",
        password="password",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

def test_import_logic():
    """Test the core import logic without Flask"""
    
    # Sample CSV data with semicolon delimiter
    csv_data = """Nom;N° SIM;PIN;PUK;IMEI;Matériel;Asset Tag;Carrier;Status
Alice Semicolon;1234567890123456800;1111;11111111;123456789012400;Samsung Galaxy S22;PHONE100;Orange;In Stock"""
    
    # Column mappings
    mappings = {
        "name": "Nom",
        "iccid": "N° SIM", 
        "pin": "PIN",
        "puk": "PUK",
        "imei": "IMEI",
        "model": "Matériel",
        "asset_tag": "Asset Tag",
        "carrier": "Carrier",
        "status": "Status"
    }
    
    print("Connecting to database...")
    db = get_test_db()
    
    try:
        # Test with semicolon delimiter
        reader = csv.DictReader(io.StringIO(csv_data), delimiter=';')
        
        inserted_count = 0
        updated_count = 0
        error_count = 0
        
        print("Processing CSV rows with semicolon delimiter...")
        for row_index, row in enumerate(reader):
            print(f"Processing row {row_index + 1}: {row}")
            
            try:
                cursor = db.cursor()
                
                # Step 1: Upsert Worker
                worker_name_csv = mappings.get('name')
                worker_id = None
                if worker_name_csv and row.get(worker_name_csv):
                    worker_name = row[worker_name_csv].strip()
                    if worker_name:
                        print(f"  Processing worker: {worker_name}")
                        
                        # Check if worker exists
                        cursor.execute("SELECT id FROM workers WHERE full_name = %s", (worker_name,))
                        worker_result = cursor.fetchone()
                        if worker_result:
                            worker_id = worker_result['id']
                            print(f"    Found existing worker with ID: {worker_id}")
                        else:
                            # Create worker
                            cursor.execute("SELECT id FROM secteurs LIMIT 1")
                            secteur_result = cursor.fetchone()
                            if not secteur_result:
                                cursor.execute(
                                    "INSERT INTO secteurs (secteur_name, description) VALUES (%s, %s) RETURNING id",
                                    ('Default Sector', 'Auto-created during CSV import')
                                )
                                secteur_id = cursor.fetchone()['id']
                                print(f"    Created default sector with ID: {secteur_id}")
                            else:
                                secteur_id = secteur_result['id']
                            
                            worker_code = f"WK{worker_name.replace(' ', '').upper()[:6]}"
                            cursor.execute(
                                "INSERT INTO workers (worker_id, full_name, secteur_id, status) VALUES (%s, %s, %s, %s) RETURNING id",
                                (worker_code, worker_name, secteur_id, 'Active')
                            )
                            worker_id = cursor.fetchone()['id']
                            print(f"    Created new worker with ID: {worker_id}")
                
                # Step 2: Upsert SIM Card
                iccid_csv = mappings.get('iccid')
                sim_id = None
                if iccid_csv and row.get(iccid_csv):
                    iccid = row[iccid_csv].strip()
                    if iccid:
                        print(f"  Processing SIM: {iccid}")
                        carrier = row.get(mappings.get('carrier', ''), '').strip() or None
                        pin = row.get(mappings.get('pin', ''), '').strip() or None
                        puk = row.get(mappings.get('puk', ''), '').strip() or None
                        
                        cursor.execute("""
                            INSERT INTO sim_cards (iccid, carrier, plan_details, status)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (iccid) DO UPDATE SET
                                carrier = EXCLUDED.carrier,
                                plan_details = EXCLUDED.plan_details,
                                status = EXCLUDED.status
                            RETURNING id;
                        """, (iccid, carrier, f"PIN: {pin}, PUK: {puk}" if pin or puk else None, 'In Stock'))
                        sim_id = cursor.fetchone()['id']
                        print(f"    Processed SIM with ID: {sim_id}")
                
                # Step 3: Upsert Phone
                imei_csv = mappings.get('imei')
                phone_id = None
                if imei_csv and row.get(imei_csv):
                    imei = row[imei_csv].strip()
                    if imei:
                        print(f"  Processing phone: {imei}")
                        
                        asset_tag = row.get(mappings.get('asset_tag'), '').strip() or f"PHONE_{imei[-6:]}"
                        serial_number = f"SN_{imei[-8:]}"
                        model = row.get(mappings.get('model'), '').strip() or None
                        status = row.get(mappings.get('status'), '').strip() or 'In Stock'
                        
                        cursor.execute("""
                            INSERT INTO phones (asset_tag, imei, serial_number, model, status)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (imei) DO UPDATE SET 
                                asset_tag = EXCLUDED.asset_tag,
                                serial_number = EXCLUDED.serial_number,
                                model = EXCLUDED.model,
                                status = EXCLUDED.status
                            RETURNING id, (xmax = 0) AS inserted;
                        """, (asset_tag, imei, serial_number, model, status))
                        
                        result = cursor.fetchone()
                        phone_id = result['id']
                        if result['inserted']:
                            inserted_count += 1
                            print(f"    Inserted new phone with ID: {phone_id}")
                        else:
                            updated_count += 1
                            print(f"    Updated existing phone with ID: {phone_id}")
                
                # Step 4: Create Assignment
                if worker_id and sim_id and phone_id:
                    print(f"  Creating assignment: worker {worker_id}, sim {sim_id}, phone {phone_id}")
                    
                    cursor.execute("""
                        SELECT id FROM assignments 
                        WHERE phone_id = %s AND return_date IS NULL
                    """, (phone_id,))
                    existing_assignment = cursor.fetchone()
                    
                    if not existing_assignment:
                        cursor.execute("""
                            INSERT INTO assignments (phone_id, sim_card_id, worker_id)
                            VALUES (%s, %s, %s)
                        """, (phone_id, sim_id, worker_id))
                        
                        cursor.execute("UPDATE phones SET status = 'In Use' WHERE id = %s", (phone_id,))
                        cursor.execute("UPDATE sim_cards SET status = 'In Use' WHERE id = %s", (sim_id,))
                        print(f"    Created assignment and updated statuses")
                    else:
                        print(f"    Assignment already exists")
                
                db.commit()
                cursor.close()
                print(f"  Row {row_index + 1} processed successfully\n")
                
            except Exception as row_error:
                if 'cursor' in locals():
                    cursor.close()
                db.rollback()
                error_count += 1
                print(f"  ERROR processing row {row_index + 1}: {row_error}\n")
                continue
        
        print(f"Import completed!")
        print(f"Inserted: {inserted_count}")
        print(f"Updated: {updated_count}")
        print(f"Errors: {error_count}")
        
    except Exception as e:
        print(f"Critical error: {e}")
        if 'db' in locals():
            db.rollback()
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    test_import_logic()
