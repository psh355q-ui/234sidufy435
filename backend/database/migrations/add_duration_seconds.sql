-- Add missing duration_seconds column

ALTER TABLE ai_debate_sessions
ADD COLUMN IF NOT EXISTS duration_seconds FLOAT;

-- Verify
SELECT column_name, data_type
FROM information_schema.columns
WHERE
    table_name = 'ai_debate_sessions'
    AND column_name = 'duration_seconds';