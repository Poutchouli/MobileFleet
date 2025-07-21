#!/usr/bin/env python3
"""Comprehensive delimiter test script"""

import psycopg2
import psycopg2.extras
import csv
import io

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

def test_delimiter(test_name, csv_data, delimiter, mappings):
    """Test CSV parsing with different delimiters"""
    print(f"\n=== Testing {test_name} ===")
    print(f"Delimiter: '{delimiter}'")
    print(f"CSV Data: {csv_data}")
    
    try:
        reader = csv.DictReader(io.StringIO(csv_data), delimiter=delimiter)
        
        print("Headers:", reader.fieldnames)
        
        for row_index, row in enumerate(reader):
            print(f"Row {row_index + 1}: {row}")
            
            # Test field extraction
            worker_name = row.get(mappings.get('name', ''), '').strip()
            iccid = row.get(mappings.get('iccid', ''), '').strip()
            imei = row.get(mappings.get('imei', ''), '').strip()
            
            print(f"  Extracted - Worker: '{worker_name}', ICCID: '{iccid}', IMEI: '{imei}'")
            
            if worker_name and iccid and imei:
                print(f"  ✅ All fields extracted successfully")
            else:
                print(f"  ❌ Some fields missing or empty")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Test all delimiter types"""
    
    # Standard field mappings
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
    
    # Test 1: Comma delimiter
    csv_comma = """Nom,N° SIM,PIN,PUK,IMEI,Matériel,Asset Tag,Carrier,Status
Alice Comma,1234567890123456900,1111,11111111,123456789012500,Samsung Galaxy S22,PHONE200,Orange,In Stock"""
    
    # Test 2: Semicolon delimiter  
    csv_semicolon = """Nom;N° SIM;PIN;PUK;IMEI;Matériel;Asset Tag;Carrier;Status
Alice Semicolon;1234567890123456901;2222;22222222;123456789012501;iPhone 14;PHONE201;SFR;In Stock"""
    
    # Test 3: Tab delimiter
    csv_tab = """Nom	N° SIM	PIN	PUK	IMEI	Matériel	Asset Tag	Carrier	Status
Alice Tab	1234567890123456902	3333	33333333	123456789012502	Google Pixel	PHONE202	Bouygues	In Stock"""
    
    # Run tests
    test_delimiter("Comma Delimiter", csv_comma, ',', mappings)
    test_delimiter("Semicolon Delimiter", csv_semicolon, ';', mappings)
    test_delimiter("Tab Delimiter", csv_tab, '\t', mappings)
    
    print("\n=== Summary ===")
    print("All delimiter tests completed. Check results above.")

if __name__ == "__main__":
    main()
