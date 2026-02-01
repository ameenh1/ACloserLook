-- Create scan_history table for storing user scan history
-- This enables the "Recent Scans" feature on the homepage

CREATE TABLE IF NOT EXISTS scan_history (
    id BIGSERIAL PRIMARY KEY,
    scan_id UUID NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    barcode TEXT NOT NULL,
    risk_level TEXT NOT NULL,  -- "Low Risk", "Caution", "High Risk"
    risk_score INTEGER,  -- 0-100 (optional from assessment)
    risky_ingredients JSONB,  -- Array of risky ingredient objects
    explanation TEXT,  -- LLM-generated explanation
    scanned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint to ensure valid risk levels
    CONSTRAINT valid_risk_level CHECK (risk_level IN ('Low Risk', 'Caution', 'High Risk'))
);

-- Index for user's recent scans (most common query)
CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON scan_history(user_id, scanned_at DESC);

-- Index for scan_id lookups
CREATE INDEX IF NOT EXISTS idx_scan_history_scan_id ON scan_history(scan_id);

-- Index for barcode lookups
CREATE INDEX IF NOT EXISTS idx_scan_history_barcode ON scan_history(barcode);

-- Enable Row Level Security
ALTER TABLE scan_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own scans
DROP POLICY IF EXISTS "Users can view their own scan history" ON scan_history;
CREATE POLICY "Users can view their own scan history"
    ON scan_history FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own scans
DROP POLICY IF EXISTS "Users can insert their own scans" ON scan_history;
CREATE POLICY "Users can insert their own scans"
    ON scan_history FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Add comment for documentation
COMMENT ON TABLE scan_history IS 'Stores user scan history for Recent Scans feature';
COMMENT ON COLUMN scan_history.scan_id IS 'UUID from the scan assessment response';
COMMENT ON COLUMN scan_history.risk_score IS 'Numeric score 0-100, where 100 is safest';
COMMENT ON COLUMN scan_history.risky_ingredients IS 'JSONB array of risky ingredient details';
