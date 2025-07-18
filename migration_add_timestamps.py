# migration_add_timestamps.py
# Script to add timestamp columns to the phones table

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the migration to add timestamp columns to phones table."""
    try:
        # Connect to the database (same way as Flask app)
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print("❌ DATABASE_URL environment variable not found")
            return False
        
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # Check if columns already exist
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'phones' AND column_name IN ('created_at', 'updated_at')
        """)
        existing_columns = [row['column_name'] for row in cursor.fetchall()]
        
        if 'created_at' in existing_columns and 'updated_at' in existing_columns:
            print("ℹ️  Timestamp columns already exist in phones table")
            cursor.close()
            conn.close()
            return True
        
        print("🔧 Adding timestamp columns to phones table...")
        
        # Step 1: Add the columns
        if 'created_at' not in existing_columns:
            cursor.execute("ALTER TABLE phones ADD COLUMN created_at TIMESTAMPTZ")
            print("   ✅ Added created_at column")
        
        if 'updated_at' not in existing_columns:
            cursor.execute("ALTER TABLE phones ADD COLUMN updated_at TIMESTAMPTZ")
            print("   ✅ Added updated_at column")
        
        # Step 2: Set default values for existing records
        cursor.execute("""
            UPDATE phones 
            SET 
                created_at = COALESCE(purchase_date::TIMESTAMPTZ, now()),
                updated_at = now()
            WHERE created_at IS NULL OR updated_at IS NULL
        """)
        print("   ✅ Set default values for existing records")
        
        # Step 3: Set defaults and constraints for new records
        cursor.execute("ALTER TABLE phones ALTER COLUMN created_at SET DEFAULT now()")
        cursor.execute("ALTER TABLE phones ALTER COLUMN updated_at SET DEFAULT now()")
        cursor.execute("ALTER TABLE phones ALTER COLUMN created_at SET NOT NULL")
        cursor.execute("ALTER TABLE phones ALTER COLUMN updated_at SET NOT NULL")
        print("   ✅ Set constraints and defaults")
        
        # Step 4: Create function to update updated_at timestamp
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = now();
                RETURN NEW;
            END;
            $$ language 'plpgsql'
        """)
        print("   ✅ Created update function")
        
        # Step 5: Create trigger
        cursor.execute("DROP TRIGGER IF EXISTS update_phones_updated_at ON phones")
        cursor.execute("""
            CREATE TRIGGER update_phones_updated_at 
                BEFORE UPDATE ON phones 
                FOR EACH ROW 
                EXECUTE FUNCTION update_updated_at_column()
        """)
        print("   ✅ Created update trigger")
        
        # Commit all changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'phones' AND column_name IN ('created_at', 'updated_at')
            ORDER BY column_name
        """)
        verification = cursor.fetchall()
        
        print("\n📋 Verification:")
        for col in verification:
            print(f"   - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']}, default: {col['column_default']})")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("🚀 Starting phones table timestamp migration...")
    success = run_migration()
    exit(0 if success else 1)
