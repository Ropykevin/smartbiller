import os
import io
from datetime import datetime, timedelta
from flask import current_app
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
import qrcode
import zipfile

from app import db
from app.models import Landlord, Property, Unit, Tenant, RentLog, UsageLog
from app.sms_service import send_sms
from app.subscription_service import SubscriptionService


def generate_custom_invoice(tenant, month, year, rent_amount, additional_charges=None, notes=None):
    """Generate a custom monthly invoice PDF for a tenant with variable amounts"""
    unit = tenant.unit
    property_ = unit.property
    
    # Create PDF buffer
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add watermark
    p.saveState()
    p.setFont("Helvetica-Bold", 60)
    p.setFillColor(HexColor("#E5E7EB"))  # Light gray
    p.setFillAlpha(0.3)  # 30% opacity
    p.rotate(45)
    p.drawCentredString(width/2 + 100, -height/2 + 100, "SMARTBILLER")
    p.restoreState()
    
    # Header with gradient-like effect
    p.setFillColor(HexColor("#1F2937"))  # Dark blue-gray
    p.rect(0, height - 120, width, 120, fill=1)
    
    # Header text in white
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawCentredString(width / 2, height - 50, "MONTHLY RENT INVOICE")
    
    # Invoice number and date
    p.setFont("Helvetica", 12)
    p.drawString(width - 200, height - 80, f"Invoice Date: {datetime.now().strftime('%B %d, %Y')}")
    p.drawString(width - 200, height - 95, f"Due Date: {month} 5, {year}")
    
    # Property and tenant info section with background
    p.setFillColor(HexColor("#F3F4F6"))  # Light gray background
    p.rect(50, height - 280, width - 100, 120, fill=1)
    
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#1F2937"))
    p.drawString(60, height - 200, "Property Information")
    
    p.setFont("Helvetica", 12)
    p.drawString(60, height - 220, f"Property: {property_.name}")
    p.drawString(60, height - 235, f"Location: {property_.location}")
    p.drawString(60, height - 250, f"Unit: {unit.unit_number}")
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(300, height - 200, "Tenant Information")
    
    p.setFont("Helvetica", 12)
    p.drawString(300, height - 220, f"Name: {tenant.name}")
    p.drawString(300, height - 235, f"Phone: {tenant.phone}")
    p.drawString(300, height - 250, f"Email: {tenant.email or 'Not provided'}")
    
    # Invoice period
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(HexColor("#059669"))  # Green
    p.drawString(60, height - 270, f"Invoice Period: {month} {year}")
    
    # Invoice details table
    y_position = height - 320
    
    # Table header
    p.setFillColor(HexColor("#374151"))  # Dark gray
    p.rect(50, y_position - 25, width - 100, 25, fill=1)
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawString(60, y_position - 15, "Description")
    p.drawString(350, y_position - 15, "Amount (KES)")
    
    # Table content
    p.setFillColor(HexColor("#FFFFFF"))
    p.rect(50, y_position - 50, width - 100, 25, fill=1)
    p.setFont("Helvetica", 12)
    p.setFillColor(HexColor("#1F2937"))
    p.drawString(60, y_position - 40, "Base Monthly Rent")
    p.drawString(350, y_position - 40, f"{rent_amount:,.2f}")
    
    # Additional charges
    total_amount = rent_amount
    y_position -= 75
    
    if additional_charges:
        for charge in additional_charges:
            p.setFillColor(HexColor("#F9FAFB"))  # Very light gray
            p.rect(50, y_position - 25, width - 100, 25, fill=1)
            p.setFont("Helvetica", 12)
            p.setFillColor(HexColor("#1F2937"))
            p.drawString(60, y_position - 15, f"  {charge['description']}")
            p.drawString(350, y_position - 15, f"{charge['amount']:,.2f}")
            total_amount += charge['amount']
            y_position -= 25
    
    # Total section with emphasis
    p.setFillColor(HexColor("#059669"))  # Green background
    p.rect(50, y_position - 25, width - 100, 25, fill=1)
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawString(60, y_position - 15, "TOTAL AMOUNT DUE")
    p.drawString(350, y_position - 15, f"{total_amount:,.2f}")
    
    # Payment status section
    y_position -= 50
    p.setFillColor(HexColor("#FEF3C7"))  # Light yellow background
    p.rect(50, y_position - 25, width - 100, 25, fill=1)
    
    # Check if payment already made
    existing_payment = RentLog.query.filter_by(
        tenant_id=tenant.id,
        month_paid_for=f"{month} {year}"
    ).first()
    
    if existing_payment:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(HexColor("#92400E"))  # Dark orange
        p.drawString(60, y_position - 15, f"Amount Paid: KES {existing_payment.amount_paid:,.2f}")
        p.drawString(350, y_position - 15, f"Balance: KES {total_amount - existing_payment.amount_paid:,.2f}")
        
        # Status indicator
        status_color = HexColor("#059669") if existing_payment.status == "Paid" else HexColor("#DC2626")
        p.setFillColor(status_color)
        p.circle(500, y_position - 12, 8, fill=1)
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(HexColor("#FFFFFF"))
        p.drawString(510, y_position - 15, existing_payment.status)
    else:
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(HexColor("#DC2626"))  # Red
        p.drawString(60, y_position - 15, "Status: UNPAID")
        p.drawString(350, y_position - 15, f"Amount Due: KES {total_amount:,.2f}")
    
    # Notes section
    if notes:
        y_position -= 50
        p.setFillColor(HexColor("#EFF6FF"))  # Light blue background
        p.rect(50, y_position - 40, width - 100, 40, fill=1)
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(HexColor("#1E40AF"))  # Blue
        p.drawString(60, y_position - 15, "Additional Notes:")
        p.setFont("Helvetica", 11)
        p.setFillColor(HexColor("#1F2937"))
        p.drawString(60, y_position - 30, notes)
    
    # Payment instructions section
    y_position -= 80
    p.setFillColor(HexColor("#F0FDF4"))  # Light green background
    p.rect(50, y_position - 60, width - 100, 60, fill=1)
    
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(HexColor("#059669"))  # Green
    p.drawString(60, y_position - 15, "Payment Instructions:")
    
    p.setFont("Helvetica", 11)
    p.setFillColor(HexColor("#1F2937"))
    p.drawString(60, y_position - 30, "• Please pay your rent by the 5th of each month to avoid late fees")
    p.drawString(60, y_position - 45, "• Payment methods: M-Pesa, Bank Transfer, Cash")
    contact_info = property_.landlord.phone or property_.landlord.email
    p.drawString(60, y_position - 60, f"• Contact: {contact_info}")
    
    # Footer with company branding
    p.setFillColor(HexColor("#1F2937"))
    p.rect(0, 0, width, 80, fill=1)
    
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawCentredString(width / 2, 50, "SmartBiller - Professional Property Management")
    
    p.setFont("Helvetica", 10)
    p.drawCentredString(width / 2, 35, "Making property management simple and efficient")
    p.drawCentredString(width / 2, 20, f"Invoice generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    p.showPage()
    p.save()
    buffer.seek(0)
    
    return buffer, total_amount


def send_custom_invoice_email(tenant, invoice_buffer, month, year, total_amount, additional_charges=None):
    """Send custom invoice via email"""
    from app import mail
    from flask_mail import Message
    
    try:
        # Build additional charges text
        additional_text = ""
        if additional_charges:
            additional_text = "\nAdditional Charges:\n"
            for charge in additional_charges:
                additional_text += f"- {charge['description']}: KES {charge['amount']:,.2f}\n"
        
        # Email body
        body = f"""
        Dear {tenant.name},
        
        Please find attached your rent invoice for {month} {year}.
        
        Unit: {tenant.unit.unit_number}
        Base Rent: KES {tenant.unit.rent_amount:,.2f}{additional_text}
        Total Amount: KES {total_amount:,.2f}
        
        Please pay by the 5th of {month} to avoid late fees.
        
        Best regards,
        {tenant.unit.property.landlord.name}
        SmartBiller Team
        """
        
        # Create message
        msg = Message(
            subject=f"Rent Invoice - {month} {year}",
            recipients=[tenant.email],
            body=body
        )
        
        # Attach invoice
        msg.attach(
            f"rent_invoice_{month}_{year}.pdf",
            "application/pdf",
            invoice_buffer.read()
        )
        
        # Send email
        mail.send(msg)
        print(f"Email sent to {tenant.email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {tenant.email}: {str(e)}")
        return False


def send_custom_invoice_sms(tenant, month, year, total_amount, additional_charges=None):
    """Send custom invoice reminder via SMS"""
    additional_text = ""
    if additional_charges:
        additional_text = f" (includes additional charges)"
    
    message = f"Dear {tenant.name}, your rent invoice for {month} {year} has been generated. Total amount: KES {total_amount:,.2f}{additional_text}. Please pay by the 5th to avoid late fees."
    send_sms(tenant.phone, message)


def update_usage_logs(landlord_id, action):
    """Update usage logs for billing purposes"""
    current_month = datetime.now().strftime('%Y-%m')
    usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
    
    if not usage:
        usage = UsageLog(landlord_id=landlord_id, month=current_month)
        db.session.add(usage)
    
    if action == 'email_sent':
        usage.email_sent = (usage.email_sent or 0) + 1
    elif action == 'sms_sent':
        usage.sms_sent = (usage.sms_sent or 0) + 1
    
    db.session.commit()


def send_late_payment_reminders():
    """Send reminders for late payments"""
    current_month = datetime.now().strftime('%B %Y')
    landlords = Landlord.query.all()
    
    for landlord in landlords:
        if not SubscriptionService.can_send_sms(landlord.id):
            continue
            
        for property_ in landlord.properties:
            for unit in property_.units:
                tenant = unit.tenant
                if not tenant:
                    continue
                
                # Check if payment is late (after 5th of month)
                if datetime.now().day > 5:
                    payment = RentLog.query.filter_by(
                        tenant_id=tenant.id,
                        month_paid_for=current_month
                    ).first()
                    
                    if not payment or payment.status != 'Paid':
                        message = f"Dear {tenant.name}, your rent for {current_month} is overdue. Please pay KES {unit.rent_amount:,.2f} immediately to avoid penalties."
                        send_sms(tenant.phone, message)
                        update_usage_logs(landlord.id, 'sms_sent')

def send_daily_error_summary():
    """Send daily error summary to admin"""
    try:
        from app.error_notification import ErrorNotificationService
        success = ErrorNotificationService.send_daily_error_summary()
        if success:
            print("✅ Daily error summary sent successfully")
        else:
            print("ℹ️ No errors to report in daily summary")
    except Exception as e:
        print(f"❌ Failed to send daily error summary: {str(e)}")


# CLI commands for manual execution
def run_late_reminders():
    """Command to run late payment reminders"""
    with current_app.app_context():
        send_late_payment_reminders()
        print("Late payment reminders sent successfully") 