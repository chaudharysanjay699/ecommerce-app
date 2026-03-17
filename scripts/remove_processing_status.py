"""Convert 'processing' status to 'confirmed'"""

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
        print("Converting 'processing' status to 'confirmed'...\n")
        
        # Update orders table
        result = await conn.execute("""
            UPDATE orders 
            SET status = 'confirmed'
            WHERE status = 'processing'
        """)
        print(f"✓ Updated orders table: {result}")
        
        # Update order_tracking table
        result = await conn.execute("""
            UPDATE order_tracking 
            SET status = 'confirmed', 
                description = COALESCE(description || ' (converted from processing)', 'Converted from processing status')
            WHERE status = 'processing'
        """)
        print(f"✓ Updated order_tracking table: {result}")
        
        # Verify the changes
        result = await conn.fetch("SELECT status, COUNT(*) as count FROM orders GROUP BY status ORDER BY status")
        print("\n📊 Updated order statuses:")
        for row in result:
            print(f"  - {row['status']}: {row['count']} orders")
        
        print("\n✅ Migration complete! All 'processing' statuses converted to 'confirmed'")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
