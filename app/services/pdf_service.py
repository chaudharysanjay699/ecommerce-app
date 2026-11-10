"""PDF generation service for invoices and shipping labels.

Uses xhtml2pdf to convert HTML templates to PDF documents.
Generated PDFs are saved to the uploads directory and URLs are stored on the order.
"""
from __future__ import annotations

import logging
import os
from html import escape
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

def build_invoice_html(order: Any, store_name: str | None = None,
                       app_settings: Any | None = None, language: str = "en") -> str:
    """Build a print-ready, India GST-compliant tax invoice HTML."""
    labels = {
        "en": {
            "tax_invoice": "Tax Invoice",
            "invoice_number": "Invoice #",
            "date": "Date",
            "order_id": "Order ID",
            "sold_by": "Sold By",
            "bill_to": "Bill To",
            "ship_to": "Ship To",
            "phone": "Phone",
            "email": "Email",
            "state": "State",
            "code": "Code",
            "product": "Product",
            "hsn": "HSN",
            "quantity": "Qty",
            "rate": "Rate",
            "discount_abbrev": "Disc.",
            "taxable": "Taxable",
            "gst_rate": "GST%",
            "cgst_abbrev": "CGST",
            "sgst_abbrev": "SGST",
            "total": "Total",
            "subtotal_before_tax": "Subtotal (before tax):",
            "discount": "Discount:",
            "cgst": "CGST:",
            "sgst": "SGST:",
            "delivery_charge": "Delivery Charge:",
            "grand_total": "Grand Total:",
            "payment_method": "Payment Method:",
            "payment_status": "Payment Status:",
            "terms": "Terms &amp; Conditions",
            "authorised_signatory": "Authorised Signatory",
            "thank_you": "Thank you for shopping with",
            "computer_generated": (
                "This is a computer-generated invoice and does not require a physical signature."
            ),
        },
        "hi": {
            "tax_invoice": "कर चालान",
            "invoice_number": "चालान संख्या",
            "date": "दिनांक",
            "order_id": "ऑर्डर आईडी",
            "sold_by": "विक्रेता",
            "bill_to": "बिल प्राप्तकर्ता",
            "ship_to": "डिलीवरी का पता",
            "phone": "फोन",
            "email": "ईमेल",
            "state": "राज्य",
            "code": "कोड",
            "product": "उत्पाद",
            "hsn": "एचएसएन",
            "quantity": "मात्रा",
            "rate": "दर",
            "discount_abbrev": "छूट",
            "taxable": "कर योग्य राशि",
            "gst_rate": "GST%",
            "cgst_abbrev": "केंद्रीय GST",
            "sgst_abbrev": "राज्य GST",
            "total": "कुल",
            "subtotal_before_tax": "कर से पहले उप-योग:",
            "discount": "छूट:",
            "cgst": "केंद्रीय GST:",
            "sgst": "राज्य GST:",
            "delivery_charge": "डिलीवरी शुल्क:",
            "grand_total": "कुल राशि:",
            "payment_method": "भुगतान का तरीका:",
            "payment_status": "भुगतान की स्थिति:",
            "terms": "नियम और शर्तें",
            "authorised_signatory": "अधिकृत हस्ताक्षरकर्ता",
            "thank_you": "से खरीदारी करने के लिए धन्यवाद",
            "computer_generated": (
                "यह कंप्यूटर द्वारा बनाया गया चालान है और इस पर भौतिक हस्ताक्षर की आवश्यकता नहीं है।"
            ),
        },
    }[language]
    is_hindi = language == "hi"

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
    default_terms = (
        "एक बार बेचा गया सामान वापस या बदला नहीं जाएगा। "
        "त्रुटियों और चूकों के लिए क्षमा।"
        if is_hindi
        else "Goods once sold will not be taken back or exchanged. "
        "E&OE - Errors and Omissions Excepted."
    )
    invoice_terms = _safe(getattr(s, "invoice_terms", None), default_terms)

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
    if is_hindi:
        payment_methods_hi = {
            "cash on delivery": "कैश ऑन डिलीवरी",
            "cod": "कैश ऑन डिलीवरी",
            "online": "ऑनलाइन",
            "upi": "यूपीआई",
        }
        payment_statuses_hi = {
            "pending": "लंबित",
            "paid": "भुगतान किया गया",
            "failed": "विफल",
            "refunded": "वापस किया गया",
            "completed": "पूर्ण",
        }
        payment_method = payment_methods_hi.get(payment_method.lower(), payment_method)
        payment_status = payment_statuses_hi.get(payment_status.lower(), payment_status)

    # ── Line items ────────────────────────────────────────────────────────
    items_rows = ""
    total_discount = 0.0
    total_taxable = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_tax = 0.0

    for idx, item in enumerate(order.items, 1):
        if item.product:
            product_name = (
                getattr(item.product, "name_hi", None) or item.product.name
                if is_hindi
                else item.product.name
            )
        else:
            product_name = str(item.product_id)
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
        seller_details += f"{labels['phone']}: {seller_phone}<br/>"
    if seller_email:
        seller_details += f"{labels['email']}: {seller_email}<br/>"
    if seller_gstin:
        seller_details += f"<strong>GSTIN:</strong> {seller_gstin}<br/>"
    if seller_pan:
        seller_details += f"<strong>PAN:</strong> {seller_pan}<br/>"
    if seller_state:
        state_line = f"{labels['state']}: {seller_state}"
        if seller_state_code:
            state_line += f" ({labels['code']}: {seller_state_code})"
        seller_details += state_line

    return f"""<!DOCTYPE html>
<html lang="{'hi' if is_hindi else 'en'}">
<head>
<meta charset="UTF-8">
<style>
    @page {{ size: A4; margin: {'0' if is_hindi else '15mm'}; }}
    body {{ font-family: {'"Noto Sans Devanagari", "Nirmala UI", Mangal,' if is_hindi else ''} Helvetica, Arial, sans-serif; color: #333; font-size: 11px; margin: 0; padding: {'15mm' if is_hindi else '0'}; }}
    @media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}

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
                    <div class="inv-subtitle">{labels['tax_invoice']}</div>
                    <div style="font-size:11px; color:#555; margin-top:4px;">
                        <strong>{labels['invoice_number']}:</strong> {invoice_number}<br/>
                        <strong>{labels['date']}:</strong> {created}<br/>
                        <strong>{labels['order_id']}:</strong> {str(order.id)[:8].upper()}
                    </div>
                </td>
            </tr>
        </table>
    </div>

    <!-- SELLER / BUYER / SHIPPING -->
    <table class="info-table">
        <tr>
            <td style="width:33%; border-right:1px solid #ddd;">
                <div class="info-label">{labels['sold_by']}</div>
                <div class="info-val">{seller_details}</div>
            </td>
            <td style="width:33%; border-right:1px solid #ddd; padding-left:12px;">
                <div class="info-label">{labels['bill_to']}</div>
                <div class="info-val">
                    <strong>{customer_name}</strong><br/>
                    {labels['phone']}: {customer_phone}<br/>
                    {f"{labels['email']}: {customer_email}<br/>" if customer_email else ""}
                </div>
            </td>
            <td style="width:34%; padding-left:12px;">
                <div class="info-label">{labels['ship_to']}</div>
                <div class="info-val">
                    <strong>{customer_name}</strong><br/>
                    {order.delivery_address}<br/>
                    {labels['phone']}: {customer_phone}
                </div>
            </td>
        </tr>
    </table>

    <!-- LINE ITEMS -->
    <table class="items">
        <thead>
            <tr>
                <th style="width:4%">#</th>
                <th style="width:20%; text-align:left">{labels['product']}</th>
                <th style="width:8%">{labels['hsn']}</th>
                <th style="width:5%">{labels['quantity']}</th>
                <th style="width:9%">{labels['rate']}</th>
                <th style="width:9%">{labels['discount_abbrev']}</th>
                <th style="width:11%">{labels['taxable']}</th>
                <th style="width:7%">{labels['gst_rate']}</th>
                <th style="width:9%">{labels['cgst_abbrev']}</th>
                <th style="width:9%">{labels['sgst_abbrev']}</th>
                <th style="width:9%">{labels['total']}</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
        </tbody>
    </table>

    <!-- TOTALS -->
    <table class="totals-table">
        <tr>
            <td class="label">{labels['subtotal_before_tax']}</td>
            <td class="value">Rs.{total_taxable:.2f}</td>
        </tr>
        <tr>
            <td class="label">{labels['discount']}</td>
            <td class="value">- Rs.{total_discount:.2f}</td>
        </tr>
        <tr>
            <td class="label">{labels['cgst']}</td>
            <td class="value">Rs.{total_cgst:.2f}</td>
        </tr>
        <tr>
            <td class="label">{labels['sgst']}</td>
            <td class="value">Rs.{total_sgst:.2f}</td>
        </tr>
        <tr>
            <td class="label">{labels['delivery_charge']}</td>
            <td class="value">Rs.{float(order.delivery_charge):.2f}</td>
        </tr>
        <tr class="grand">
            <td class="label">{labels['grand_total']}</td>
            <td class="value">Rs.{float(order.total):.2f}</td>
        </tr>
    </table>

    <!-- PAYMENT -->
    <div class="payment-box">
        <span><strong>{labels['payment_method']}</strong> {payment_method}</span>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        <span><strong>{labels['payment_status']}</strong> {payment_status}</span>
    </div>

    <!-- FOOTER -->
    <div class="footer">
        <table style="width:100%">
            <tr>
                <td style="width:60%; vertical-align:top;">
                    <div class="info-label">{labels['terms']}</div>
                    <div class="terms">{invoice_terms}</div>
                </td>
                <td style="width:40%; vertical-align:top;">
                    <div class="sig">
                        For <strong>{seller_name}</strong><br/><br/><br/>
                        {labels['authorised_signatory']}
                    </div>
                </td>
            </tr>
        </table>
        <div class="thanks">{seller_name + ' ' + labels['thank_you'] if is_hindi else labels['thank_you'] + ' ' + seller_name}!</div>
        <div class="no-sig">{labels['computer_generated']}</div>
    </div>

</body>
</html>"""


# ── Shipping Label HTML ───────────────────────────────────────────────────────

def _build_shipping_label_html(
    order: Any,
    store_name: str | None = None,
    language: str = "en",
) -> str:
    is_hindi = language == "hi"
    store = store_name or settings.PROJECT_NAME

    customer_name = order.user.full_name if hasattr(order, "user") and order.user else "N/A"
    customer_phone = order.user.phone if hasattr(order, "user") and order.user else "N/A"

    items_summary = ", ".join(
        f"{(item.product.name_hi if is_hindi and item.product.name_hi else item.product.name) if item.product else 'वस्तु' if is_hindi else 'Item'} x{item.quantity}"
        for item in order.items
    )
    labels = {
        "en": {
            "shipping_label": "SHIPPING LABEL",
            "order": "ORDER",
            "ship_to": "Ship To",
            "phone": "Phone",
            "order_date": "Order Date",
            "items": "Items",
            "total": "TOTAL",
            "cash_on_delivery": "CASH ON DELIVERY",
        },
        "hi": {
            "shipping_label": "शिपिंग लेबल",
            "order": "ऑर्डर",
            "ship_to": "यहाँ भेजें",
            "phone": "फोन",
            "order_date": "ऑर्डर की तारीख",
            "items": "वस्तुएँ",
            "total": "कुल",
            "cash_on_delivery": "डिलीवरी पर नकद",
        },
    }[language]

    created = ""
    if hasattr(order, "created_at") and order.created_at:
        created = order.created_at.strftime("%d %b %Y")

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
<meta charset="UTF-8">
<style>
    @page {{ size: A4; margin: {'0' if is_hindi else '10mm'}; }}
    * {{ box-sizing: border-box; }}
    body {{ font-family: {'"Noto Sans Devanagari", "Nirmala UI", Mangal,' if is_hindi else ''} Helvetica, Arial, sans-serif; color: #333; font-size: 13px; margin: 0; padding: {'10mm' if is_hindi else '0'}; }}
    .label {{ border: 3px solid #222; padding: 16px; width: 100%; max-width: 100%; overflow-wrap: anywhere; }}
    .store-header {{ text-align: center; border-bottom: 3px dashed #222; padding-bottom: 14px; margin-bottom: 14px; }}
    .store-header h2 {{ margin: 0; font-size: 26px; letter-spacing: 2px; }}
    .store-header p {{ margin: 4px 0 0; color: #666; font-size: 13px; }}
    .order-id {{ text-align: center; font-size: 20px; font-weight: bold; background: #eee; padding: 10px; margin-bottom: 16px; letter-spacing: 2px; }}
    table.info {{ width: 100%; table-layout: fixed; border-collapse: collapse; margin-bottom: 10px; }}
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
            <h2>{escape(str(store))}</h2>
            <p>{labels['shipping_label']}</p>
        </div>

        <div class="order-id">{labels['order']} #{str(order.id)[:8].upper()}</div>

        <table class="info">
            <tr>
                <td style="width:50%">
                    <span class="label-key">{labels['ship_to']}</span><br/>
                    <span class="label-val"><strong>{escape(str(customer_name))}</strong><br/>
                    {escape(str(order.delivery_address))}<br/>
                    {labels['phone']}: {escape(str(customer_phone))}</span>
                </td>
                <td style="width:50%; text-align:right">
                    <span class="label-key">{labels['order_date']}</span><br/>
                    <span class="label-val">{escape(created)}</span>
                </td>
            </tr>
        </table>

        <table class="info">
            <tr>
                <td>
                    <span class="label-key">{labels['items']} ({len(order.items)})</span>
                    <div class="items-box">{escape(items_summary)}</div>
                </td>
            </tr>
        </table>

        <div class="total-box">{labels['total']}: Rs.{order.total:.2f}</div>

        <div class="cod-badge">{labels['cash_on_delivery']}</div>
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

    html = build_invoice_html(order, store_name, app_settings)

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
