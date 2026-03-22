"""Centralised email service using fastapi-mail.

Provides helpers for OTP delivery, order invoices, and admin notifications.
"""
from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from app.core.config import settings

logger = logging.getLogger(__name__)


def _is_configured() -> bool:
    return bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD and settings.MAIL_FROM)


def _mail_config():
    """Build a fastapi-mail ConnectionConfig from settings."""
    from fastapi_mail import ConnectionConfig

    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
    )


async def _send_mail(subject: str, recipients: list[str], html_body: str) -> None:
    """Low-level send helper. Silently skips if SMTP is not configured."""
    if not _is_configured():
        logger.warning("Email not configured — skipping email delivery.")
        return
    if not recipients:
        return

    try:
        from fastapi_mail import FastMail, MessageSchema, MessageType

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_body,
            subtype=MessageType.html,
        )
        await FastMail(_mail_config()).send_message(message)
        logger.info("Email sent: %s → %s", subject, recipients)
    except Exception:
        logger.exception("Failed to send email: %s → %s", subject, recipients)


# ── OTP email ─────────────────────────────────────────────────────────────────

async def send_otp_email(email: str, code: str, *, store_name: str | None = None) -> None:
    """Send an OTP code to the given email address."""
    name = store_name or settings.PROJECT_NAME
    await _send_mail(
        subject=f"Your {name} OTP",
        recipients=[email],
        html_body=(
            f"<p>Your one-time password is:</p>"
            f"<h2 style='letter-spacing:4px'>{code}</h2>"
            f"<p>Valid for <strong>{settings.OTP_EXPIRE_MINUTES} minutes</strong>. "
            f"Do not share it with anyone.</p>"
        ),
    )


# ── Invoice email ─────────────────────────────────────────────────────────────

def _build_invoice_html(order: Any, store_name: str | None = None) -> str:
    """Build an HTML invoice for a completed order."""
    store = store_name or settings.PROJECT_NAME
    items_rows = ""
    for item in order.items:
        product_name = item.product.name if item.product else str(item.product_id)
        items_rows += (
            f"<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #eee'>{product_name}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:center'>{item.quantity}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>₹{item.unit_price:.2f}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>₹{item.subtotal:.2f}</td>"
            f"</tr>"
        )

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
        <div style="text-align:center;margin-bottom:20px">
            <h1 style="color:#4CAF50;margin:0">{store}</h1>
            <p style="color:#666;margin:5px 0">Order Invoice</p>
        </div>

        <div style="background:#f9f9f9;padding:15px;border-radius:8px;margin-bottom:20px">
            <p style="margin:5px 0"><strong>Order ID:</strong> {order.id}</p>
            <p style="margin:5px 0"><strong>Status:</strong> {order.status.value}</p>
            <p style="margin:5px 0"><strong>Delivery Address:</strong> {order.delivery_address}</p>
        </div>

        <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
            <thead>
                <tr style="background:#4CAF50;color:white">
                    <th style="padding:10px;text-align:left">Product</th>
                    <th style="padding:10px;text-align:center">Qty</th>
                    <th style="padding:10px;text-align:right">Price</th>
                    <th style="padding:10px;text-align:right">Subtotal</th>
                </tr>
            </thead>
            <tbody>{items_rows}</tbody>
        </table>

        <div style="text-align:right;margin-bottom:20px">
            <p style="margin:5px 0">Subtotal: <strong>₹{order.subtotal:.2f}</strong></p>
            <p style="margin:5px 0">Delivery: <strong>₹{order.delivery_charge:.2f}</strong></p>
            <hr style="border:1px solid #4CAF50">
            <p style="font-size:18px;margin:5px 0">Total: <strong style="color:#4CAF50">₹{order.total:.2f}</strong></p>
        </div>

        <p style="text-align:center;color:#999;font-size:12px">
            Thank you for shopping with {store}!
        </p>
    </div>
    """


async def send_invoice_email(email: str, order: Any, *, store_name: str | None = None) -> None:
    """Send an order invoice to the customer's email."""
    name = store_name or settings.PROJECT_NAME
    await _send_mail(
        subject=f"Invoice for Order #{order.id} — {name}",
        recipients=[email],
        html_body=_build_invoice_html(order, store_name=name),
    )


# ── Admin notification email ─────────────────────────────────────────────────

def _build_admin_order_email_html(order: Any, event: str, store_name: str | None = None) -> str:
    """Build a professional HTML email template for admin order notifications."""
    store = store_name or settings.PROJECT_NAME
    # Event-specific styling
    event_colors = {
        "New Order Placed": {"bg": "#4CAF50", "icon": "🛎️"},
        "Order Cancelled": {"bg": "#F44336", "icon": "❌"},
        "Order Status": {"bg": "#2196F3", "icon": "📦"},
    }
    
    # Default to orange for unknown events
    event_style = event_colors.get(event, {"bg": "#FF9800", "icon": "🔔"})
    
    # Build order items table (without extra indentation)
    items_html = ""
    for item in order.items:
        product_name = item.product.name if item.product else str(item.product_id)
        items_html += f"""<tr>
<td style="padding:12px 8px;border-bottom:1px solid #e0e0e0;color:#333">{product_name}</td>
<td style="padding:12px 8px;border-bottom:1px solid #e0e0e0;text-align:center;color:#666">{item.quantity}</td>
<td style="padding:12px 8px;border-bottom:1px solid #e0e0e0;text-align:right;color:#666">₹{item.unit_price:.2f}</td>
<td style="padding:12px 8px;border-bottom:1px solid #e0e0e0;text-align:right;color:#333;font-weight:600">₹{item.subtotal:.2f}</td>
</tr>"""
    
    # Get customer info
    customer_name = order.user.full_name if hasattr(order, 'user') and order.user else "N/A"
    customer_phone = order.user.phone if hasattr(order, 'user') and order.user else "N/A"
    customer_email = order.user.email if hasattr(order, 'user') and order.user and order.user.email else "N/A"
    
    # Build conditional sections (without indentation to avoid HTML rendering issues)
    cancel_reason_section = ""
    if order.cancel_reason:
        cancel_reason_section = f"""<div style="margin-top:20px;padding:16px;background:#ffebee;border-left:4px solid #F44336;border-radius:4px">
<p style="margin:0;color:#c62828;font-size:14px;font-weight:600">Cancel Reason:</p>
<p style="margin:8px 0 0;color:#666;font-size:14px">{order.cancel_reason}</p>
</div>"""
    
    notes_section = ""
    if order.notes:
        notes_section = f"""<div style="margin-top:20px">
<h4 style="margin:0 0 8px;color:#666;font-size:14px;font-weight:600">Order Notes:</h4>
<p style="margin:0;color:#555;font-size:13px;font-style:italic;padding:12px;background:#f9f9f9;border-radius:4px">{order.notes}</p>
</div>"""
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:20px 0">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background:{event_style['bg']};padding:30px;text-align:center">
                            <div style="font-size:36px;margin-bottom:10px">{event_style['icon']}</div>
                            <h1 style="margin:0;color:white;font-size:24px;font-weight:600">{event}</h1>
                            <p style="margin:8px 0 0;color:rgba(255,255,255,0.9);font-size:14px">{store} Admin Notification</p>
                        </td>
                    </tr>
                    
                    <!-- Order Summary Card -->
                    <tr>
                        <td style="padding:30px">
                            <div style="background:#f9f9f9;border-left:4px solid {event_style['bg']};padding:20px;border-radius:4px;margin-bottom:24px">
                                <h2 style="margin:0 0 16px;color:#333;font-size:18px;font-weight:600">Order Summary</h2>
                                <table width="100%" cellpadding="4" cellspacing="0">
                                    <tr>
                                        <td style="color:#666;font-size:14px;padding:4px 0">Order ID:</td>
                                        <td style="color:#333;font-size:14px;font-weight:600;text-align:right;padding:4px 0">{order.id}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px;padding:4px 0">Status:</td>
                                        <td style="text-align:right;padding:4px 0">
                                            <span style="background:{event_style['bg']};color:white;padding:4px 12px;border-radius:12px;font-size:12px;font-weight:600;text-transform:uppercase">{order.status.value}</span>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px;padding:4px 0">Order Total:</td>
                                        <td style="color:#4CAF50;font-size:18px;font-weight:700;text-align:right;padding:4px 0">₹{order.total:.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px;padding:4px 0">Items Count:</td>
                                        <td style="color:#333;font-size:14px;font-weight:600;text-align:right;padding:4px 0">{len(order.items)} item(s)</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Customer Information -->
                            <div style="margin-bottom:24px">
                                <h3 style="margin:0 0 12px;color:#333;font-size:16px;font-weight:600;border-bottom:2px solid #e0e0e0;padding-bottom:8px">Customer Information</h3>
                                <table width="100%" cellpadding="6" cellspacing="0">
                                    <tr>
                                        <td style="color:#666;font-size:14px;width:120px">Name:</td>
                                        <td style="color:#333;font-size:14px;font-weight:500">{customer_name}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px">Phone:</td>
                                        <td style="color:#333;font-size:14px;font-weight:500">{customer_phone}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px">Email:</td>
                                        <td style="color:#333;font-size:14px;font-weight:500">{customer_email}</td>
                                    </tr>
                                </table>
                            </div>
                            
                            <!-- Delivery Address -->
                            <div style="margin-bottom:24px">
                                <h3 style="margin:0 0 12px;color:#333;font-size:16px;font-weight:600;border-bottom:2px solid #e0e0e0;padding-bottom:8px">Delivery Address</h3>
                                <p style="margin:0;color:#555;font-size:14px;line-height:1.6;padding:8px 12px;background:#f9f9f9;border-radius:4px">{order.delivery_address}</p>
                            </div>
                            
                            <!-- Order Items -->
                            <div style="margin-bottom:24px">
                                <h3 style="margin:0 0 12px;color:#333;font-size:16px;font-weight:600;border-bottom:2px solid #e0e0e0;padding-bottom:8px">Order Items</h3>
                                <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e0e0e0;border-radius:4px;overflow:hidden">
                                    <thead>
                                        <tr style="background:#f5f5f5">
                                            <th style="padding:12px 8px;text-align:left;color:#666;font-size:12px;font-weight:600;text-transform:uppercase">Product</th>
                                            <th style="padding:12px 8px;text-align:center;color:#666;font-size:12px;font-weight:600;text-transform:uppercase">Qty</th>
                                            <th style="padding:12px 8px;text-align:right;color:#666;font-size:12px;font-weight:600;text-transform:uppercase">Price</th>
                                            <th style="padding:12px 8px;text-align:right;color:#666;font-size:12px;font-weight:600;text-transform:uppercase">Subtotal</th>
                                        </tr>
                                    </thead>
                                    <tbody>
{items_html}
                                    </tbody>
                                </table>
                            </div>
                            
                            <!-- Order Totals -->
                            <div style="background:#f9f9f9;padding:16px;border-radius:4px">
                                <table width="100%" cellpadding="4" cellspacing="0">
                                    <tr>
                                        <td style="color:#666;font-size:14px;text-align:right;padding:4px 0">Subtotal:</td>
                                        <td style="color:#333;font-size:14px;font-weight:600;text-align:right;width:100px;padding:4px 0">₹{order.subtotal:.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#666;font-size:14px;text-align:right;padding:4px 0">Delivery Charge:</td>
                                        <td style="color:#333;font-size:14px;font-weight:600;text-align:right;padding:4px 0">₹{order.delivery_charge:.2f}</td>
                                    </tr>
                                    <tr>
                                        <td style="color:#333;font-size:16px;font-weight:600;text-align:right;padding:12px 0 4px;border-top:2px solid #e0e0e0">Total:</td>
                                        <td style="color:#4CAF50;font-size:20px;font-weight:700;text-align:right;padding:12px 0 4px;border-top:2px solid #e0e0e0">₹{order.total:.2f}</td>
                                    </tr>
                                </table>
                            </div>
                            
                            {cancel_reason_section}
                            
                            {notes_section}
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background:#f5f5f5;padding:24px;text-align:center;border-top:1px solid #e0e0e0">
                            <p style="margin:0 0 8px;color:#999;font-size:12px">This is an automated admin notification from <strong>{store}</strong></p>
                            <p style="margin:0;color:#999;font-size:11px">Please do not reply directly to this email.</p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
    """


async def send_admin_order_email(
    admin_emails: list[str], order: Any, event: str = "New Order", *, store_name: str | None = None
) -> None:
    """Notify admin users about an order event via email with a professional template."""
    if not admin_emails:
        return
    name = store_name or settings.PROJECT_NAME
    await _send_mail(
        subject=f"🔔 {event}: Order #{order.id} — {name}",
        recipients=admin_emails,
        html_body=_build_admin_order_email_html(order, event, store_name=name),
    )


# ── Customer order status email ──────────────────────────────────────────────

def _build_customer_order_status_html(order: Any, event: str, store_name: str | None = None) -> str:
    """Build an HTML email for customer order status updates."""
    store = store_name or settings.PROJECT_NAME

    status_info = {
        "confirmed": {"color": "#4CAF50", "icon": "✅", "message": "Your order has been confirmed!"},
        "packed": {"color": "#2196F3", "icon": "📦", "message": "Your order has been packed and is ready for dispatch!"},
        "out_for_delivery": {"color": "#FF9800", "icon": "🚚", "message": "Your order is out for delivery!"},
        "delivered": {"color": "#4CAF50", "icon": "🎉", "message": "Your order has been delivered!"},
        "cancelled": {"color": "#F44336", "icon": "❌", "message": "Your order has been cancelled."},
    }
    info = status_info.get(order.status.value, {"color": "#2196F3", "icon": "📦", "message": "Your order status has been updated."})

    items_rows = ""
    for item in order.items:
        product_name = item.product.name if item.product else str(item.product_id)
        items_rows += (
            f"<tr>"
            f"<td style='padding:8px;border-bottom:1px solid #eee'>{product_name}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:center'>{item.quantity}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>₹{item.unit_price:.2f}</td>"
            f"<td style='padding:8px;border-bottom:1px solid #eee;text-align:right'>₹{item.subtotal:.2f}</td>"
            f"</tr>"
        )

    cancel_section = ""
    if order.cancel_reason:
        cancel_section = f"""<div style="margin-top:15px;padding:12px;background:#ffebee;border-left:4px solid #F44336;border-radius:4px">
<p style="margin:0;color:#c62828;font-size:14px"><strong>Reason:</strong> {order.cancel_reason}</p>
</div>"""

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
        <div style="text-align:center;margin-bottom:20px">
            <h1 style="color:{info['color']};margin:0">{store}</h1>
        </div>
        <div style="text-align:center;padding:20px;background:{info['color']};border-radius:8px;margin-bottom:20px">
            <div style="font-size:36px;margin-bottom:10px">{info['icon']}</div>
            <h2 style="color:white;margin:0">{event}</h2>
            <p style="color:rgba(255,255,255,0.9);margin:8px 0 0">{info['message']}</p>
        </div>
        <div style="background:#f9f9f9;padding:15px;border-radius:8px;margin-bottom:20px">
            <p style="margin:5px 0"><strong>Order ID:</strong> {order.id}</p>
            <p style="margin:5px 0"><strong>Status:</strong> {order.status.value.replace('_', ' ').title()}</p>
            <p style="margin:5px 0"><strong>Delivery Address:</strong> {order.delivery_address}</p>
        </div>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
            <thead>
                <tr style="background:{info['color']};color:white">
                    <th style="padding:10px;text-align:left">Product</th>
                    <th style="padding:10px;text-align:center">Qty</th>
                    <th style="padding:10px;text-align:right">Price</th>
                    <th style="padding:10px;text-align:right">Subtotal</th>
                </tr>
            </thead>
            <tbody>{items_rows}</tbody>
        </table>
        <div style="text-align:right;margin-bottom:20px">
            <p style="margin:5px 0">Subtotal: <strong>₹{order.subtotal:.2f}</strong></p>
            <p style="margin:5px 0">Delivery: <strong>₹{order.delivery_charge:.2f}</strong></p>
            <hr style="border:1px solid {info['color']}">
            <p style="font-size:18px;margin:5px 0">Total: <strong style="color:{info['color']}">₹{order.total:.2f}</strong></p>
        </div>
        {cancel_section}
        <p style="text-align:center;color:#999;font-size:12px">
            Thank you for shopping with {store}!
        </p>
    </div>
    """


async def send_order_status_email(
    email: str, order: Any, event: str = "Order Update", *, store_name: str | None = None
) -> None:
    """Send an order status update email to the customer."""
    name = store_name or settings.PROJECT_NAME
    await _send_mail(
        subject=f"{event}: Order #{order.id} — {name}",
        recipients=[email],
        html_body=_build_customer_order_status_html(order, event, store_name=name),
    )
