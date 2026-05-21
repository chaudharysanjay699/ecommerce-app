# CASCADE DELETE ANALYSIS - DATA LOSS RISK

## ⚠️ CRITICAL ISSUE: CASCADE DELETES ARE CAUSING DATA LOSS

Your database has multiple CASCADE delete relationships that automatically delete child records when parent records are deleted. This is causing data to disappear.

---

## 🔴 CASCADE DELETE CHAINS

### 1. **User Deletion → CASCADE to Multiple Tables**
If a **User** is deleted (or soft-deleted), it will CASCADE delete:
- ✅ `otps` (ON DELETE CASCADE) - OK
- ✅ `addresses` (ON DELETE CASCADE) - OK
- ✅ `carts` + `cart_items` (ON DELETE CASCADE) - OK
- ❌ `notifications` (ON DELETE CASCADE) - **RISK**: You lose user notifications
- ✅ `device_tokens` (ON DELETE CASCADE) - OK
- ✅ `wishlist_items` (ON DELETE CASCADE) - OK

**Orders ARE PROTECTED** - `orders.user_id` has `ON DELETE RESTRICT` ✅

---

### 2. **Product Deletion → CASCADE to Cart & Wishlist**
If a **Product** is deleted (or soft-deleted), it will CASCADE delete:
- ❌ `cart_items` (ON DELETE CASCADE) - **RISK**: Products removed from carts silently
- ❌ `wishlist_items` (ON DELETE CASCADE) - **RISK**: Products removed from wishlists silently

**Order items ARE PROTECTED** - `order_items.product_id` has `ON DELETE RESTRICT` ✅

---

### 3. **Cart Deletion → CASCADE to Cart Items**
If a **Cart** is deleted, it will CASCADE delete:
- ✅ `cart_items` (ON DELETE CASCADE) - Expected behavior

---

### 4. **Order Deletion → CASCADE to Order Items & Tracking**
If an **Order** is deleted, it will CASCADE delete:
- ❌ `order_items` (ON DELETE CASCADE) - **RISK**: Order history lost
- ❌ `order_tracking` (ON DELETE CASCADE) - **RISK**: Tracking history lost

---

### 5. **Category Deletion → Hierarchical CASCADE**
If a **parent Category** is deleted, it will CASCADE delete:
- ❌ `child categories` (ON DELETE CASCADE via self-referential FK) - **MAJOR RISK**

**Products ARE PROTECTED** - `products.category_id` has `ON DELETE RESTRICT` ✅

---

## 🔍 WHAT'S HAPPENING TO YOUR DATA

### Scenario 1: Soft Delete User
When you call the **soft delete** endpoint:
```python
# In auth_service.py line 336
await self.user_repo.soft_delete(user)
```

This does NOT trigger CASCADE deletes because the user record still exists (just marked `is_deleted=True`).

### Scenario 2: Hard Delete User (via base_repository)
If anyone calls:
```python
await repo.delete(user)  # Hard delete
```

This WILL trigger CASCADE deletes and wipe out:
- All their carts, cart_items
- All their notifications
- All their wishlist items
- All their device tokens
- All their addresses
- All their OTPs

---

### Scenario 3: Delete Product (Soft Delete Used)
Admin endpoint at line 349:
```python
await repo.update(product, {"is_deleted": True})  # Soft delete
```

This does NOT trigger CASCADE deletes.

### Scenario 4: Hard Delete Product
If anyone calls:
```python
await repo.delete(product)  # Hard delete
```

This WILL trigger CASCADE deletes and wipe out:
- All cart_items containing this product
- All wishlist_items containing this product

---

### Scenario 5: Delete Offer
Offer deletion (line 71 in offers.py):
```python
await OfferService(db).delete(offer_id)  # Hard delete
```

Offers have CASCADE on `products.id`, so deleting an offer is relatively safe.

---

### Scenario 6: Delete Category
If you soft-delete a category:
```python
await repo.update(category, {"is_deleted": True})  # Line 503 in admin.py
```

This does NOT trigger CASCADE deletes.

But if anyone hard-deletes a parent category, ALL CHILD CATEGORIES are CASCADE deleted too.

---

## 🛠️ ROOT CAUSES

1. **Mixed Hard/Soft Delete Strategy**: Some entities use soft delete, others use hard delete
2. **CASCADE Deletes on Important Data**: Notifications, cart items, wishlist items get wiped
3. **No Orphan Protection**: When products are deleted, carts/wishlists lose items silently

---

## ✅ SAFE OPERATIONS (Currently)

These operations use **soft delete** and DON'T trigger cascades:
- User account deletion (auth.py line 160)
- Product deletion (admin.py line 349)
- Category deletion (admin.py line 503)

---

## ❌ DANGEROUS OPERATIONS

These operations use **hard delete** and WILL trigger cascades:
- Offer deletion (offers.py line 71)
- Address deletion (addresses.py line 91)
- Cart item removal (cart_service.py line 112)
- Uploaded file cleanup (uploaded_file_repository.py line 43)

---

## 🔧 RECOMMENDED FIXES

### Option 1: Convert ALL to Soft Delete (Recommended)
Add `is_deleted` + `deleted_at` to all tables and NEVER hard delete.

### Option 2: Remove CASCADE Deletes
Change CASCADE to RESTRICT or SET NULL where data preservation is important:
```sql
-- Example fix for cart_items
ALTER TABLE cart_items 
DROP CONSTRAINT cart_items_product_id_fkey,
ADD CONSTRAINT cart_items_product_id_fkey 
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT;
```

### Option 3: Add Cleanup Jobs
Create scheduled jobs that clean up orphaned records safely.

---

## 🔍 HOW TO INVESTIGATE YOUR DATA LOSS

Check if any hard deletes were executed:
```sql
-- Check if users were actually deleted (not soft deleted)
SELECT COUNT(*) FROM users WHERE is_deleted = true;

-- Check for orphaned cart items (product was deleted)
SELECT ci.* FROM cart_items ci
LEFT JOIN products p ON ci.product_id = p.id
WHERE p.id IS NULL;

-- Check for orphaned wishlist items
SELECT wi.* FROM wishlist_items wi
LEFT JOIN products p ON wi.product_id = p.id
WHERE p.id IS NULL;
```

Check PostgreSQL logs for actual DELETE statements:
```sql
-- Enable query logging (if not already enabled)
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();
```

---

## 📋 IMMEDIATE ACTION ITEMS

1. ✅ **Stop all hard delete operations** - Review code for `await repo.delete()` calls
2. ✅ **Add soft delete to remaining tables** - Offers, addresses, notifications, etc.
3. ✅ **Change CASCADE to RESTRICT** - For cart_items, wishlist_items on products
4. ✅ **Add query filters** - Always filter `WHERE is_deleted = false` in queries
5. ✅ **Review recent migrations** - Check if migration 0011 caused any issues

---

## 🚨 CHECK THESE FILES IMMEDIATELY

Locations where hard deletes happen:
- [app/api/v1/offers.py](app/api/v1/offers.py#L71) - Offer deletion
- [app/api/v1/addresses.py](app/api/v1/addresses.py#L91) - Address deletion  
- [app/services/cart_service.py](app/services/cart_service.py#L112) - Cart item removal
- [app/services/offer_service.py](app/services/offer_service.py#L86) - Offer service deletion
- [app/repositories/uploaded_file_repository.py](app/repositories/uploaded_file_repository.py#L43) - File cleanup

---

**SUMMARY**: Your data is getting blank because of CASCADE deletes. Most likely, someone deleted:
1. A product → wiped all cart_items and wishlist_items for that product
2. A user (hard delete, not soft) → wiped all their related data
3. A category → wiped all child categories

Check your application logs and database audit trail to see which delete operations were executed recently.
