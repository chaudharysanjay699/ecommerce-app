"""Convert existing order status data from UPPERCASE to lowercase"""

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
        print("Converting order statuses to lowercase...")
        
        # Update orders table
        result = await conn.execute("""
            UPDATE orders 
            SET status = LOWER(status::text)::orderstatus
            WHERE status::text IN ('PLACED', 'CONFIRMED', 'PACKED', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED')
        """)
        print(f"✓ Updated orders table: {result}")
        
        # Update order_tracking table
        result = await conn.execute("""
            UPDATE order_tracking 
            SET status = LOWER(status::text)::orderstatus
            WHERE status::text IN ('PLACED', 'CONFIRMED', 'PACKED', 'OUT_FOR_DELIVERY', 'DELIVERED', 'CANCELLED')
        """)
        print(f"✓ Updated order_tracking table: {result}")
        
        # Verify the changes
        result = await conn.fetch("SELECT DISTINCT status FROM orders")
        print("\nCurrent statuses in orders table:")
        for row in result:
            print(f"  - {row['status']}")
            
        result = await conn.fetch("SELECT DISTINCT status FROM order_tracking")
        print("\nCurrent statuses in order_tracking table:")
        for row in result:
            print(f"  - {row['status']}")
        
        print("\n✅ Migration complete!")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
