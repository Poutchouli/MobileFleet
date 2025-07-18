-- Migration script to add timestamp columns to phones table
-- Run this script to add created_at and updated_at columns to existing phones table

-- Step 1: Add the columns
ALTER TABLE phones ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ;
ALTER TABLE phones ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- Step 2: Set default values for existing records
UPDATE phones 
SET 
    created_at = COALESCE(purchase_date::TIMESTAMPTZ, now()),
    updated_at = now()
WHERE created_at IS NULL OR updated_at IS NULL;

-- Step 3: Set defaults and constraints for new records
ALTER TABLE phones ALTER COLUMN created_at SET DEFAULT now();
ALTER TABLE phones ALTER COLUMN updated_at SET DEFAULT now();
ALTER TABLE phones ALTER COLUMN created_at SET NOT NULL;
ALTER TABLE phones ALTER COLUMN updated_at SET NOT NULL;

-- Step 4: Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Step 5: Create trigger to automatically update updated_at for phones table
DROP TRIGGER IF EXISTS update_phones_updated_at ON phones;
CREATE TRIGGER update_phones_updated_at 
    BEFORE UPDATE ON phones 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Verify the changes
SELECT column_name, data_type, is_nullable, column_default 
FROM information_schema.columns 
WHERE table_name = 'phones' AND column_name IN ('created_at', 'updated_at');
