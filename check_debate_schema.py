import asyncpg
import asyncio

async def check_table():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='Qkqhdi1!',
        database='ai_trading'
    )
    
    try:
        # Get columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'ai_debate_sessions' 
            ORDER BY ordinal_position
        """)
        
        print("ai_debate_sessions table columns:")
        print("="*70)
        for col in columns:
            print(f"{col['column_name']:25} {col['data_type']:20} NULL: {col['is_nullable']}")
        
        print(f"\nTotal columns: {len(columns)}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_table())
