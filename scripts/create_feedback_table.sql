-- Create user_feedback table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    target_type VARCHAR(50) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    feedback_type VARCHAR(20) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_feedback_target ON user_feedback (target_type, target_id);