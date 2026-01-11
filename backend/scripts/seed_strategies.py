import sys
import os
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.database import get_sync_session
from backend.database.repository_multi_strategy import StrategyRepository

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def seed_strategies():
    json_path = os.path.join(os.path.dirname(__file__), '../../docs/planning/seed-strategies.json')
    
    if not os.path.exists(json_path):
        logger.error(f"Seed file not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        strategies_data = json.load(f)
        
    with get_sync_session() as session:
        repo = StrategyRepository(session)
        
        for data in strategies_data:
            # Check if strategy exists by name (unique identifier)
            # data['id'] in JSON maps to 'name' column in DB
            strategy_name = data['id']
            
            existing = repo.get_by_name(strategy_name)
            
            if existing:
                logger.info(f"Strategy {strategy_name} exists. Updating...")
                # Update existing strategy
                existing.display_name = data['name']
                existing.persona_type = data['type']
                existing.priority = data['priority']
                existing.time_horizon = data.get('time_horizon', 'medium')
                existing.is_active = (data['status'] == 'ACTIVE')
                existing.config_metadata = data['config']
                # repo.update calls session.commit() internally usually? 
                # Checking repo.update implementation: it does find by ID and update attributes.
                # StrategyRepository.update implementation needs to be checked if it commits.
                # If not, we commit at end.
                # But here we updated attributes on the object attached to session.
            else:
                logger.info(f"Creating strategy: {strategy_name}")
                repo.create(
                    name=strategy_name,
                    display_name=data['name'],
                    persona_type=data['type'],
                    priority=data['priority'],
                    time_horizon=data.get('time_horizon', 'medium'),
                    is_active=(data['status'] == 'ACTIVE'),
                    config_metadata=json.dumps(data['config']) # Explicitly dump to string for JSONB
                )
        
        session.commit()
        logger.info("Strategy seeding completed.")

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        seed_strategies()
    except Exception as e:
        logger.exception("Seeding failed")
        sys.exit(1)
