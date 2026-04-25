from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.notification import BannerCreate, BannerOut, BannerUpdate
from app.schemas.offer import OfferCreate, OfferOut, OfferUpdate
from app.schemas.order import AdminOrderCancel, OrderOut, OrderStatusUpdate
from app.schemas.order_tracking import OrderTrackingOut
from app.schemas.product import CategoryCreate, CategoryOut, CategoryUpdate, CategoryWithChildrenOut, ProductCreate, ProductDetailOut, ProductOut, ProductUpdate, StockAdjust
from app.schemas.user import AdminUserUpdate, UserOut
from app.schemas.app_settings import AppSettingsOut, AppSettingsUpdate
from app.services.notification_service import BannerService
from app.services.offer_service import OfferService
from app.services.order_service import OrderService
from app.services.product_service import CategoryService, ProductService
from app.services.tracking_service import TrackingService
from app.utils.file_upload import delete_file, save_upload_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

# ── Shorthand dependency alias & Models ───────────────────────────────────────
Admin = Annotated[object, Depends(get_current_admin)]
DB = Annotated[AsyncSession, Depends(get_db)]


class UserStatusUpdate(BaseModel):
    """Payload for toggling user active status."""
    is_active: bool


# ── Dashboard ─────────────────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def get_dashboard_stats(
    _: Admin,
    db: DB,
):
    """Return key statistics for the admin dashboard."""
    try:
        from app.repositories.user_repository import UserRepository
        from app.repositories.product_repository import ProductRepository
        from app.repositories.order_repository import OrderRepository
        
        # Get total and active users (exclude deleted and super-admin)
        result = await db.execute(
            select(func.count()).select_from(User).where(
                User.is_deleted == False, User.is_super_admin == False
            )
        )
        total_users = result.scalar_one()
        
        result = await db.execute(
            select(func.count()).select_from(User).where(
                User.is_active == True, User.is_deleted == False, User.is_super_admin == False
            )
        )
        active_users = result.scalar_one()
        
        # Get total products
        total_products = await ProductRepository(db).count()

        result = await db.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.is_out_of_stock == True)
        )
        out_of_stock_products = result.scalar_one()
        
        # Get order statistics
        total_orders = await OrderRepository(db).count()
        total_orders = await OrderRepository(db).count()
        
        # Get total revenue from delivered orders
        result = await db.execute(
            select(func.sum(Order.total)).where(
                Order.status == OrderStatus.DELIVERED
            )
        )
        total_revenue = result.scalar_one() or 0.0
        
        # Get order counts by status
        result = await db.execute(
            select(func.count()).select_from(Order).where(Order.status == OrderStatus.PLACED)
        )
        pending_orders = result.scalar_one()
        
        out_of_stock_result = await db.execute(
            select(func.count()).select_from(Order).where(Order.status == OrderStatus.DELIVERED)
        )
        delivered_orders = out_of_stock_result.scalar_one()
        
        result = await db.execute(
            select(func.count()).select_from(Order).where(Order.status == OrderStatus.CANCELLED)
        )
        cancelled_orders = result.scalar_one()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_products": total_products,
            "out_of_stock_products": out_of_stock_products,
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "pending_orders": pending_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Users ─────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    _: Admin,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Return a paginated list of users (excludes deleted and super-admin users)."""
    from app.repositories.user_repository import UserRepository
    return await UserRepository(db).list_for_admin(skip, limit)


@router.patch("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    payload: AdminUserUpdate,
    _: Admin,
    db: DB,
):
    """Toggle a user's active/verified/admin flags."""
    from app.repositories.user_repository import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    data = payload.model_dump(exclude_none=True)
    return await repo.update(user, data)


@router.patch("/users/{user_id}/status", response_model=UserOut)
async def toggle_user_status(
    user_id: UUID,
    payload: UserStatusUpdate,
    _: Admin,
    db: DB,
):
    """Toggle a user's active status."""
    from app.repositories.user_repository import UserRepository

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return await repo.update(user, {"is_active": payload.is_active})


# ── Orders ────────────────────────────────────────────────────────────────────

@router.get("/orders", response_model=list[OrderOut])
async def list_all_orders(
    _: Admin,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Return all orders across all users (paginated)."""
    return await OrderService(db).admin_list_orders(skip, limit)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    _: Admin,
    db: DB,
):
    """Return full detail for any order."""
    return await OrderService(db).admin_get_order(order_id)


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdate,
    _: Admin,
    db: DB,
):
    """Advance an order to a new status and append a tracking event."""
    return await OrderService(db).admin_update_status(order_id, payload)


@router.patch("/orders/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: UUID,
    payload: AdminOrderCancel,
    _: Admin,
    db: DB,
):
    """Cancel an order and notify the customer."""
    return await OrderService(db).admin_cancel_order(order_id, payload)


@router.get("/orders/{order_id}/tracking", response_model=list[OrderTrackingOut])
async def get_order_tracking(
    order_id: UUID,
    _: Admin,
    db: DB,
):
    """Return the complete tracking timeline for any order."""
    return await TrackingService(db).list_for_order(order_id)


@router.get("/orders/{order_id}/invoice")
async def get_admin_order_invoice(
    order_id: UUID,
    _: Admin,
    db: DB,
):
    """Admin: return the invoice PDF for any order."""
    order = await OrderService(db).admin_get_order(order_id)
    if not order.invoice_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not generated yet")
    filepath = Path(settings.UPLOAD_DIR) / "pdfs" / f"invoice_{order.id}.pdf"
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice file not found")
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=f"invoice_{str(order.id)[:8]}.pdf",
    )


@router.get("/orders/{order_id}/shipping-label")
async def get_admin_order_shipping_label(
    order_id: UUID,
    _: Admin,
    db: DB,
):
    """Admin: return the shipping label PDF for any order."""
    order = await OrderService(db).admin_get_order(order_id)
    if not order.shipping_label_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping label not generated yet")
    filepath = Path(settings.UPLOAD_DIR) / "pdfs" / f"shipping_label_{order.id}.pdf"
    if not filepath.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipping label file not found")
    return FileResponse(
        path=str(filepath),
        media_type="application/pdf",
        filename=f"shipping_label_{str(order.id)[:8]}.pdf",
    )


@router.post("/orders/{order_id}/regenerate-pdfs", response_model=OrderOut)
async def regenerate_order_pdfs(
    order_id: UUID,
    _: Admin,
    db: DB,
):
    """Admin: regenerate invoice & shipping label PDFs for an order."""
    from app.repositories.app_settings_repository import AppSettingsRepository
    from app.services.pdf_service import generate_invoice_pdf, generate_shipping_label_pdf
    from app.repositories.order_repository import OrderRepository

    order = await OrderService(db).admin_get_order(order_id)
    app_settings = await AppSettingsRepository(db).get_settings()

    invoice_url = await generate_invoice_pdf(order, store_name=app_settings.store_name, app_settings=app_settings)
    label_url = await generate_shipping_label_pdf(order, store_name=app_settings.store_name)

    order_repo = OrderRepository(db)
    await order_repo.update(order, {"invoice_url": invoice_url, "shipping_label_url": label_url})

    return await OrderService(db).admin_get_order(order_id)


# ── Products ──────────────────────────────────────────────────────────────────

@router.get("/products", response_model=list[ProductDetailOut])
async def list_all_products(
    _: Admin,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Return all products (including inactive) for admin management with category."""
    from app.repositories.product_repository import ProductRepository
    return await ProductRepository(db).list_with_category(skip, limit)


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    _: Admin,
    db: DB,
):
    """Create a new product."""
    return await ProductService(db).create(payload)


@router.put("/products/{product_id}", response_model=ProductOut)
@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    _: Admin,
    db: DB,
):
    """Update a product (supports both PUT and PATCH)."""
    return await ProductService(db).update(product_id, payload)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    _: Admin,
    db: DB,
):
    """Soft delete a product (sets is_deleted=True)."""
    await ProductService(db).delete(product_id)
    return None


@router.post("/products/{product_id}/restore", response_model=ProductOut)
async def restore_product(
    product_id: UUID,
    _: Admin,
    db: DB,
):
    """Restore a soft-deleted product."""
    return await ProductService(db).restore(product_id)


@router.get("/products/out-of-stock", response_model=list[ProductOut])
async def list_out_of_stock(
    _: Admin,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Return all products that are currently out of stock."""
    from app.repositories.product_repository import ProductRepository
    return await ProductRepository(db).list_out_of_stock(skip, limit)


@router.post("/products/{product_id}/adjust-stock", response_model=ProductOut)
async def adjust_stock(
    product_id: UUID,
    payload: StockAdjust,
    _: Admin,
    db: DB,
):
    """Set the absolute stock level for a product."""
    return await ProductService(db).adjust_stock(product_id, payload)


@router.post("/products/upload-image")
async def upload_product_image(
    admin: Admin,
    db: DB,
    file: UploadFile = File(...),
):
    """
    Upload an image for a product.
    
    Returns the file path/URL that can be used in the image_url field.
    Supports: JPG, JPEG, PNG, GIF, WEBP (max 5MB)
    
    File metadata is saved to the database for tracking.
    """
    try:
        from app.repositories.uploaded_file_repository import UploadedFileRepository
        from app.models.uploaded_file import UploadedFile
        from app.utils.file_upload import get_file_url
        
        # Save file to uploads/products/
        file_metadata = await save_upload_file(file, subdir="products")
        file_path = file_metadata["file_path"]
        
        # Save metadata to database (only path, URL constructed at runtime)
        uploaded_file = UploadedFile(
            original_filename=file_metadata["original_filename"],
            file_path=file_path,
            file_url=file_path,  # Store path, construct URL at runtime
            file_size=file_metadata["file_size"],
            mime_type=file_metadata["mime_type"],
            entity_type="product",
            entity_id=None,  # Will be set when product is created/updated
            uploaded_by=admin.id if hasattr(admin, 'id') else None,
        )
        
        repo = UploadedFileRepository(db)
        await repo.create(uploaded_file)
        await db.commit()
        
        # Construct full URL dynamically
        file_url = get_file_url(file_path)
        
        return {
            "file_path": file_path,
            "file_url": file_url,
            "filename": file_metadata["original_filename"],
            "file_size": file_metadata["file_size"],
            "mime_type": file_metadata["mime_type"],
            "server_url": settings.SERVER_URL,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload product image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


# ── Categories ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryWithChildrenOut])
async def list_all_categories(
    _: Admin,
    db: DB,
    include_deleted: bool = False,
):
    """Return all categories with subcategories for admin management. Set include_deleted=true to see deleted categories."""
    from app.repositories.product_repository import CategoryRepository
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.product import Category
    
    if include_deleted:
        result = await db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .order_by(Category.is_deleted, Category.sort_order, Category.name)
        )
        categories = result.scalars().all()
    else:
        result = await db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.is_deleted == False)
            .order_by(Category.sort_order, Category.name)
        )
        categories = result.scalars().all()
    
    # Filter out deleted children from all categories
    for category in categories:
        category.children = [child for child in category.children if not child.is_deleted]
    
    return categories


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    _: Admin,
    db: DB,
):
    """Create a new category."""
    return await CategoryService(db).create(payload)


@router.patch("/categories/{category_id}/toggle", response_model=CategoryOut)
async def toggle_category_status(
    category_id: UUID,
    _: Admin,
    db: DB,
):
    """Toggle a category's active/inactive status."""
    return await CategoryService(db).toggle_status(category_id)


@router.put("/categories/{category_id}", response_model=CategoryOut)
@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    _: Admin,
    db: DB,
):
    """Update a category (supports both PUT and PATCH)."""
    return await CategoryService(db).update(category_id, payload)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    _: Admin,
    db: DB,
):
    """Soft delete a category (sets is_deleted=True)."""
    await CategoryService(db).delete(category_id)
    return None


@router.post("/categories/{category_id}/restore", response_model=CategoryOut)
async def restore_category(
    category_id: UUID,
    _: Admin,
    db: DB,
):
    """Restore a soft-deleted category."""
    return await CategoryService(db).restore(category_id)


@router.post("/categories/upload-image")
async def upload_category_image(
    admin: Admin,
    db: DB,
    file: UploadFile = File(...),
):
    """
    Upload an image for a category.
    
    Returns the file path/URL that can be used in the image_url field.
    Supports: JPG, JPEG, PNG, GIF, WEBP (max 5MB)
    
    File metadata is saved to the database for tracking.
    """
    try:
        from app.repositories.uploaded_file_repository import UploadedFileRepository
        from app.models.uploaded_file import UploadedFile
        from app.utils.file_upload import get_file_url
        
        # Save file to uploads/categories/
        file_metadata = await save_upload_file(file, subdir="categories")
        file_path = file_metadata["file_path"]
        
        # Save metadata to database (only path, URL constructed at runtime)
        uploaded_file = UploadedFile(
            original_filename=file_metadata["original_filename"],
            file_path=file_path,
            file_url=file_path,  # Store path, construct URL at runtime
            file_size=file_metadata["file_size"],
            mime_type=file_metadata["mime_type"],
            entity_type="category",
            entity_id=None,  # Will be set when category is created/updated
            uploaded_by=admin.id if hasattr(admin, 'id') else None,
        )
        
        repo = UploadedFileRepository(db)
        await repo.create(uploaded_file)
        await db.commit()
        
        # Construct full URL dynamically
        file_url = get_file_url(file_path)
        
        return {
            "file_path": file_path,
            "file_url": file_url,
            "filename": file_metadata["original_filename"],
            "file_size": file_metadata["file_size"],
            "mime_type": file_metadata["mime_type"],
            "server_url": settings.SERVER_URL,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload category image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )


# ── Uploaded Files ────────────────────────────────────────────────────────────

@router.get("/uploaded-files/{entity_type}/{entity_id}")
async def get_uploaded_files(
    entity_type: str,
    entity_id: UUID,
    _: Admin,
    db: DB,
):
    """
    Get all uploaded files for a specific entity.
    
    Args:
        entity_type: Type of entity ('category', 'product', 'banner', etc.)
        entity_id: UUID of the entity
    
    Returns list of file metadata records.
    """
    from app.repositories.uploaded_file_repository import UploadedFileRepository
    from app.schemas.uploaded_file import UploadedFileOut
    
    repo = UploadedFileRepository(db)
    files = await repo.get_by_entity(entity_type, entity_id)
    
    return [UploadedFileOut.model_validate(f) for f in files]


# ── Offers ────────────────────────────────────────────────────────────────────

@router.get("/offers", response_model=list[OfferOut])
async def list_offers(
    _: Admin,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    """Return all active offers."""
    return await OfferService(db).list_active(skip, limit)


@router.post("/offers", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
async def create_offer(
    payload: OfferCreate,
    _: Admin,
    db: DB,
):
    """Create a new product discount offer."""
    return await OfferService(db).create(payload)


@router.patch("/offers/{offer_id}", response_model=OfferOut)
async def update_offer(
    offer_id: UUID,
    payload: OfferUpdate,
    _: Admin,
    db: DB,
):
    """Partially update an existing offer."""
    return await OfferService(db).update(offer_id, payload)


@router.patch("/offers/{offer_id}/deactivate", response_model=OfferOut)
async def deactivate_offer(
    offer_id: UUID,
    _: Admin,
    db: DB,
):
    """Immediately deactivate an offer."""
    return await OfferService(db).deactivate(offer_id)


# ── Banners ───────────────────────────────────────────────────────────────────

@router.get("/banners", response_model=list[BannerOut])
async def list_banners(
    _: Admin,
    db: DB,
):
    """Return all banners (active and inactive)."""
    from app.repositories.notification_repository import BannerRepository
    return await BannerRepository(db).list(0, 200)


@router.post("/banners", response_model=BannerOut, status_code=status.HTTP_201_CREATED)
async def create_banner(
    payload: BannerCreate,
    _: Admin,
    db: DB,
):
    """Create a new home-screen banner."""
    return await BannerService(db).create(payload)


@router.patch("/banners/{banner_id}", response_model=BannerOut)
async def update_banner(
    banner_id: UUID,
    payload: BannerUpdate,
    _: Admin,
    db: DB,
):
    """Partially update a banner."""
    return await BannerService(db).update(banner_id, payload)


@router.patch("/banners/{banner_id}/toggle", response_model=BannerOut)
async def toggle_banner(
    banner_id: UUID,
    is_active: bool,
    _: Admin,
    db: DB,
):
    """Activate or deactivate a banner."""
    return await BannerService(db).toggle(banner_id, is_active)


@router.post("/banners/upload-image")
async def upload_banner_image(
    admin: Admin,
    db: DB,
    file: UploadFile = File(...),
):
    """
    Upload an image for a banner.
    
    Returns the file path/URL that can be used in the image_url field.
    Supports: JPG, JPEG, PNG, GIF, WEBP (max 5MB)
    
    File metadata is saved to the database for tracking.
    """
    try:
        from app.repositories.uploaded_file_repository import UploadedFileRepository
        from app.models.uploaded_file import UploadedFile
        from app.utils.file_upload import get_file_url
        
        # Save file to uploads/banners/
        file_metadata = await save_upload_file(file, subdir="banners")
        file_path = file_metadata["file_path"]
        
        # Create a database record (only path, URL constructed at runtime)
        uploaded_file = UploadedFile(
            entity_type="banner",
            entity_id=None,  # Not yet associated with a specific banner
            original_filename=file_metadata["original_filename"],
            file_path=file_path,
            file_url=file_path,  # Store path, construct URL at runtime
            file_size=file_metadata["file_size"],
            mime_type=file_metadata["mime_type"],
            uploaded_by=admin.id if hasattr(admin, 'id') else None,
        )
        file_record = await UploadedFileRepository(db).create(uploaded_file)
        await db.commit()
        
        # Construct full URL dynamically
        image_url = get_file_url(file_path)
        
        return {
            "image_url": image_url,
            "file_url": image_url,  # Alias for compatibility
            "url": image_url,  # Alias for compatibility
            "file_path": file_path,
            "filename": file_metadata["original_filename"],
            "file_size": file_metadata["file_size"],
            "mime_type": file_metadata["mime_type"],
            "server_url": settings.SERVER_URL,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Banner image upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ── App Settings ──────────────────────────────────────────────────────────────

@router.get("/settings", response_model=AppSettingsOut)
async def get_app_settings(
    _: Admin,
    db: DB,
):
    """Get all application settings."""
    from app.repositories.app_settings_repository import AppSettingsRepository
    return await AppSettingsRepository(db).get_settings()


@router.patch("/settings", response_model=AppSettingsOut)
async def update_app_settings(
    payload: AppSettingsUpdate,
    _: Admin,
    db: DB,
):
    """Update application settings."""
    from app.repositories.app_settings_repository import AppSettingsRepository
    
    update_data = payload.model_dump(exclude_unset=True)
    updated = await AppSettingsRepository(db).update_settings(update_data)
    await db.commit()
    return updated


@router.get("/settings/today-orders-count")
async def get_today_orders_count(
    _: Admin,
    db: DB,
):
    """Get the count of orders placed today (for monitoring order limits)."""
    from datetime import datetime, timezone
    
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await db.execute(
        select(func.count())
        .select_from(Order)
        .where(Order.created_at >= today_start)
    )
    today_count = result.scalar_one()
    
    from app.repositories.app_settings_repository import AppSettingsRepository
    s = await AppSettingsRepository(db).get_settings()
    
    return {
        "today_orders_count": today_count,
        "daily_order_limit": s.daily_order_limit,
        "order_limit_enabled": s.order_limit_enabled,
        "limit_reached": (
            s.order_limit_enabled 
            and s.daily_order_limit is not None 
            and today_count >= s.daily_order_limit
        ),
    }
