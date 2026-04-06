"""PDF generation service for invoices and shipping labels.

Uses xhtml2pdf to convert HTML templates to PDF documents.
Generated PDFs are saved to the uploads directory and URLs are stored on the order.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any
from uuid import UUID

from app.core.config import settings

logger = logging.getLogger(__name__)

# Directory where generated PDFs are stored
PDF_DIR = Path(settings.UPLOAD_DIR) / "pdfs"
PDF_DIR.mkdir(parents=True, exist_ok=True)


def _pdf_url(filename: str) -> str:
    """Return the public URL for a generated PDF."""
    return f"{settings.SERVER_URL}/uploads/pdfs/{filename}"


def _safe(val: Any, default: str = "") -> str:
    """Return str(val) if truthy, else default."""
    return str(val) if val else default


# ── Invoice HTML (GST-compliant) ──────────────────────────────────────────────

def _build_invoice_pdf_html(order: Any, store_name: str | None = None,
                            app_settings: Any | None = None) -> str:
    """Build a production-ready, India GST-compliant tax invoice HTML."""

    # ── Seller details ────────────────────────────────────────────────────
    s = app_settings
    seller_name = (s.store_name if s else None) or store_name or settings.PROJECT_NAME
    seller_phone = _safe(getattr(s, "store_phone", None))
    seller_email = _safe(getattr(s, "store_email", None))
    seller_address = _safe(getattr(s, "store_address", None))
    seller_gstin = _safe(getattr(s, "store_gstin", None))
    seller_pan = _safe(getattr(s, "store_pan", None))
    seller_state = _safe(getattr(s, "store_state", None))
    seller_state_code = _safe(getattr(s, "store_state_code", None))
    invoice_terms = _safe(getattr(s, "invoice_terms", None),
                          "Goods once sold will not be taken back or exchanged. "
                          "E&OE - Errors and Omissions Excepted.")

    # ── Buyer details ─────────────────────────────────────────────────────
    customer_name = order.user.full_name if hasattr(order, "user") and order.user else "N/A"
    customer_phone = order.user.phone if hasattr(order, "user") and order.user else "N/A"
    customer_email = (
        order.user.email
        if hasattr(order, "user") and order.user and order.user.email
        else ""
    )

    # ── Invoice meta ──────────────────────────────────────────────────────
    invoice_number = _safe(getattr(order, "invoice_number", None), str(order.id)[:8].upper())
    created = ""
    if hasattr(order, "created_at") and order.created_at:
        created = order.created_at.strftime("%d %b %Y, %I:%M %p")
    payment_method = _safe(getattr(order, "payment_method", None), "Cash on Delivery")
    payment_status = _safe(getattr(order, "payment_status", None), "Pending")

    # ── Line items ────────────────────────────────────────────────────────
    items_rows = ""
    total_discount = 0.0
    total_taxable = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_tax = 0.0

    for idx, item in enumerate(order.items, 1):
        product_name = item.product.name if item.product else str(item.product_id)
        hsn = _safe(getattr(item, "hsn_code", None), "-")
        qty = item.quantity
        rate = float(item.unit_price)
        discount = float(getattr(item, "discount", 0) or 0)
        tax_rate = float(getattr(item, "tax_rate", 0) or 0)
        tax_amount = float(getattr(item, "tax_amount", 0) or 0)
        taxable_value = float(item.subtotal) - tax_amount
        half_tax = tax_amount / 2.0

        total_discount += discount * qty
        total_taxable += taxable_value
        total_cgst += half_tax
        total_sgst += half_tax
        total_tax += tax_amount

        items_rows += (
            f"<tr>"
            f"<td class='center'>{idx}</td>"
            f"<td>{product_name}</td>"
            f"<td class='center'>{hsn}</td>"
            f"<td class='center'>{qty}</td>"
            f"<td class='right'>Rs.{rate:.2f}</td>"
            f"<td class='right'>Rs.{discount * qty:.2f}</td>"
            f"<td class='right'>Rs.{taxable_value:.2f}</td>"
            f"<td class='center'>{tax_rate:.1f}%</td>"
            f"<td class='right'>Rs.{half_tax:.2f}</td>"
            f"<td class='right'>Rs.{half_tax:.2f}</td>"
            f"<td class='right'>Rs.{float(item.subtotal):.2f}</td>"
            f"</tr>"
        )

    # ── Seller info block ─────────────────────────────────────────────────
    seller_details = f"<strong>{seller_name}</strong><br/>"
    if seller_address:
        seller_details += f"{seller_address}<br/>"
    if seller_phone:
        seller_details += f"Phone: {seller_phone}<br/>"
    if seller_email:
        seller_details += f"Email: {seller_email}<br/>"
    if seller_gstin:
        seller_details += f"<strong>GSTIN:</strong> {seller_gstin}<br/>"
    if seller_pan:
        seller_details += f"<strong>PAN:</strong> {seller_pan}<br/>"
    if seller_state:
        state_line = f"State: {seller_state}"
        if seller_state_code:
            state_line += f" (Code: {seller_state_code})"
        seller_details += state_line

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: Helvetica, Arial, sans-serif; color: #333; font-size: 11px; margin: 0; padding: 0; }}

    /* Header */
    .inv-header {{ border-bottom: 3px solid #2E7D32; padding-bottom: 8px; margin-bottom: 10px; }}
    .inv-header table {{ width: 100%; }}
    .inv-header td {{ vertical-align: top; padding: 0; }}
    .inv-title {{ font-size: 22px; font-weight: bold; color: #2E7D32; }}
    .inv-subtitle {{ font-size: 14px; color: #555; margin-top: 2px; text-transform: uppercase; letter-spacing: 2px; }}

    /* Info blocks */
    .info-table {{ width: 100%; margin-bottom: 8px; }}
    .info-table td {{ vertical-align: top; padding: 6px 8px; }}
    .info-label {{ font-size: 10px; text-transform: uppercase; color: #888; letter-spacing: 1px; font-weight: bold; margin-bottom: 3px; }}
    .info-val {{ font-size: 11px; color: #222; line-height: 1.5; }}

    /* Items table */
    .items {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 10px; }}
    .items th {{ background: #2E7D32; color: white; padding: 6px 4px; text-align: center; font-size: 9px; text-transform: uppercase; }}
    .items td {{ padding: 5px 4px; border-bottom: 1px solid #e0e0e0; }}
    .items tr:nth-child(even) td {{ background: #f9f9f9; }}
    .center {{ text-align: center; }}
    .right {{ text-align: right; }}

    /* Totals */
    .totals-table {{ width: 40%; margin-left: 60%; border-collapse: collapse; margin-bottom: 10px; }}
    .totals-table td {{ padding: 4px 8px; font-size: 11px; }}
    .totals-table .label {{ text-align: right; color: #555; }}
    .totals-table .value {{ text-align: right; font-weight: bold; }}
    .totals-table .grand td {{ border-top: 2px solid #2E7D32; font-size: 14px; color: #2E7D32; padding-top: 6px; }}

    /* Payment */
    .payment-box {{ background: #f5f5f5; padding: 8px 12px; margin-bottom: 10px; border-left: 4px solid #2E7D32; }}
    .payment-box span {{ font-size: 11px; }}

    /* Footer */
    .footer {{ border-top: 2px solid #2E7D32; padding-top: 8px; margin-top: 14px; }}
    .footer .terms {{ font-size: 9px; color: #777; line-height: 1.4; }}
    .footer .thanks {{ text-align: center; font-size: 12px; color: #2E7D32; font-weight: bold; margin-top: 8px; }}
    .footer .sig {{ text-align: right; margin-top: 20px; font-size: 10px; color: #555; }}
    .no-sig {{ font-size: 9px; color: #999; text-align: center; margin-top: 4px; }}
</style>
</head>
<body>

    <!-- HEADER -->
    <div class="inv-header">
        <table>
            <tr>
                <td style="width:60%">
                    <div class="inv-title">{seller_name}</div>
                </td>
                <td style="width:40%; text-align:right">
                    <div class="inv-subtitle">Tax Invoice</div>
                    <div style="font-size:11px; color:#555; margin-top:4px;">
                        <strong>Invoice #:</strong> {invoice_number}<br/>
                        <strong>Date:</strong> {created}<br/>
                        <strong>Order ID:</strong> {str(order.id)[:8].upper()}
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <!-- SELLER / BUYER / SHIPPING -->
    <table class="info-table">
        <tr>
            <td style="width:33%; border-right:1px solid #ddd;">
                <div class="info-label">Sold By</div>
                <div class="info-val">{seller_details}</div>
            </td>
            <td style="width:33%; border-right:1px solid #ddd; padding-left:12px;">
                <div class="info-label">Bill To</div>
                <div class="info-val">
                    <strong>{customer_name}</strong><br/>
                    Phone: {customer_phone}<br/>
                    {f"Email: {customer_email}<br/>" if customer_email else ""}
                </div>
            </td>
            <td style="width:34%; padding-left:12px;">
                <div class="info-label">Ship To</div>
                <div class="info-val">
                    <strong>{customer_name}</strong><br/>
                    {order.delivery_address}<br/>
                    Phone: {customer_phone}
                </div>
            </td>
        </tr>
    </table>

    <!-- LINE ITEMS -->
    <table class="items">
        <thead>
            <tr>
                <th style="width:4%">#</th>
                <th style="width:20%; text-align:left">Product</th>
                <th style="width:8%">HSN</th>
                <th style="width:5%">Qty</th>
                <th style="width:9%">Rate</th>
                <th style="width:9%">Disc.</th>
                <th style="width:11%">Taxable</th>
                <th style="width:7%">GST%</th>
                <th style="width:9%">CGST</th>
                <th style="width:9%">SGST</th>
                <th style="width:9%">Total</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
        </tbody>
    </table>

    <!-- TOTALS -->
    <table class="totals-table">
        <tr>
            <td class="label">Subtotal (before tax):</td>
            <td class="value">Rs.{total_taxable:.2f}</td>
        </tr>
        <tr>
            <td class="label">Discount:</td>
            <td class="value">- Rs.{total_discount:.2f}</td>
        </tr>
        <tr>
            <td class="label">CGST:</td>
            <td class="value">Rs.{total_cgst:.2f}</td>
        </tr>
        <tr>
            <td class="label">SGST:</td>
            <td class="value">Rs.{total_sgst:.2f}</td>
        </tr>
        <tr>
            <td class="label">Delivery Charge:</td>
            <td class="value">Rs.{float(order.delivery_charge):.2f}</td>
        </tr>
        <tr class="grand">
            <td class="label">Grand Total:</td>
            <td class="value">Rs.{float(order.total):.2f}</td>
        </tr>
    </table>

    <!-- PAYMENT -->
    <div class="payment-box">
        <span><strong>Payment Method:</strong> {payment_method}</span>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <span><strong>Payment Status:</strong> {payment_status}</span>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <table style="width:100%">
            <tr>
                <td style="width:60%; vertical-align:top;">
                    <div class="info-label">Terms &amp; Conditions</div>
                    <div class="terms">{invoice_terms}</div>
                </td>
                <td style="width:40%; vertical-align:top;">
                    <div class="sig">
                        For <strong>{seller_name}</strong><br/><br/><br/>
                        Authorised Signatory
                    </div>
                </td>
            </tr>
        </table>
        <div class="thanks">Thank you for shopping with {seller_name}!</div>
        <div class="no-sig">This is a computer-generated invoice and does not require a physical signature.</div>
    </div>

</body>
</html>"""


# ── Shipping Label HTML ───────────────────────────────────────────────────────

def _build_shipping_label_html(order: Any, store_name: str | None = None) -> str:
    store = store_name or settings.PROJECT_NAME

    customer_name = order.user.full_name if hasattr(order, "user") and order.user else "N/A"
    customer_phone = order.user.phone if hasattr(order, "user") and order.user else "N/A"

    items_summary = ", ".join(
        f"{item.product.name if item.product else 'Item'} x{item.quantity}"
        for item in order.items
    )

    created = ""
    if hasattr(order, "created_at") and order.created_at:
        created = order.created_at.strftime("%d %b %Y")

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: Helvetica, Arial, sans-serif; color: #333; font-size: 13px; margin: 0; padding: 0; }}
    .label {{ border: 3px solid #222; padding: 20px; width: 100%; }}
    .store-header {{ text-align: center; border-bottom: 3px dashed #222; padding-bottom: 14px; margin-bottom: 14px; }}
    .store-header h2 {{ margin: 0; font-size: 26px; letter-spacing: 2px; }}
    .store-header p {{ margin: 4px 0 0; color: #666; font-size: 13px; }}
    .order-id {{ text-align: center; font-size: 20px; font-weight: bold; background: #eee; padding: 10px; margin-bottom: 16px; letter-spacing: 2px; }}
    table.info {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; }}
    table.info td {{ padding: 6px 8px; vertical-align: top; font-size: 13px; }}
    .label-key {{ color: #888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; font-weight: bold; }}
    .label-val {{ color: #222; font-size: 14px; }}
    .label-val strong {{ font-size: 15px; }}
    .items-box {{ font-size: 12px; color: #444; background: #f9f9f9; padding: 8px 10px; margin-top: 4px; }}
    .total-box {{ text-align: center; font-size: 22px; font-weight: bold; padding: 10px 0; margin: 10px 0; border-top: 2px solid #222; border-bottom: 2px solid #222; }}
    .cod-badge {{ text-align: center; background: #222; color: white; padding: 10px; font-weight: bold; font-size: 16px; letter-spacing: 2px; }}
</style>
</head>
<body>
    <div class="label">
        <div class="store-header">
            <h2>{store}</h2>
            <p>SHIPPING LABEL</p>
        </div>

        <div class="order-id">ORDER #{str(order.id)[:8].upper()}</div>

        <table class="info">
            <tr>
                <td style="width:50%">
                    <span class="label-key">Ship To</span><br/>
                    <span class="label-val"><strong>{customer_name}</strong><br/>
                    {order.delivery_address}<br/>
                    Phone: {customer_phone}</span>
                </td>
                <td style="width:50%; text-align:right">
                    <span class="label-key">Order Date</span><br/>
                    <span class="label-val">{created}</span>
                </td>
            </tr>
        </table>

        <table class="info">
            <tr>
                <td>
                    <span class="label-key">Items ({len(order.items)})</span>
                    <div class="items-box">{items_summary}</div>
                </td>
            </tr>
        </table>

        <div class="total-box">Rs.{order.total:.2f}</div>

        <div class="cod-badge">CASH ON DELIVERY</div>
    </div>
</body>
</html>"""


# ── PDF Generation ────────────────────────────────────────────────────────────

def _generate_pdf(html: str, filepath: Path) -> None:
    """Render HTML to a PDF file using xhtml2pdf."""
    from xhtml2pdf import pisa

    with open(filepath, "wb") as f:
        pisa.CreatePDF(html, dest=f)


async def generate_invoice_pdf(order: Any, store_name: str | None = None,
                               app_settings: Any | None = None) -> str:
    """Generate an invoice PDF for the given order and return its public URL."""
    filename = f"invoice_{order.id}.pdf"
    filepath = PDF_DIR / filename

    html = _build_invoice_pdf_html(order, store_name, app_settings)

    import asyncio
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _generate_pdf, html, filepath)

    url = _pdf_url(filename)
    logger.info("Invoice PDF generated: %s", url)
    return url


async def generate_shipping_label_pdf(order: Any, store_name: str | None = None) -> str:
    """Generate a shipping label PDF for the given order and return its public URL."""
    filename = f"shipping_label_{order.id}.pdf"
    filepath = PDF_DIR / filename

    html = _build_shipping_label_html(order, store_name)

    import asyncio
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _generate_pdf, html, filepath)

    url = _pdf_url(filename)
    logger.info("Shipping label PDF generated: %s", url)
    return url
