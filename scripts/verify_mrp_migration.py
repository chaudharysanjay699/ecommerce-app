"""Verify that old_price has been renamed to mrp and all products have mrp values"""

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
        # Check if old_price column exists
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'old_price'
        """)
        
        if result > 0:
            print("❌ Column 'old_price' still exists in products table")
        else:
            print("✅ Column 'old_price' has been removed")
        
        # Check if mrp column exists
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'mrp'
        """)
        
        if result > 0:
            print("✅ Column 'mrp' exists in products table")
        else:
            print("❌ Column 'mrp' does not exist in products table")
        
        # Check for NULL mrp values
        result = await conn.fetchval("SELECT COUNT(*) FROM products WHERE mrp IS NULL")
        
        if result > 0:
            print(f"⚠️  {result} products have NULL mrp values")
        else:
            print("✅ All products have mrp values")
        
        # Show sample products
        result = await conn.fetch("""
            SELECT id, name, price, mrp 
            FROM products 
            LIMIT 5
        """)
        
        print("\n📊 Sample products:")
        for row in result:
            discount = ""
            if row['mrp'] and row['mrp'] > row['price']:
                discount_pct = round(((row['mrp'] - row['price']) / row['mrp']) * 100)
                discount = f" ({discount_pct}% off)"
            print(f"  - {row['name'][:30]:30} | Price: ₹{row['price']:6.2f} | MRP: ₹{row['mrp']:6.2f}{discount}")
        
        # Count products with discount
        result = await conn.fetchval("""
            SELECT COUNT(*) 
            FROM products 
            WHERE mrp IS NOT NULL AND mrp > price
        """)
        
        print(f"\n💰 {result} products have discounts (MRP > Price)")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
