-- RENTPLAY v5.0 Migration - Add price_annual and is_furnished columns
-- Run this on your PostgreSQL database (DigitalOcean console or psql)

ALTER TABLE rentplay_property ADD COLUMN IF NOT EXISTS price_annual DECIMAL(12,2) DEFAULT 0;
ALTER TABLE rentplay_property ADD COLUMN IF NOT EXISTS is_furnished BOOLEAN DEFAULT FALSE;

-- Set existing rows: copy current price to price_annual (since annual is required)
UPDATE rentplay_property SET price_annual = price WHERE price_annual IS NULL OR price_annual = 0;

-- Now make price_annual NOT NULL
ALTER TABLE rentplay_property ALTER COLUMN price_annual SET NOT NULL;

-- Make monthly price nullable (since not all properties have monthly rent)
ALTER TABLE rentplay_property ALTER COLUMN price DROP NOT NULL;

-- Optional: if you want to rename price to price_monthly in DB too
-- ALTER TABLE rentplay_property RENAME COLUMN price TO price_monthly;

-- Verify
-- SELECT unit_code, title, price_annual, price, is_furnished FROM rentplay_property LIMIT 5;
