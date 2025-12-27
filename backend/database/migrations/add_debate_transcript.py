"""
Add debate_transcript column to ai_debate_sessions table
"""
import sys
import os
from pathlib import Path

# Add project root to path (migrations -> database -> backend -> project_root)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment FIRST
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✓ Loaded .env from: {env_path}")
else:
    print(f"⚠️  .env not found at: {env_path}")

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine  
from sqlalchemy import text

async def run_migration():
    """Add debate_transcript column"""
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # Construct from parts
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "ai_trading")
        db_user = os.getenv("DB_USER", "postgres")
        db_pass = os.getenv("POSTGRES_PASSWORD", "ghkdwlgPtm!")
        db_url = f"postgresql+asyncpg://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        print(f"📡 Using DB: {db_name} on {db_host}:{db_port}")
    
    # Create async engine
    engine = create_async_engine(db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check if column exists
            result = await conn.execute(text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'ai_debate_sessions' AND column_name = 'debate_transcript'"
            ))
            exists = result.fetchone()
            
            if exists:
                print("✅ debate_transcript column already exists")
                return True
            
            # Add column
            await conn.execute(text(
                "ALTER TABLE ai_debate_sessions ADD COLUMN debate_transcript JSONB"
            ))
            
            print("✅ Added debate_transcript column successfully")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(run_migration())
    sys.exit(0 if success else 1)
