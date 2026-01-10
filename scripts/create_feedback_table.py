import sys
import os
import logging
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Load env vars explicitly
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"DEBUG: Loaded .env from {env_path}")

from backend.database.models import UserFeedback, Base
from backend.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_feedback_table():
    print("🛠️ Creating 'user_feedback' table (Standalone)...")
    
    # User specified credentials
    pwd = "Qkqhdi1!"
    port = 5433
    host = "127.0.0.1" # Force IPv4
    user = settings.timescale_user or "postgres"
    dbname = settings.timescale_db
    
    print(f"DEBUG: Using hardcoded credentials: user={user}, host={host}, port={port}, db={dbname}")
    
    db_url = f"postgresql://{user}:{pwd}@{host}:{port}/{dbname}"
    
    try:
        engine = create_engine(db_url)
        UserFeedback.__table__.create(bind=engine, checkfirst=True)
        print("✅ 'user_feedback' table created/verified successfully.")
    except Exception as e:
        print(f"❌ Failed to create table: {e}")

if __name__ == "__main__":
    create_feedback_table()
