-- Add debate_transcript column to ai_debate_sessions
-- Date: 2025-12-27

ALTER TABLE ai_debate_sessions
ADD COLUMN IF NOT EXISTS debate_transcript JSONB;

COMMENT ON COLUMN ai_debate_sessions.debate_transcript IS 'Full debate transcript with agent reasoning';