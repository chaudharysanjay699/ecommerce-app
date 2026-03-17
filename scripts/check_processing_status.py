"""Check if any orders have 'processing' status"""

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
        # Check orders table
        result = await conn.fetch("SELECT id, status FROM orders WHERE status = 'processing'")
        if result:
            print(f"⚠️  Found {len(result)} orders with 'processing' status:")
            for row in result:
                print(f"  - Order ID: {row['id']}")
        else:
            print("✅ No orders with 'processing' status found in orders table")
        
        # Check order_tracking table
        result = await conn.fetch("SELECT id, order_id, status FROM order_tracking WHERE status = 'processing'")
        if result:
            print(f"\n⚠️  Found {len(result)} tracking records with 'processing' status:")
            for row in result:
                print(f"  - Tracking ID: {row['id']}, Order ID: {row['order_id']}")
        else:
            print("✅ No tracking records with 'processing' status found")
        
        # Show all current statuses in use
        print("\n📊 Current order statuses in use:")
        result = await conn.fetch("SELECT status, COUNT(*) as count FROM orders GROUP BY status ORDER BY status")
        for row in result:
            print(f"  - {row['status']}: {row['count']} orders")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
