"""Fix enum values in database - add lowercase versions"""

import asyncio
import asyncpg


async def main():
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='postgres',
        database='ecom-db'
    )
    
    try:
        # Check current enum values
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
            ORDER BY enumlabel
        """)
        
        print("Current enum values:")
        for row in result:
            print(f"  - {row['enumlabel']}")
        
        # Add lowercase values if they don't exist
        lowercase_values = ['placed', 'confirmed', 'processing', 'packed', 'out_for_delivery', 'delivered', 'cancelled']
        
        for value in lowercase_values:
            try:
                await conn.execute(f"ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS '{value}'")
                print(f"✓ Added enum value: {value}")
            except Exception as e:
                print(f"✗ Failed to add {value}: {e}")
        
        # Check enum values again
        result = await conn.fetch("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'orderstatus')
            ORDER BY enumlabel
        """)
        
        print("\nUpdated enum values:")
        for row in result:
            print(f"  - {row['enumlabel']}")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
