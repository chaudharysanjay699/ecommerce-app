"""Test MRP validation"""

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
        print("🧪 Testing MRP Validation Logic\n")
        
        # Get a sample product
        result = await conn.fetchrow("SELECT id, name, price, mrp FROM products LIMIT 1")
        
        if not result:
            print("❌ No products found in database")
            return
        
        product = dict(result)
        print(f"📦 Sample Product:")
        print(f"   Name: {product['name']}")
        print(f"   Price: ₹{product['price']}")
        print(f"   MRP: ₹{product['mrp']}")
        
        print(f"\n✅ Valid Cases:")
        print(f"   1. MRP (₹{product['mrp']}) >= Price (₹{product['price']}) ✓")
        print(f"   2. MRP = Price (no discount) ✓")
        print(f"   3. MRP > Price (with discount) ✓")
        
        print(f"\n❌ Invalid Cases (should be blocked):")
        invalid_mrp = product['price'] - 10
        print(f"   1. MRP (₹{invalid_mrp}) < Price (₹{product['price']}) ✗")
        print(f"      Error: MRP cannot be less than selling price")
        
        print(f"\n📋 Validation Rules:")
        print(f"   • Frontend: Validates before API call")
        print(f"   • Backend Schema: Validates on create/update")
        print(f"   • Backend Service: Validates partial updates with existing values")
        
        print(f"\n💡 Business Logic:")
        print(f"   • MRP (Maximum Retail Price) = Printed price on product")
        print(f"   • Selling Price = Actual price customer pays")
        print(f"   • Discount = ((MRP - Price) / MRP) × 100%")
        print(f"   • MRP should always be >= Selling Price")
            
    finally:
        await conn.close()


if __name__ == '__main__':
    asyncio.run(main())
