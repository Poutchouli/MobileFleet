from app import app, get_db

with app.app_context():
    try:
        db = get_db()
        cursor = db.cursor()
        
        print("Updating asset_history_log constraint...")
        
        # Drop the old constraint
        cursor.execute('ALTER TABLE asset_history_log DROP CONSTRAINT asset_history_log_asset_type_check;')
        print("✅ Dropped old constraint")
        
        # Add the new constraint that includes 'Ticket'
        cursor.execute("ALTER TABLE asset_history_log ADD CONSTRAINT asset_history_log_asset_type_check CHECK (asset_type IN ('Phone', 'SIM', 'Ticket'));")
        print("✅ Added new constraint with 'Ticket' support")
        
        db.commit()
        cursor.close()
        print('✅ Successfully updated asset_history_log constraint to include Ticket')
        
    except Exception as e:
        print(f'❌ Error updating constraint: {e}')
        if 'db' in locals():
            db.rollback()
            cursor.close()
