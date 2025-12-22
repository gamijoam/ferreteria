-- SQL Script to manually add cost_price column to product_units table
-- Execute this in PostgreSQL (psql or pgAdmin)

-- Add cost_price column if it doesn't exist
ALTER TABLE product_units ADD COLUMN IF NOT EXISTS cost_price NUMERIC(14,4);

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'product_units'
ORDER BY ordinal_position;
