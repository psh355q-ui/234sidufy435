import asyncpg
import asyncio

async def analyze_all_tables():
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='Qkqhdi1!',
        database='ai_trading'
    )
    
    try:
        # Get all tables
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        print("="*100)
        print("ANALYZING ALL TABLES FOR VOTE/RESULT COLUMNS")
        print("="*100)
        
        vote_keywords = ['vote', 'action', 'signal', 'decision', 'recommendation', 'buy', 'sell', 'hold']
        
        for table in tables:
            table_name = table['table_name']
            
            # Get columns
            columns = await conn.fetch("""
                SELECT column_name, data_type
                FROM information_schema.columns 
                WHERE table_name = $1
                ORDER BY ordinal_position
            """, table_name)
            
            # Check if any column contains keywords
            matching_columns = []
            for col in columns:
                col_name_lower = col['column_name'].lower()
                if any(keyword in col_name_lower for keyword in vote_keywords):
                    matching_columns.append((col['column_name'], col['data_type']))
            
            if matching_columns:
                print(f"\n📊 {table_name}")
                print(f"   Total columns: {len(columns)}")
                print(f"   Vote/Result columns:")
                for col_name, col_type in matching_columns:
                    print(f"      - {col_name:30} {col_type}")
        
        print("\n" + "="*100)
        print("DETAILED: ai_debate_sessions (War Room)")
        print("="*100)
        
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'ai_debate_sessions' 
            ORDER BY ordinal_position
        """)
        
        for col in columns:
            null_str = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"{col['column_name']:30} {col['data_type']:25} {null_str}")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_all_tables())
