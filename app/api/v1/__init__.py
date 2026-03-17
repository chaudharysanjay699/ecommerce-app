from fastapi import APIRouter

from app.api.v1 import admin, auth, cart, notifications, offers, orders, products, tracking, wishlist

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(tracking.router)
api_router.include_router(offers.router)
api_router.include_router(notifications.router)
api_router.include_router(wishlist.router)
api_router.include_router(admin.router)
