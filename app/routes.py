from flask import render_template, redirect, url_for, request, session, flash, jsonify, send_file, current_app, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import openai
from flask_mail import Message, Mail
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import random
from reportlab.lib.utils import ImageReader
import qrcode
from reportlab.lib.colors import HexColor
import uuid
import string
import json
import traceback
from app.subscription_service import SubscriptionService
from app.error_notification import ErrorNotificationService

# Create blueprint
main = Blueprint('main', __name__)

AT_USERNAME = "sandbox"
AT_API_KEY = "atsk_40c68a16b6817f55ed1bfcb1f18693786bf57faa01ecc08c16939e89be41e9866c2977bc"

# Email configuration - will be initialized in app

def send_sms(phone, message):
    print(f"SMS to {phone}: {message}")

def allowed_file(filename, allowed_extensions=None):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_image(file, folder='uploads'):
    """Save uploaded image and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.root_path, 'static', folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Import models after db initialization
from .models import Landlord, Property, Unit, Tenant, RentLog, PropertyImage, UnitImage, RentLogImage, ExitNotice, Invoice, generate_receipt_number, generate_invoice_number, Employee, Admin, SystemLog, LoginAttempt, SystemMetrics, APIUsage, ErrorLog, DatabaseHealth, SecurityAlert, Subscription, PricingPlan, UsageLog

def send_employee_welcome_email(employee, default_password, landlord_name):
    """Send welcome email to new employee with login credentials"""
    from app import mail
    try:
        subject = f"Welcome to SmartBiller - Your Login Credentials"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to SmartBiller</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .credentials {{ background: #e8f4fd; border: 2px solid #2196F3; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .login-link {{ background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 Welcome to SmartBiller!</h1>
                    <p>Your property management account has been created</p>
                </div>
                
                <div class="content">
                    <h2>Hello {employee.name},</h2>
                    
                    <p>Welcome to SmartBiller! Your account has been created by <strong>{landlord_name}</strong> to help manage rental properties.</p>
                    
                    <div class="credentials">
                        <h3>🔐 Your Login Credentials</h3>
                        <p><strong>Email:</strong> {employee.email}</p>
                        <p><strong>Password:</strong> {default_password}</p>
                        <p><strong>Position:</strong> {employee.position}</p>
                    </div>
                    
                    <h3>🚀 What You Can Do</h3>
                    <ul>
                        <li>Log rent payments on behalf of your landlord</li>
                        <li>View property and tenant information</li>
                        <li>Generate receipts and reports</li>
                        <li>Track payment history</li>
                    </ul>
                    
                    <h3>🔗 Quick Access</h3>
                    <a href="https://smartbiller.co.ke/employee_login" class="login-link">
                        📱 Login to SmartBiller
                    </a>
                    
                    <h3>🔒 Security Tips</h3>
                    <ul>
                        <li>Change your password after first login</li>
                        <li>Keep your credentials secure</li>
                        <li>Log out when finished</li>
                        <li>Contact your landlord if you need help</li>
                    </ul>
                    
                    <p><strong>Note:</strong> This is a temporary password. Please change it after your first login for security.</p>
                </div>
                
                <div class="footer">
                    <p>SmartBiller - Professional Property Management</p>
                    <p>Making property management simple and efficient</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[employee.email],
            html=html_content
        )
        
        # Send email
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending email to {employee.email}: {str(e)}")
        return False


def send_employee_reactivation_email(employee, landlord_name):
    """Send reactivation email to employee"""
    from app import mail
    try:
        subject = f"SmartBiller Account Reactivated"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Account Reactivated</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: #e8f5e8; border: 2px solid #4CAF50; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .login-link {{ background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Account Reactivated!</h1>
                    <p>Your SmartBiller access has been restored</p>
                </div>
                
                <div class="content">
                    <h2>Hello {employee.name}</h2>
                    
                    <p>Great news! Your SmartBiller account has been reactivated by <strong>{landlord_name}</strong>.</p>
                    
                    <div class="info-box">
                        <h3>🔓 Access Restored</h3>
                        <p><strong>Email:</strong> {employee.email}</p>
                        <p><strong>Position:</strong> {employee.position}</p>
                        <p><strong>Status:</strong> Active</p>
                    </div>
                    
                    <h3>🚀 You Can Now:</h3>
                    <ul>
                        <li>Log in to your SmartBiller account</li>
                        <li>Log rent payments on behalf of your landlord</li>
                        <li>View property and tenant information</li>
                        <li>Generate receipts and reports</li>
                        <li>Track payment history</li>
                    </ul>
                    
                    <h3>🔗 Quick Access</h3>
                    <a href="https://smartbiller.co.ke/employee_login" class="login-link">
                        📱 Login to SmartBiller
                    </a>
                    
                    <h3>🔒 Security Reminder</h3>
                    <ul>
                        <li>Use your existing password to log in</li>
                        <li>If you forgot your password, contact your landlord</li>
                        <li>Keep your credentials secure</li>
                        <li>Log out when finished</li>
                    </ul>
                    
                    <p><strong>Note:</strong> If you need a password reset, please contact your landlord.</p>
                </div>
                
                <div class="footer">
                    <p>SmartBiller - Professional Property Management</p>
                    <p>Making property management simple and efficient</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[employee.email],
            html=html_content
        )
        
        # Send email
        mail.send(msg)
        return True
        
    except Exception as e:
        print(f"Error sending reactivation email to {employee.email}: {str(e)}")
        return False

@main.route('/')
def index():
    if 'landlord_id' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone')  # Optional phone field
        password = generate_password_hash(request.form['password'])
        if Landlord.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('main.register'))
        landlord = Landlord(
            name=name, 
            email=email,
            phone=phone if phone else None,
            password=password,
            trial_ends_at=datetime.utcnow() + timedelta(days=30),
            is_trial_active=True
        )
        db.session.add(landlord)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        landlord = Landlord.query.filter_by(email=email).first()
        if landlord and check_password_hash(landlord.password, password):
            session['landlord_id'] = landlord.id
            
            # Log successful login
            log_login_attempt(email, 'landlord', True, request.remote_addr, request.user_agent.string)
            log_system_event('info', 'auth', f'Landlord login successful: {email}', 
                           landlord.id, 'landlord', request.remote_addr, request.user_agent.string)
            
            flash('Welcome back!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Log failed login attempt
            log_login_attempt(email, 'landlord', False, request.remote_addr, request.user_agent.string, 'invalid_credentials')
            log_system_event('warning', 'auth', f'Failed landlord login attempt: {email}', 
                           None, 'landlord', request.remote_addr, request.user_agent.string)
            
            flash('Invalid credentials.', 'error')
    return render_template('login.html')


@main.route('/logout')
def logout():
    if 'landlord_id' in session:
        landlord_id = session['landlord_id']
        log_system_event('info', 'auth', 'Landlord logout', landlord_id, 'landlord', 
                        request.remote_addr, request.user_agent.string)
        flash('You have been logged out successfully.', 'success')
        session.pop('landlord_id', None)
        return redirect(url_for('main.login'))
    elif 'tenant_id' in session:
        tenant_id = session['tenant_id']
        log_system_event('info', 'auth', 'Tenant logout', tenant_id, 'tenant', 
                        request.remote_addr, request.user_agent.string)
        flash('You have been logged out successfully.', 'success')
        session.pop('tenant_id', None)
        session.pop('tenant_email', None)
        return redirect(url_for('main.tenant_login'))
    else:
        return redirect(url_for('main.index'))


@main.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))

    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Please log in as a landlord to access the dashboard.', 'error')
        return redirect(url_for('main.login'))

    selected_month = (
        request.form.get('selected_month') if request.method == 'POST'
        else request.args.get('selected_month')
    )
    if not selected_month:
        selected_month = datetime.now().strftime('%B %Y')

    # Get filter parameters
    payment_filter = request.form.get('payment_filter') if request.method == 'POST' else request.args.get('payment_filter')
    occupancy_filter = request.form.get('occupancy_filter') if request.method == 'POST' else request.args.get('occupancy_filter')
    property_filter = request.form.get('property_filter') if request.method == 'POST' else request.args.get('property_filter')
    unit_search = request.form.get('unit_search') if request.method == 'POST' else request.args.get('unit_search')

    # Filter properties if property filter is applied
    properties_query = Property.query.filter_by(landlord_id=landlord.id)
    if property_filter:
        properties_query = properties_query.filter(Property.id == int(property_filter))
    properties = properties_query.all()
    rent_status = {}

    for prop in properties:
        unit_statuses = []
        # Order units by unit_number in ascending order
        ordered_units = sorted(prop.units, key=lambda x: x.unit_number)
        for unit in ordered_units:
            tenant = unit.tenant
            if tenant:
                # Get all payments for this tenant
                all_payments = RentLog.query.filter_by(tenant_id=tenant.id).order_by(RentLog.date_paid).all()
                total_paid = sum(payment.amount_paid for payment in all_payments)
                
                # Get payment for selected month
                month_payment = RentLog.query.filter_by(
                    tenant_id=tenant.id,
                    month_paid_for=selected_month
                ).first()
                
                month_paid = month_payment.amount_paid if month_payment else 0
                
                # Calculate balance for selected month
                # Check if there's an invoice for this month with additional charges
                invoice_for_month = Invoice.query.filter_by(
                    tenant_id=tenant.id,
                    month=selected_month.split()[0],
                    year=int(selected_month.split()[1])
                ).first()
                
                # Use invoice total if available, otherwise use monthly rent
                amount_due = invoice_for_month.total_amount if invoice_for_month else unit.rent_amount
                month_balance = amount_due - month_paid
                
                # Determine if fully paid for this month
                paid = month_balance <= 0
                
                # Calculate overall balance using actual invoice amounts
                # Get all invoices for this tenant
                all_invoices = Invoice.query.filter_by(tenant_id=tenant.id).all()
                
                # Calculate total invoiced amount
                total_invoiced = sum(inv.total_amount for inv in all_invoices)
                
                # If no invoices, use monthly rent for months with payments
                if total_invoiced == 0:
                    unique_months = set(payment.month_paid_for for payment in all_payments)
                    months_with_payments = len(unique_months)
                    
                    # If selected month has no payment, add it to what's owed
                    if selected_month not in unique_months:
                        months_owed = months_with_payments + 1
                    else:
                        months_owed = months_with_payments
                    
                    total_should_be_owed = months_owed * unit.rent_amount
                else:
                    total_should_be_owed = total_invoiced
                
                overall_balance = total_should_be_owed - total_paid
                
                # Calculate additional charges for this month
                additional_charges_amount = amount_due - unit.rent_amount if amount_due > unit.rent_amount else 0
                
                unit_statuses.append({
                    'unit': unit,
                    'tenant': tenant,
                    'paid': paid,
                    'amount': unit.rent_amount,  # Always show base unit rent
                    'additional_charges': additional_charges_amount,  # Show additional charges separately
                    'total_amount_due': amount_due,  # Total amount due (rent + additional charges)
                    'month_paid': month_paid,
                    'month_balance': month_balance,
                    'total_paid': total_paid,
                    'overall_balance': overall_balance,
                    'credit_available': abs(overall_balance) if overall_balance < 0 else 0,
                    'payment_status': 'Paid' if paid else 'Partial' if month_paid > 0 else 'Unpaid'
                })
            else:
                unit_statuses.append({
                    'unit': unit,
                    'tenant': None,
                    'paid': False,
                    'amount': unit.rent_amount,
                    'month_paid': 0,
                    'month_balance': unit.rent_amount,
                    'total_paid': 0,
                    'payment_status': 'Vacant'
                })
        # Apply filters to unit statuses
        filtered_unit_statuses = unit_statuses
        
        # Filter by payment status
        if payment_filter:
            if payment_filter == 'paid':
                filtered_unit_statuses = [u for u in filtered_unit_statuses if u['payment_status'] == 'Paid']
            elif payment_filter == 'unpaid':
                filtered_unit_statuses = [u for u in filtered_unit_statuses if u['payment_status'] == 'Unpaid']
            elif payment_filter == 'partial':
                filtered_unit_statuses = [u for u in filtered_unit_statuses if u['payment_status'] == 'Partial']
        
        # Filter by occupancy status
        if occupancy_filter:
            if occupancy_filter == 'occupied':
                filtered_unit_statuses = [u for u in filtered_unit_statuses if u['tenant'] is not None]
            elif occupancy_filter == 'vacant':
                filtered_unit_statuses = [u for u in filtered_unit_statuses if u['tenant'] is None]
        
        # Filter by unit number search
        if unit_search:
            filtered_unit_statuses = [u for u in filtered_unit_statuses if unit_search.lower() in u['unit'].unit_number.lower()]
        
        rent_status[prop.id] = filtered_unit_statuses

    # Safe month list generation
    from calendar import monthrange
    months = [datetime(datetime.now().year, m, 1).strftime('%B %Y')
              for m in range(1, 13)]

    total_units = sum(len(p.units) for p in properties)
    total_properties = len(properties)
    total_paid_units = sum(1 for r in rent_status.values() for e in r if e['paid'])
    total_unpaid_units = sum(1 for r in rent_status.values() for e in r if e['tenant'] and not e['paid'])
    total_collected = sum(e['month_paid'] for r in rent_status.values() for e in r)
    
    # Calculate total outstanding
    total_outstanding = sum(e['month_balance'] for r in rent_status.values() for e in r if e['month_balance'] > 0)

    # Get pending exit notices for notifications
    pending_exit_notices = ExitNotice.query.filter_by(
        landlord_id=landlord.id, 
        status='Pending'
    ).order_by(ExitNotice.created_at.desc()).limit(5).all()

    # Update session with pending exit notices count
    session['pending_exit_notices_count'] = len(pending_exit_notices)

    # Add flash messages for active filters
    if payment_filter or occupancy_filter or property_filter or unit_search:
        filter_messages = []
        if payment_filter:
            filter_messages.append(f"Payment: {payment_filter.title()}")
        if occupancy_filter:
            filter_messages.append(f"Occupancy: {occupancy_filter.title()}")
        if property_filter:
            selected_property = Property.query.get(int(property_filter))
            if selected_property:
                filter_messages.append(f"Property: {selected_property.name}")
        if unit_search:
            filter_messages.append(f"Unit Search: '{unit_search}'")
        
        if filter_messages:
            flash(f"Filters applied: {', '.join(filter_messages)}", 'info')
    
    # Get subscription data for upgrade modal
    subscription_service = SubscriptionService()
    current_plan = subscription_service.get_landlord_plan(landlord.id)
    usage_summary = subscription_service.get_usage_summary(landlord.id)
    
    # Check trial status
    is_trial_active = subscription_service.is_trial_active(landlord.id)
    trial_days_remaining = 0
    if is_trial_active and landlord.trial_ends_at:
        trial_days_remaining = (landlord.trial_ends_at - datetime.utcnow()).days
    
    # Provide default values if data is missing
    if not current_plan:
        # Create a default plan object with basic limits
        from app.models import PricingPlan
        current_plan = PricingPlan(
            name='Basic',
            code='basic',
            max_properties=3,
            max_units_per_property=100,
            max_sms_per_month=50
        )
    
    if not usage_summary:
        # Create default usage summary
        usage_summary = {
            'properties_count': 0,
            'units_count': 0,
            'sms_sent': 0,
            'pdf_generated': 0,
            'api_calls': 0,
            'plan': 'Basic',
            'max_properties': 3,
            'max_sms': 50,
            'can_generate_pdf': False,
            'can_use_api': False
        }
    
    # Check if upgrade modal should be shown (when limits are reached)
    show_upgrade_modal = False
    if current_plan and usage_summary:
        print(f"DEBUG: Usage summary: {usage_summary}")
        # Handle None values safely
        properties_count = usage_summary.get('properties_count', 0) or 0
        sms_sent = usage_summary.get('sms_sent', 0) or 0
        
        if (properties_count >= current_plan.max_properties or 
            sms_sent >= current_plan.max_sms_per_month):
            show_upgrade_modal = True
    
    # Get current plan features for display
    current_features = []
    if current_plan:
        if current_plan.code == 'basic':
            current_features = [
                f"Up to {current_plan.max_properties} properties",
                f"Up to {current_plan.max_units_per_property} units per property",
                f"{current_plan.max_sms_per_month} SMS per month",
                "Basic reporting",
                "Email support"
            ]
        elif current_plan.code == 'professional':
            current_features = [
                f"Up to {current_plan.max_properties} properties",
                f"Up to {current_plan.max_units_per_property} units per property",
                f"{current_plan.max_sms_per_month} SMS per month",
                "PDF receipts & invoices",
                "Exit notice management",
                "API access",
                "Priority support"
            ]
        else:  # enterprise
            current_features = [
                "Unlimited properties",
                "Unlimited units",
                "Unlimited SMS",
                "Custom integrations",
                "White-label solution",
                "Dedicated support"
            ]

    return render_template(
        'dashboard.html',
        landlord=landlord,
        properties=properties,
        rent_status=rent_status,
        current_month=selected_month,
        months=months,
        total_units=total_units,
        total_properties=total_properties,
        total_paid=total_paid_units,
        total_unpaid=total_unpaid_units,
        total_collected=total_collected,
        total_outstanding=total_outstanding,
        unit_search=unit_search,
        pending_exit_notices=pending_exit_notices,
        current_plan=current_plan,
        usage=usage_summary,
        current_features=current_features,
        show_upgrade_modal=show_upgrade_modal,
        is_trial_active=is_trial_active,
        trial_days_remaining=trial_days_remaining
    )


@main.route('/dashboard-responsive')
def dashboard_responsive():
    """Enhanced responsive dashboard with mobile-first design"""
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))

    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Please log in as a landlord to access the dashboard.', 'error')
        return redirect(url_for('main.login'))

    # Get basic stats
    properties = Property.query.filter_by(landlord_id=landlord.id).all()
    total_units = sum(len(p.units) for p in properties)
    total_properties = len(properties)
    
    # Calculate payment stats
    total_paid = 0
    total_unpaid = 0
    total_collected = 0
    
    for prop in properties:
        for unit in prop.units:
            if unit.tenant:
                # Get current month payments
                current_month = datetime.now().strftime('%B %Y')
                month_payment = RentLog.query.filter_by(
                    tenant_id=unit.tenant.id,
                    month_paid_for=current_month
                ).first()
                
                if month_payment and month_payment.amount_paid >= unit.rent_amount:
                    total_paid += 1
                    total_collected += month_payment.amount_paid
                else:
                    total_unpaid += 1
                    if month_payment:
                        total_collected += month_payment.amount_paid

    # Get subscription data
    subscription_service = SubscriptionService()
    current_plan = subscription_service.get_landlord_plan(landlord.id)
    usage_summary = subscription_service.get_usage_summary(landlord.id)
    
    # Check trial status
    is_trial_active = subscription_service.is_trial_active(landlord.id)
    trial_days_remaining = 0
    if is_trial_active and landlord.trial_ends_at:
        trial_days_remaining = (landlord.trial_ends_at - datetime.utcnow()).days

    # Get recent activities (simplified for responsive demo)
    recent_activities = []
    recent_rent_logs = RentLog.query.filter_by(
        landlord_id=landlord.id
    ).order_by(RentLog.date_paid.desc()).limit(10).all()
    
    for rent_log in recent_rent_logs:
        if rent_log.tenant and rent_log.tenant.unit and rent_log.tenant.unit.property:
            recent_activities.append({
                'property_name': rent_log.tenant.unit.property.name,
                'unit_number': rent_log.tenant.unit.unit_number,
                'tenant_name': rent_log.tenant.name,
                'amount': rent_log.amount_paid,
                'status': 'paid' if rent_log.amount_paid >= rent_log.tenant.unit.rent_amount else 'partial',
                'date': rent_log.date_paid
            })

    return render_template(
        'dashboard_responsive.html',
        landlord=landlord,
        total_units=total_units,
        total_properties=total_properties,
        total_paid=total_paid,
        total_unpaid=total_unpaid,
        total_collected=total_collected,
        current_plan=current_plan,
        usage=usage_summary,
        is_trial_active=is_trial_active,
        trial_days_remaining=trial_days_remaining,
        recent_activities=recent_activities
    )


@main.route('/responsive-demo')
def responsive_demo():
    """Demo page for responsive design features"""
    return render_template('responsive_demo.html')


@main.route('/datatables-demo')
def datatables_demo():
    """Demo page for DataTables features"""
    return render_template('datatables_demo.html')


@main.route('/add_property', methods=['GET', 'POST'])
def add_property():
    if 'landlord_id' not in session:
        flash('Please log in to add a property.')
        return redirect(url_for('main.login'))
    
    # Debug logging
    print(f"DEBUG: Landlord ID: {session['landlord_id']}")
    print(f"DEBUG: Can add property: {SubscriptionService.can_add_property(session['landlord_id'])}")
    
    # Enforce plan property limit
    if not SubscriptionService.can_add_property(session['landlord_id']):
        print(f"DEBUG: Property limit reached for landlord {session['landlord_id']}")
        print(f"DEBUG: Redirecting to upgrade page")
        flash('You have reached your property limit for your current plan. Please upgrade to add more.', 'danger')
        return redirect(url_for('main.upgrade'))
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            location = request.form['location']
            payment_method = request.form['payment_method']
            payment_destination = request.form['payment_destination']
            
            if not name or not location:
                flash('Property name and location are required.', 'error')
                return render_template('add_property.html')
            
            prop = Property(name=name, location=location, payment_method=payment_method,
                            payment_destination=payment_destination, landlord_id=session['landlord_id'])
            db.session.add(prop)
            db.session.commit()
            flash('Property added successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding property: {str(e)}', 'error')
            return render_template('add_property.html')
    return render_template('add_property.html')


@main.route('/add_unit', methods=['GET', 'POST'])
def add_unit_selector():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    landlord = Landlord.query.get(session['landlord_id'])
    properties = Property.query.filter_by(landlord_id=landlord.id).all()
    
    if request.method == 'POST':
        property_id = request.form.get('property_id')
        if property_id:
            return redirect(url_for('main.add_unit', property_id=property_id))
        else:
            flash('Please select a property.')
    
    return render_template('add_unit_selector.html', properties=properties)


@main.route('/property/<int:property_id>/add_unit', methods=['GET', 'POST'])
def add_unit(property_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    # Get property and verify ownership
    property = Property.query.get_or_404(property_id)
    if property.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this property.')
        return redirect(url_for('main.dashboard'))
    
    # Enforce plan unit limit
    if not SubscriptionService.can_add_unit_to_property(session['landlord_id'], property_id):
        flash('You have reached your unit limit for this property on your current plan. Please upgrade to add more units.', 'danger')
        return redirect(url_for('main.upgrade'))
    
    if request.method == 'POST':
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Handle bulk unit creation
            unit_numbers = request.form.getlist('unit_number')
            rent_amounts = request.form.getlist('rent_amount')
            
            if len(unit_numbers) > 1:
                # Bulk creation
                created_count = 0
                for i, unit_number in enumerate(unit_numbers):
                    if unit_number and rent_amounts[i]:
                        # Check unit limit before each creation
                        if not SubscriptionService.can_add_unit_to_property(session['landlord_id'], property_id):
                            if is_ajax:
                                return jsonify({'success': False, 'message': f'Unit limit reached. Only {created_count} units were created.'})
                            else:
                                flash(f'Unit limit reached. Only {created_count} units were created.', 'warning')
                                break
                        
                        unit = Unit(
                            unit_number=unit_number,
                            rent_amount=float(rent_amounts[i]),
                            property_id=property_id
                        )
                        db.session.add(unit)
                        created_count += 1
                
                db.session.commit()
                
                if is_ajax:
                    return jsonify({'success': True, 'count': created_count, 'message': f'{created_count} units created successfully!'})
                else:
                    flash(f'{created_count} units created successfully!')
            else:
                # Single unit creation
                unit_number = request.form['unit_number']
                rent_amount = request.form['rent_amount']
                unit = Unit(
                    unit_number=unit_number,
                    rent_amount=rent_amount,
                    property_id=property_id
                )
                db.session.add(unit)
                db.session.commit()
                
                if is_ajax:
                    return jsonify({'success': True, 'message': 'Unit created successfully!'})
                else:
                    flash('Unit created successfully!')
            
            if is_ajax:
                return jsonify({'success': True, 'message': 'Unit(s) created successfully!'})
            else:
                return redirect(url_for('main.add_unit', property_id=property_id))
                
        except Exception as e:
            db.session.rollback()
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)})
            else:
                flash(f'Error creating unit: {str(e)}')
                return redirect(url_for('main.add_unit', property_id=property_id))
    
    return render_template('add_unit.html', property=property)


@main.route('/unit/<int:unit_id>/edit', methods=['GET', 'POST'])
def edit_unit(unit_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    unit = Unit.query.get_or_404(unit_id)
    property = Property.query.get(unit.property_id)
    
    # Verify ownership
    if property.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this unit.')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            unit.unit_number = request.form['unit_number']
            unit.rent_amount = float(request.form['rent_amount'])
            db.session.commit()
            
            if is_ajax:
                return jsonify({'success': True, 'message': 'Unit updated successfully!'})
            else:
                flash('Unit updated successfully!')
                return redirect(url_for('main.dashboard'))
                
        except Exception as e:
            db.session.rollback()
            if is_ajax:
                return jsonify({'success': False, 'message': str(e)})
            else:
                flash(f'Error updating unit: {str(e)}')
                return redirect(url_for('main.dashboard'))
    
    return render_template('edit_unit.html', unit=unit, property=property)


@main.route('/unit/<int:unit_id>/delete', methods=['POST'])
def delete_unit(unit_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    unit = Unit.query.get_or_404(unit_id)
    property = Property.query.get(unit.property_id)
    
    # Verify ownership
    if property.landlord_id != session['landlord_id']:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    # Check if unit has a tenant
    if unit.tenant:
        return jsonify({'success': False, 'message': 'Cannot delete unit with active tenant'})
    
    try:
        db.session.delete(unit)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Unit deleted successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@main.route('/unit/<int:unit_id>/add_tenant', methods=['GET', 'POST'])
def add_tenant(unit_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    # Get unit and verify ownership
    unit = Unit.query.get_or_404(unit_id)
    property = Property.query.get(unit.property_id)
    landlord_id = property.landlord_id
    print(f"Landlord ID: {landlord_id}")
    print(f"Session ID: {session['landlord_id']}")
    
    if landlord_id != session['landlord_id']:
        flash('Unauthorized access to this unit.')
        return redirect(url_for('main.dashboard'))
    
    # Check if unit already has a tenant
    if unit.tenant:
        flash('This unit already has a tenant assigned.')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']  # Now required for login
            id_number = request.form.get('id_number')
            emergency_contact = request.form.get('emergency_contact')
            occupation = request.form.get('occupation')
            employer = request.form.get('employer')
            move_in_date = request.form.get('move_in_date')
            
            # Validate email is provided
            if not email:
                flash('Email address is required for tenant login.', 'error')
                return redirect(url_for('main.add_tenant', unit_id=unit_id))
            
            # Check if email is already in use
            existing_tenant = Tenant.query.filter_by(email=email).first()
            if existing_tenant:
                flash('A tenant with this email address already exists.', 'error')
                return redirect(url_for('main.add_tenant', unit_id=unit_id))
            
            # Create new tenant
            tenant = Tenant(
                name=name,
                phone=phone,
                email=email,
                unit_id=unit_id
            )
            if id_number:
                tenant.id_number = id_number
            if emergency_contact:
                tenant.emergency_contact = emergency_contact
            if occupation:
                tenant.occupation = occupation
            if employer:
                tenant.employer = employer
            if move_in_date:
                tenant.move_in_date = datetime.strptime(move_in_date, '%Y-%m-%d')
            
            # Generate login code for tenant
            tenant.login_code = ''.join(random.choices(string.digits, k=6))
            tenant.login_code_expiry = datetime.utcnow() + timedelta(hours=24)
            
            db.session.add(tenant)
            
            # Update unit status to occupied
            unit.status = 'Occupied'
            
            db.session.commit()
            
            flash(f'Tenant {name} added successfully! Login code: {tenant.login_code}')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding tenant: {str(e)}')
            return redirect(url_for('main.add_tenant', unit_id=unit_id))
    
    return render_template('add_tenant.html', unit=unit, unit_id=unit_id)


@main.route('/tenant/<int:tenant_id>/log_rent', methods=['GET', 'POST'])
def log_rent(tenant_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))

    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        flash('Tenant not found.')
        return redirect(url_for('main.dashboard'))
    
    unit = tenant.unit  # Needed for rent comparison

    if request.method == 'POST':
        amount_paid = float(request.form['amount_paid'])
        date_paid = request.form['date_paid']
        month_paid_for = request.form['month_paid_for']

        # Get monthly rent amount
        monthly_rent = unit.rent_amount
        
        # Determine who logged the payment based on session (define early)
        logged_by_employee_id = None
        if 'employee_id' in session:
            # Employee is logged in
            logged_by_employee_id = session['employee_id']
        # If no employee_id in session, it's logged by the landlord (logged_by_employee_id remains None)
        
        # Check if there's already a payment for this month
        existing_payment = RentLog.query.filter_by(
            tenant_id=tenant_id,
            month_paid_for=month_paid_for
        ).first()
        
        # Calculate current balance before this payment
        current_month_balance, total_paid, overall_balance, additional_charges, amount_due_for_month = calculate_tenant_balance(tenant_id, month_paid_for)
        
        # If there's an existing payment, this is an installment
        if existing_payment:
            # Get the total amount paid for this month so far
            total_paid_for_month = existing_payment.amount_paid + amount_paid
            
            # Calculate remaining balance after this installment
            remaining_balance = monthly_rent - total_paid_for_month
            
            # Determine status for this installment
            if total_paid_for_month >= monthly_rent:
                installment_status = "Paid"
            elif total_paid_for_month > 0:
                installment_status = "Partial"
            else:
                installment_status = "Unpaid"
            
            # Generate notes for the installment payment
            installment_notes = []
            installment_notes.append(f"Installment payment - KES {amount_paid:,.2f}")
            installment_notes.append(f"Total paid for {month_paid_for}: KES {total_paid_for_month:,.2f}")
            if remaining_balance > 0:
                installment_notes.append(f"Remaining balance: KES {remaining_balance:,.2f}")
            
            # Add manual notes if provided
            payment_notes = request.form.get('payment_notes', '').strip()
            if payment_notes:
                installment_notes.append(f"Manual notes: {payment_notes}")
            
            # Determine who logged the payment
            logged_by = "Landlord"
            if 'employee_id' in session:
                employee = Employee.query.get(session['employee_id'])
                if employee:
                    logged_by = f"Employee: {employee.name}"
            
            installment_notes.append(f"Logged by: {logged_by}")
            
            # Create a new log entry for this installment (don't update existing)
            installment_log = RentLog(
                tenant_id=tenant_id,
                amount_paid=amount_paid,  # Store the actual installment amount
                date_paid=datetime.strptime(date_paid, '%Y-%m-%d'),
                month_paid_for=month_paid_for,
                status=installment_status,
                logged_by_employee_id=logged_by_employee_id,
                notes=" | ".join(installment_notes) if installment_notes else None
            )
            
            db.session.add(installment_log)
            db.session.commit()
            
            # Prepare message for installment
            if remaining_balance <= 0:
                flash(f'Installment payment logged successfully! Total paid for {month_paid_for}: KES {total_paid_for_month:,.2f}. Status: {installment_status}.')
            else:
                flash(f'Installment payment logged successfully! KES {amount_paid:,.2f} added. Total for {month_paid_for}: KES {total_paid_for_month:,.2f}. Remaining: KES {remaining_balance:,.2f}')
            
            return redirect(url_for('main.dashboard'))
        
        # If tenant has credit (negative overall balance), apply it to this payment
        credit_available = abs(overall_balance) if overall_balance < 0 else 0
        effective_payment = amount_paid + credit_available
        
        # Determine status for this specific month
        if effective_payment == 0:
            status = "Unpaid"
        elif effective_payment < monthly_rent:
            status = "Partial"
        else:
            status = "Paid"
        
        # ALWAYS create a rent log entry for every payment attempt, even if amount is 0
        # This ensures complete audit trail of all payment activities
        
        # Generate notes for the payment log
        notes = []
        if amount_paid == 0:
            notes.append("Payment attempt logged - no amount paid")
        if credit_available > 0:
            notes.append(f"Applied credit: KES {credit_available:,.2f}")
        if effective_payment != amount_paid:
            notes.append(f"Effective payment: KES {effective_payment:,.2f} (including credit)")
        
        # Add manual notes if provided
        payment_notes = request.form.get('payment_notes', '').strip()
        if payment_notes:
            notes.append(f"Manual notes: {payment_notes}")
        
        # Determine who logged the payment
        logged_by = "Landlord"
        if 'employee_id' in session:
            employee = Employee.query.get(session['employee_id'])
            if employee:
                logged_by = f"Employee: {employee.name}"
        
        notes.append(f"Logged by: {logged_by}")
        
        # Create comprehensive payment log
        rent_log = RentLog(
            tenant_id=tenant_id,
            amount_paid=amount_paid,  # Store the actual amount paid (can be 0)
            date_paid=datetime.strptime(date_paid, '%Y-%m-%d'),
            month_paid_for=month_paid_for,
            status=status,
            logged_by_employee_id=logged_by_employee_id,
            notes=" | ".join(notes) if notes else None
        )

        db.session.add(rent_log)
        db.session.commit()
        
        # Prepare message for user
        if credit_available > 0:
            if effective_payment >= monthly_rent:
                flash(f'Payment logged successfully! Status: {status}. Applied KES {credit_available:,.2f} credit + KES {amount_paid:,.2f} payment = KES {effective_payment:,.2f} total.')
            else:
                remaining = monthly_rent - effective_payment
                flash(f'Payment logged successfully! Status: {status}. Applied KES {credit_available:,.2f} credit + KES {amount_paid:,.2f} payment. Remaining: KES {remaining:,.2f}')
        elif amount_paid > monthly_rent:
            overpayment = amount_paid - monthly_rent
            # Calculate how many months this overpayment can cover
            months_covered = int(overpayment // monthly_rent)
            remaining_credit = overpayment % monthly_rent
            
            if months_covered > 0:
                if remaining_credit > 0:
                    flash(f'Payment logged successfully! Status: {status}. Overpayment of KES {overpayment:,.2f} will cover {months_covered} full month(s) + KES {remaining_credit:,.2f} credit for future months.')
                else:
                    flash(f'Payment logged successfully! Status: {status}. Overpayment of KES {overpayment:,.2f} will cover {months_covered} full month(s) of rent.')
            else:
                flash(f'Payment logged successfully! Status: {status}. Overpayment of KES {overpayment:,.2f} will be applied as credit for future months.')
        elif amount_paid == monthly_rent:
            flash(f'Payment logged successfully! Status: {status}. Full payment received.')
        else:
            remaining = monthly_rent - amount_paid
            flash(f'Payment logged successfully! Status: {status}. Remaining balance for {month_paid_for}: KES {remaining:,.2f}')
        
        return redirect(url_for('main.dashboard'))

    # Calculate current balance for display
    current_month = datetime.now().strftime('%B %Y')
    
    # Use the helper function to calculate balances
    current_month_balance, total_paid, overall_balance, additional_charges, amount_due_for_month = calculate_tenant_balance(tenant_id, current_month)
    
    # Calculate credit available (absolute value of negative balance)
    credit_available = abs(overall_balance) if overall_balance < 0 else 0
    
    # Get employees for the landlord
    landlord = Landlord.query.get(session['landlord_id'])
    employees = Employee.query.filter_by(landlord_id=landlord.id, is_active=True).all()

    return render_template('log_rent.html', 
                         tenant=tenant, 
                         current_month_balance=current_month_balance,
                         total_paid=total_paid,
                         overall_balance=overall_balance,
                         additional_charges=additional_charges,
                         amount_due_for_month=amount_due_for_month,
                         credit_available=credit_available,
                         today_date=datetime.now().strftime('%Y-%m-%d'),
                         employees=employees)


@main.route('/send_reminders')
def send_reminders():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Landlord not found.')
        return redirect(url_for('main.login'))
        
    current_month = datetime.now().strftime('%B %Y')
    for prop in landlord.properties:
        for unit in prop.units:
            tenant = unit.tenant
            if tenant:
                paid = RentLog.query.filter_by(
                    tenant_id=tenant.id, month_paid_for=current_month).first()
                if not paid:
                    message = f"Dear {tenant.name}, your rent for {current_month} is due. Please pay {unit.rent_amount}."
                    send_sms(tenant.phone, message)
    flash('Reminders sent! (Check console for mock SMS)')
    return redirect(url_for('main.dashboard'))


@main.route('/send_notice', methods=['GET', 'POST'])
def send_notice():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))

    landlord_id = session['landlord_id']

    if request.method == 'POST':
        tenant_id = request.form['tenant_id']
        property_id = request.form['property_id']
        subject = request.form.get('subject')
        message = request.form['message']
        due_date = request.form.get('due_date')

        # Fetch tenant, unit, property and validate ownership
        tenant = Tenant.query.get(tenant_id)
        if not tenant:
            flash('Tenant not found.')
            return redirect(url_for('main.dashboard'))
            
        unit = tenant.unit
        property = Property.query.get(property_id)
        if not property:
            flash('Property not found.')
            return redirect(url_for('main.dashboard'))

        # Optional: prevent cross-access by checking ownership
        if property.landlord_id != landlord_id or unit.property_id != property.id:
            flash("Unauthorized action.")
            return redirect(url_for('main.dashboard'))

        # Replace placeholders
        msg_filled = message.replace('{{ tenant_name }}', tenant.name)
        msg_filled = msg_filled.replace('{{ unit_number }}', unit.unit_number)
        msg_filled = msg_filled.replace('{{ property_name }}', property.name)
        msg_filled = msg_filled.replace('{{ due_date }}', due_date or 'N/A')

        # Send notice (SMS/Email logic can go here)
        send_sms(tenant.phone, msg_filled)

        flash("Notice sent successfully!")
        return redirect(url_for('main.dashboard'))

    # Filter properties and tenants by current landlord
    properties = Property.query.filter_by(landlord_id=landlord_id).all()

    # Only tenants in the landlord's units
    tenants = Tenant.query.join(Unit).filter(Unit.property_id.in_(
        db.session.query(Property.id).filter_by(landlord_id=landlord_id)
    )).all()

    return render_template("send_notice.html", properties=properties, tenants=tenants)


@main.route('/unit/<int:unit_id>/history')
def unit_history(unit_id):
    if 'landlord_id' not in session:
        flash('Please log in to view unit history.')
        return redirect(url_for('main.login'))
    
    unit = Unit.query.get_or_404(unit_id)
    property = Property.query.get(unit.property_id)
    
    # Verify ownership
    if property.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this unit.')
        return redirect(url_for('main.dashboard'))
    
    tenant = unit.tenant
    if not tenant:
        flash('This unit has no tenant history.')
        return render_template('unit_history.html', unit=unit, tenant=tenant, history=[])
    
    history = RentLog.query.filter_by(tenant_id=tenant.id).order_by(
        RentLog.date_paid.desc()).all()
    
    if not history:
        flash('No payment history found for this unit.')
    
    return render_template('unit_history.html', unit=unit, tenant=tenant, history=history)


@main.route('/tenant/<int:tenant_id>/update', methods=['GET', 'POST'])
def update_tenant(tenant_id):
    if 'landlord_id' not in session:
        flash('Please log in to update tenant information.')
        return redirect(url_for('main.login'))
    
    tenant = Tenant.query.get_or_404(tenant_id)
    unit = tenant.unit
    property = Property.query.get(unit.property_id)
    
    # Verify ownership
    if property.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this tenant.')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            tenant.name = request.form['name']
            tenant.phone = request.form['phone']
            new_email = request.form.get('email')
            
            # Check if email is being changed and if it's already in use
            if new_email and new_email != tenant.email:
                existing_tenant = Tenant.query.filter_by(email=new_email).first()
                if existing_tenant and existing_tenant.id != tenant.id:
                    flash('A tenant with this email address already exists.', 'error')
                    return render_template('update_tenant.html', tenant=tenant)
                tenant.email = new_email
            
            tenant.id_number = request.form.get('id_number')
            tenant.emergency_contact = request.form.get('emergency_contact')
            tenant.occupation = request.form.get('occupation')
            tenant.employer = request.form.get('employer')
            
            db.session.commit()
            flash('Tenant information updated successfully!')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating tenant: {str(e)}')
            return render_template('update_tenant.html', tenant=tenant)
    
    return render_template('update_tenant.html', tenant=tenant)


@main.route('/pricing')
def pricing():
    print(f"DEBUG: Pricing route accessed")
    try:
        # Get trial information if user is logged in
        is_trial_active = False
        trial_days_remaining = 0
        
        if 'landlord_id' in session:
            landlord = Landlord.query.get(session['landlord_id'])
            if landlord:
                is_trial_active = SubscriptionService.is_trial_active(session['landlord_id'])
                if is_trial_active and landlord.trial_ends_at:
                    trial_days_remaining = (landlord.trial_ends_at - datetime.utcnow()).days
        
        return render_template('pricing.html', 
                             is_trial_active=is_trial_active,
                             trial_days_remaining=trial_days_remaining)
    except Exception as e:
        print(f"DEBUG: Error in pricing route: {e}")
        return f"Error loading pricing page: {e}", 500


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            if not name or not email or not message:
                flash('Please fill in all required fields.')
                return render_template('contact.html')
            
            # Here you would typically send an email or save to database
            # For now, we'll just show a success message
            flash('Thank you for your message! We will get back to you soon.')
            return redirect(url_for('main.contact'))
            
        except Exception as e:
            flash(f'Error sending message: {str(e)}')
            return render_template('contact.html')
    
    return render_template('contact.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/api/chatbot', methods=['POST'])
def chatbot_api():
    if 'landlord_id' not in session:
        return jsonify({'error': 'Unauthorized access'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        ai_reply = response.choices[0].message.content
        return jsonify({'reply': ai_reply})
    except Exception as e:
        return jsonify({'error': f'Chatbot error: {str(e)}'}), 500


@main.route('/tenant_login', methods=['GET', 'POST'])
def tenant_login():
    if request.method == 'POST':
        email = request.form['email']
        
        # Validate email format
        if not email or '@' not in email:
            flash('Please enter a valid email address.', 'error')
            return render_template('tenant_login.html')
        
        tenant = Tenant.query.filter_by(email=email).first()
        if not tenant:
            flash('No tenant found with that email address. Please check your email or contact your landlord.', 'danger')
            return render_template('tenant_login.html')
        
        # Check if tenant has a valid unit
        if not tenant.unit:
            flash('Your account is not associated with any unit. Please contact your landlord.', 'error')
            return render_template('tenant_login.html')
        
        code = str(random.randint(100000, 999999))
        tenant.login_code = code
        tenant.login_code_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        
        # Print login code to terminal for development/testing
        print(f"\n{'='*50}")
        print(f"TENANT LOGIN CODE GENERATED")
        print(f"{'='*50}")
        print(f"Email: {email}")
        print(f"Tenant: {tenant.name}")
        print(f"Unit: {tenant.unit.unit_number if tenant.unit else 'No unit'}")
        print(f"Login Code: {code}")
        print(f"Expires: {tenant.login_code_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # Send code via SMS (mock)
        send_sms(
            tenant.phone, f'Your SmartBiller login code is: {code}. It expires in 10 minutes.')
        session['tenant_email'] = email
        flash(f'Login code sent to {email}. Please check your email and enter the 6-digit code.', 'success')
        return redirect(url_for('main.tenant_verify'))
    return render_template('tenant_login.html')


@main.route('/tenant_verify', methods=['GET', 'POST'])
def tenant_verify():
    email = session.get('tenant_email')
    if not email:
        return redirect(url_for('main.tenant_login'))
    tenant = Tenant.query.filter_by(email=email).first()
    if request.method == 'POST':
        code = request.form['code']
        
        # Print verification attempt to terminal
        print(f"\n{'='*50}")
        print(f"TENANT LOGIN VERIFICATION ATTEMPT")
        print(f"{'='*50}")
        print(f"Email: {email}")
        print(f"Tenant: {tenant.name if tenant else 'Unknown'}")
        print(f"Attempted Code: {code}")
        if tenant:
            print(f"Stored Code: {tenant.login_code}")
            print(f"Code Expires: {tenant.login_code_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Code Valid: {tenant.login_code == code}")
            print(f"Not Expired: {tenant.login_code_expiry > datetime.utcnow()}")
        else:
            print(f"Stored Code: No tenant found")
        print(f"{'='*50}\n")
        
        if tenant and tenant.login_code == code and tenant.login_code_expiry > datetime.utcnow():
            session['tenant_id'] = tenant.id
            print(f"✅ LOGIN SUCCESSFUL for {tenant.name}")
            flash(f'Welcome back, {tenant.name}!', 'success')
            return redirect(url_for('main.tenant_dashboard'))
        else:
            print(f"❌ LOGIN FAILED for {email}")
            if not tenant:
                flash('Invalid email address. Please try logging in again.', 'danger')
            elif tenant.login_code != code:
                flash('Invalid verification code. Please check the code and try again.', 'danger')
            elif tenant.login_code_expiry <= datetime.utcnow():
                flash('Verification code has expired. Please request a new code.', 'warning')
            else:
                flash('Invalid or expired code. Please try again.', 'danger')
    return render_template('tenant_verify.html')


@main.route('/tenant_dashboard')
def tenant_dashboard():
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        return redirect(url_for('main.tenant_login'))
    tenant = Tenant.query.get(tenant_id)
    
    # Get recent invoices for this tenant
    recent_invoices = Invoice.query.filter_by(tenant_id=tenant_id).order_by(Invoice.created_at.desc()).limit(5).all()
    
    return render_template('tenant_dashboard.html', tenant=tenant, recent_invoices=recent_invoices)

@main.route('/tenant/invoice/<int:invoice_id>')
def tenant_invoice(invoice_id):
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        return redirect(url_for('main.tenant_login'))
    
    invoice = Invoice.query.filter_by(id=invoice_id, tenant_id=tenant_id).first()
    if not invoice:
        flash('Invoice not found.', 'error')
        return redirect(url_for('main.tenant_dashboard'))
    
    # Return the PDF file
    invoice_path = os.path.join(current_app.root_path, 'static', invoice.pdf_path)
    if os.path.exists(invoice_path):
        return send_file(invoice_path, as_attachment=True, download_name=f"invoice_{invoice.invoice_number}.pdf")
    else:
        flash('Invoice file not found.', 'error')
        return redirect(url_for('main.tenant_dashboard'))

@main.route('/tenant/invoices')
def tenant_invoices():
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        return redirect(url_for('main.tenant_login'))
    
    tenant = Tenant.query.get(tenant_id)
    invoices = Invoice.query.filter_by(tenant_id=tenant_id).order_by(Invoice.created_at.desc()).all()
    
    # Parse additional_charges JSON for each invoice
    for invoice in invoices:
        if invoice.additional_charges:
            try:
                invoice.parsed_charges = json.loads(invoice.additional_charges)
            except (json.JSONDecodeError, TypeError):
                invoice.parsed_charges = []
        else:
            invoice.parsed_charges = []
    
    return render_template('tenant_invoices.html', tenant=tenant, invoices=invoices)


@main.route('/tenant/exit_notice', methods=['GET', 'POST'])
def tenant_exit_notice():
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        return redirect(url_for('main.tenant_login'))
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        flash('Tenant not found.', 'error')
        return redirect(url_for('main.tenant_login'))
    
    if request.method == 'POST':
        try:
            intended_exit_date = datetime.strptime(request.form['intended_exit_date'], '%Y-%m-%d').date()
            reason = request.form['reason']
            additional_comments = request.form.get('additional_comments', '')
            
            # Create exit notice
            exit_notice = ExitNotice(
                tenant_id=tenant.id,
                landlord_id=tenant.unit.property.landlord_id,
                intended_exit_date=intended_exit_date,
                reason=reason,
                additional_comments=additional_comments
            )
            
            db.session.add(exit_notice)
            db.session.commit()
            
            # Send SMS notification to landlord (optional)
            landlord_phone = exit_notice.landlord.phone if hasattr(exit_notice.landlord, 'phone') else None
            if landlord_phone:
                sms_message = f"New exit notice from {exit_notice.tenant.name} ({exit_notice.tenant.unit.unit_number}). Intended exit date: {exit_notice.intended_exit_date.strftime('%B %d, %Y')}. Reason: {exit_notice.reason}"
                send_sms(landlord_phone, sms_message)
            
            flash('Exit notice submitted successfully! Your landlord will be notified.', 'success')
            return redirect(url_for('main.tenant_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting exit notice: {str(e)}', 'error')
            return render_template('tenant_exit_notice.html', tenant=tenant)
    
    return render_template('tenant_exit_notice.html', tenant=tenant)


@main.route('/landlord/exit_notices')
def landlord_exit_notices():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Please log in as a landlord to access exit notices.', 'error')
        return redirect(url_for('main.login'))
    
    # Get all exit notices for this landlord
    exit_notices = ExitNotice.query.filter_by(landlord_id=landlord.id).order_by(ExitNotice.created_at.desc()).all()
    
    return render_template('landlord_exit_notices.html', exit_notices=exit_notices, landlord=landlord)


@main.route('/landlord/exit_notice/<int:notice_id>/respond', methods=['GET', 'POST'])
def respond_exit_notice(notice_id):
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    exit_notice = ExitNotice.query.get_or_404(notice_id)
    
    # Verify ownership
    if exit_notice.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this exit notice.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            status = request.form['status']
            response = request.form.get('response', '')
            
            exit_notice.status = status
            exit_notice.landlord_response = response
            exit_notice.response_date = datetime.utcnow()
            
            db.session.commit()
            
            # Update session count for pending notices
            pending_count = ExitNotice.query.filter_by(
                landlord_id=session['landlord_id'], 
                status='Pending'
            ).count()
            session['pending_exit_notices_count'] = pending_count
            
            # Send SMS notification to tenant
            if status == 'Approved':
                message = f"Your exit notice has been approved. You can vacate on {exit_notice.intended_exit_date.strftime('%Y-%m-%d')}. {response}"
            elif status == 'Rejected':
                message = f"Your exit notice has been rejected. Reason: {response}"
            else:
                message = f"Your exit notice has been updated. Status: {status}. {response}"
            
            send_sms(exit_notice.tenant.phone, message)
            
            flash(f'Exit notice {status.lower()} successfully!', 'success')
            return redirect(url_for('main.landlord_exit_notices'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error responding to exit notice: {str(e)}', 'error')
    
    return render_template('respond_exit_notice.html', exit_notice=exit_notice)


@main.route('/tenant/receipt/<int:rentlog_id>')
def tenant_receipt(rentlog_id):
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        return redirect(url_for('main.tenant_login'))

    rentlog = RentLog.query.get(rentlog_id)
    if not rentlog or rentlog.tenant_id != tenant_id:
        return 'Unauthorized', 403

    tenant = rentlog.tenant
    unit = tenant.unit
    property_ = unit.property

    # QR Code: Verifiable URL
    qr_data = f"https://smartbiller.co.ke/verify/receipt/{rentlog.id}"
    qr = qrcode.make(qr_data)
    qr_buffer = io.BytesIO()
    qr.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_image = ImageReader(qr_buffer)

    # Paths to logo and watermark
    logo_path = os.path.join(current_app.root_path,
                             'static', 'images', 'logo.png')
    watermark_path = logo_path  # reuse logo as watermark

    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Background gradient effect
    p.saveState()
    p.setFillColor(HexColor("#F8FAFC"))
    p.rect(0, 0, width, height, fill=1, stroke=0)
    p.restoreState()

    # Header section with gradient background
    header_height = 120
    p.saveState()
    p.setFillColor(HexColor("#4F46E5"))
    p.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
    p.restoreState()

    # Draw logo if exists
    if os.path.exists(logo_path):
        logo_image = ImageReader(logo_path)
        p.drawImage(logo_image, 50, height - 100, width=70,
                    height=70, preserveAspectRatio=True, mask='auto')

    # Header text
    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawCentredString(width / 2, height - 35, "RENT PAYMENT RECEIPT")
    
    p.setFont("Helvetica", 14)
    p.setFillColor(HexColor("#E0E7FF"))
    p.drawCentredString(width / 2, height - 55, f"{property_.name}")
    p.drawCentredString(width / 2, height - 70, f"{property_.location}")

    # Receipt number and date in top right
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(HexColor("#FFFFFF"))
    p.drawRightString(width - 50, height - 35, f"Receipt #: {rentlog.receipt_number or 'N/A'}")
    p.setFont("Helvetica", 10)
    p.drawRightString(width - 50, height - 50, f"Date: {rentlog.date_paid.strftime('%B %d, %Y')}")

    # Watermark in center
    if os.path.exists(watermark_path):
        watermark_image = ImageReader(watermark_path)
        p.saveState()
        p.translate(width / 2, height / 2)
        p.rotate(45)
        p.setFillAlpha(0.03)
        p.drawImage(watermark_image, -250, -250,
                    width=500, height=500, mask='auto')
        p.restoreState()

    # Main content area
    content_start = height - header_height - 40
    content_width = width - 100
    content_x = 50

    # Tenant Information Section
    section_y = content_start
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#1F2937"))
    p.drawString(content_x, section_y, "TENANT INFORMATION")
    
    # Draw section underline
    p.setStrokeColor(HexColor("#4F46E5"))
    p.setLineWidth(2)
    p.line(content_x, section_y - 5, content_x + 200, section_y - 5)

    # Tenant details in a styled box
    tenant_box_y = section_y - 40
    tenant_box_height = 80
    
    # Box background
    p.saveState()
    p.setFillColor(HexColor("#F3F4F6"))
    p.setStrokeColor(HexColor("#E5E7EB"))
    p.setLineWidth(1)
    p.roundRect(content_x, tenant_box_y - tenant_box_height, content_width, tenant_box_height, 8, fill=1, stroke=1)
    p.restoreState()

    # Tenant details
    tenant_details = [
        ("Name", tenant.name),
        ("Phone", tenant.phone),
        ("Unit", unit.unit_number),
        ("Monthly Rent", f"KES {unit.rent_amount:,.2f}")
    ]

    detail_x = content_x + 20
    detail_y = tenant_box_y - 20
    detail_spacing = 18

    for i, (label, value) in enumerate(tenant_details):
        y_pos = detail_y - (i * detail_spacing)
        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(HexColor("#4F46E5"))
        p.drawString(detail_x, y_pos, label)
        p.setFont("Helvetica", 10)
        p.setFillColor(HexColor("#374151"))
        p.drawString(detail_x + 120, y_pos, value)

    # Payment Details Section
    payment_section_y = tenant_box_y - tenant_box_height - 60
    p.setFont("Helvetica-Bold", 16)
    p.setFillColor(HexColor("#1F2937"))
    p.drawString(content_x, payment_section_y, "PAYMENT DETAILS")
    
    # Draw section underline
    p.setStrokeColor(HexColor("#4F46E5"))
    p.setLineWidth(2)
    p.line(content_x, payment_section_y - 5, content_x + 200, payment_section_y - 5)

    # Payment details in a styled table
    payment_box_y = payment_section_y - 40
    payment_box_height = 120
    
    # Box background
    p.saveState()
    p.setFillColor(HexColor("#FFFFFF"))
    p.setStrokeColor(HexColor("#E5E7EB"))
    p.setLineWidth(1)
    p.roundRect(content_x, payment_box_y - payment_box_height, content_width, payment_box_height, 8, fill=1, stroke=1)
    p.restoreState()

    # Calculate balance
    balance = unit.rent_amount - rentlog.amount_paid
    balance_text = f"KES {balance:,.2f}" if balance > 0 else "KES 0.00"
    balance_color = HexColor("#DC2626") if balance > 0 else HexColor("#059669")

    payment_details = [
        ("Month Paid For", rentlog.month_paid_for, HexColor("#374151")),
        ("Amount Paid", f"KES {rentlog.amount_paid:,.2f}", HexColor("#059669")),
        ("Payment Status", rentlog.status or "Paid", HexColor("#059669")),
        ("Balance Due", balance_text, balance_color)
    ]

    detail_y = payment_box_y - 20
    detail_spacing = 25

    for i, (label, value, color) in enumerate(payment_details):
        y_pos = detail_y - (i * detail_spacing)
        
        # Row background
        if i % 2 == 0:
            p.saveState()
            p.setFillColor(HexColor("#F9FAFB"))
            p.rect(detail_x - 10, y_pos - 8, content_width - 20, 20, fill=1, stroke=0)
            p.restoreState()
        
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(HexColor("#4F46E5"))
        p.drawString(detail_x, y_pos, label)
        p.setFont("Helvetica-Bold", 11)
        p.setFillColor(color)
        p.drawString(detail_x + 200, y_pos, value)

    # QR Code section
    qr_section_y = payment_box_y - payment_box_height - 40
    qr_x = width - 150
    qr_y = qr_section_y - 100
    
    # QR code background
    p.saveState()
    p.setFillColor(HexColor("#FFFFFF"))
    p.setStrokeColor(HexColor("#E5E7EB"))
    p.setLineWidth(1)
    p.roundRect(qr_x - 10, qr_y - 10, 120, 120, 8, fill=1, stroke=1)
    p.restoreState()
    
    # Draw QR code
    p.drawImage(qr_image, qr_x, qr_y, width=100, height=100,
                preserveAspectRatio=True, mask='auto')
    
    # QR code label
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(HexColor("#4F46E5"))
    p.drawCentredString(qr_x + 50, qr_y - 20, "VERIFY RECEIPT")
    p.setFont("Helvetica", 8)
    p.setFillColor(HexColor("#6B7280"))
    p.drawCentredString(qr_x + 50, qr_y - 30, "Scan to verify authenticity")

    # Footer section
    footer_y = 120
    
    # Footer background
    p.saveState()
    p.setFillColor(HexColor("#F3F4F6"))
    p.rect(0, 0, width, footer_y, fill=1, stroke=0)
    p.restoreState()
    
    # Footer border
    p.setStrokeColor(HexColor("#E5E7EB"))
    p.setLineWidth(1)
    p.line(50, footer_y, width - 50, footer_y)

    # Footer content
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(HexColor("#4F46E5"))
    p.drawCentredString(width / 2, footer_y - 20, "Thank you for your payment!")
    
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#6B7280"))
    p.drawCentredString(width / 2, footer_y - 35, f"Signed electronically by SmartBiller on {rentlog.date_paid.strftime('%B %d, %Y')}")
    p.drawCentredString(width / 2, footer_y - 50, "This receipt is computer-generated and does not require a physical signature.")
    
    # Contact information
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(HexColor("#4F46E5"))
    p.drawCentredString(width / 2, footer_y - 70, "Powered by SmartBiller")
    p.setFont("Helvetica", 9)
    p.setFillColor(HexColor("#6B7280"))
    p.drawCentredString(width / 2, footer_y - 85, "https://smartbiller.co.ke • Contact: +254 788 963 983")

    # Finalize
    p.showPage()
    p.save()
    buffer.seek(0)

    filename = f"{tenant.name.replace(' ', '_')}_receipt_{rentlog.month_paid_for.replace(' ', '_')}.pdf"

    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

def generate_bulk_receipts(rentlogs, month, year):
    from zipfile import ZipFile
    buffer = io.BytesIO()
    zip_file = ZipFile(buffer, 'w')

    for rentlog in rentlogs:
        tenant = rentlog.tenant
        unit = tenant.unit
        property_ = unit.property
        
        # QR Code: Verifiable URL
        qr_data = f"https://smartbiller.co.ke/verify/receipt/{rentlog.id}"
        qr = qrcode.make(qr_data)
        qr_buffer = io.BytesIO()
        qr.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = ImageReader(qr_buffer)

        # Paths to logo and watermark
        logo_path = os.path.join(current_app.root_path, 'static', 'images', 'logo.png')
        watermark_path = logo_path  # reuse logo as watermark

        pdf_buffer = io.BytesIO()
        p = canvas.Canvas(pdf_buffer, pagesize=letter)
        width, height = letter

        # Background gradient effect
        p.saveState()
        p.setFillColor(HexColor("#F8FAFC"))
        p.rect(0, 0, width, height, fill=1, stroke=0)
        p.restoreState()

        # Header section with gradient background
        header_height = 120
        p.saveState()
        p.setFillColor(HexColor("#4F46E5"))
        p.rect(0, height - header_height, width, header_height, fill=1, stroke=0)
        p.restoreState()

        # Draw logo if exists
        if os.path.exists(logo_path):
            logo_image = ImageReader(logo_path)
            p.drawImage(logo_image, 50, height - 100, width=70, height=70, preserveAspectRatio=True, mask='auto')

        # Header text
        p.setFont("Helvetica-Bold", 28)
        p.setFillColor(HexColor("#FFFFFF"))
        p.drawCentredString(width / 2, height - 35, "RENT PAYMENT RECEIPT")
        
        p.setFont("Helvetica", 14)
        p.setFillColor(HexColor("#E0E7FF"))
        p.drawCentredString(width / 2, height - 55, f"{property_.name}")
        p.drawCentredString(width / 2, height - 70, f"{property_.location}")

        # Receipt number and date in top right
        p.setFont("Helvetica-Bold", 12)
        p.setFillColor(HexColor("#FFFFFF"))
        p.drawRightString(width - 50, height - 35, f"Receipt #: {rentlog.receipt_number or 'N/A'}")
        p.setFont("Helvetica", 10)
        p.drawRightString(width - 50, height - 50, f"Date: {rentlog.date_paid.strftime('%B %d, %Y')}")

        # Watermark in center
        if os.path.exists(watermark_path):
            watermark_image = ImageReader(watermark_path)
            p.saveState()
            p.translate(width / 2, height / 2)
            p.rotate(45)
            p.setFillAlpha(0.03)
            p.drawImage(watermark_image, -250, -250, width=500, height=500, mask='auto')
            p.restoreState()

        # Main content area
        content_start = height - header_height - 40
        content_width = width - 100
        content_x = 50

        # Tenant Information Section
        section_y = content_start
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(HexColor("#1F2937"))
        p.drawString(content_x, section_y, "TENANT INFORMATION")
        
        # Draw section underline
        p.setStrokeColor(HexColor("#4F46E5"))
        p.setLineWidth(2)
        p.line(content_x, section_y - 5, content_x + 200, section_y - 5)

        # Tenant details in a styled box
        tenant_box_y = section_y - 40
        tenant_box_height = 80
        
        # Box background
        p.saveState()
        p.setFillColor(HexColor("#F3F4F6"))
        p.setStrokeColor(HexColor("#E5E7EB"))
        p.setLineWidth(1)
        p.roundRect(content_x, tenant_box_y - tenant_box_height, content_width, tenant_box_height, 8, fill=1, stroke=1)
        p.restoreState()

        # Tenant details
        tenant_details = [
            ("Name", tenant.name),
            ("Phone", tenant.phone),
            ("Unit", unit.unit_number),
            ("Monthly Rent", f"KES {unit.rent_amount:,.2f}")
        ]

        detail_x = content_x + 20
        detail_y = tenant_box_y - 20
        detail_spacing = 18

        for i, (label, value) in enumerate(tenant_details):
            y_pos = detail_y - (i * detail_spacing)
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(HexColor("#4F46E5"))
            p.drawString(detail_x, y_pos, label)
            p.setFont("Helvetica", 10)
            p.setFillColor(HexColor("#374151"))
            p.drawString(detail_x + 120, y_pos, value)

        # Payment Details Section
        payment_section_y = tenant_box_y - tenant_box_height - 60
        p.setFont("Helvetica-Bold", 16)
        p.setFillColor(HexColor("#1F2937"))
        p.drawString(content_x, payment_section_y, "PAYMENT DETAILS")
        
        # Draw section underline
        p.setStrokeColor(HexColor("#4F46E5"))
        p.setLineWidth(2)
        p.line(content_x, payment_section_y - 5, content_x + 200, payment_section_y - 5)

        # Payment details in a styled table
        payment_box_y = payment_section_y - 40
        payment_box_height = 120
        
        # Box background
        p.saveState()
        p.setFillColor(HexColor("#FFFFFF"))
        p.setStrokeColor(HexColor("#E5E7EB"))
        p.setLineWidth(1)
        p.roundRect(content_x, payment_box_y - payment_box_height, content_width, payment_box_height, 8, fill=1, stroke=1)
        p.restoreState()

        # Calculate balance
        balance = unit.rent_amount - rentlog.amount_paid
        balance_text = f"KES {balance:,.2f}" if balance > 0 else "KES 0.00"
        balance_color = HexColor("#DC2626") if balance > 0 else HexColor("#059669")

        payment_details = [
            ("Month Paid For", rentlog.month_paid_for, HexColor("#374151")),
            ("Amount Paid", f"KES {rentlog.amount_paid:,.2f}", HexColor("#059669")),
            ("Payment Status", rentlog.status or "Paid", HexColor("#059669")),
            ("Balance Due", balance_text, balance_color)
        ]

        detail_y = payment_box_y - 20
        detail_spacing = 25

        for i, (label, value, color) in enumerate(payment_details):
            y_pos = detail_y - (i * detail_spacing)
            
            # Row background
            if i % 2 == 0:
                p.saveState()
                p.setFillColor(HexColor("#F9FAFB"))
                p.rect(detail_x - 10, y_pos - 8, content_width - 20, 20, fill=1, stroke=0)
                p.restoreState()
            
            p.setFont("Helvetica-Bold", 11)
            p.setFillColor(HexColor("#4F46E5"))
            p.drawString(detail_x, y_pos, label)
            p.setFont("Helvetica-Bold", 11)
            p.setFillColor(color)
            p.drawString(detail_x + 200, y_pos, value)

        # QR Code section
        qr_section_y = payment_box_y - payment_box_height - 40
        qr_x = width - 150
        qr_y = qr_section_y - 100
        
        # QR code background
        p.saveState()
        p.setFillColor(HexColor("#FFFFFF"))
        p.setStrokeColor(HexColor("#E5E7EB"))
        p.setLineWidth(1)
        p.roundRect(qr_x - 10, qr_y - 10, 120, 120, 8, fill=1, stroke=1)
        p.restoreState()
        
        # Draw QR code
        p.drawImage(qr_image, qr_x, qr_y, width=100, height=100, preserveAspectRatio=True, mask='auto')
        
        # QR code label
        p.setFont("Helvetica", 8)
        p.setFillColor(HexColor("#6B7280"))
        p.drawCentredString(qr_x + 50, qr_y - 20, "Scan to verify receipt")

        # Footer with company branding
        p.setFillColor(HexColor("#1F2937"))
        p.rect(0, 0, width, 80, fill=1)
        
        p.setFont("Helvetica-Bold", 14)
        p.setFillColor(HexColor("#FFFFFF"))
        p.drawCentredString(width / 2, 50, "SmartBiller - Professional Property Management")
        
        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, 35, "Making property management simple and efficient")
        p.drawCentredString(width / 2, 20, f"Receipt generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")

        p.showPage()
        p.save()
        pdf_buffer.seek(0)

        filename = f"{tenant.name.replace(' ', '_')}_{month}_{year}.pdf"
        zip_file.writestr(filename, pdf_buffer.read())

    zip_file.close()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'receipts_{month}_{year}.zip',
        mimetype='application/zip'
    )


@main.route('/reports', methods=['GET', 'POST'])
def reports():
    if 'landlord_id' not in session:
        flash('Please log in to access reports.')
        return redirect(url_for('main.login'))
    
    landlord_id = session['landlord_id']
    properties = Property.query.filter_by(landlord_id=landlord_id).all()
    
    if not properties:
        flash('No properties found. Please add a property first.')
        return redirect(url_for('main.add_property'))

    if request.method == 'POST':
        try:
            property_id = request.form['property_id']
            month = request.form['month']
            year = request.form['year']

            if not property_id or not month or not year:
                flash('Please select property, month, and year.')
                return render_template('reports.html', properties=properties)

            rentlogs = RentLog.query.join(Tenant).join(Unit).filter(
                Unit.property_id == property_id,
                RentLog.date_paid.between(
                    f"{year}-{month}-01", f"{year}-{month}-31")
            ).all()

            if not rentlogs:
                flash(f'No payment records found for {month} {year}.')
                return render_template('reports.html', properties=properties)

            flash(f'Generating report for {month} {year}...')
            return generate_bulk_receipts(rentlogs, month, year)
            
        except Exception as e:
            flash(f'Error generating report: {str(e)}')
            return render_template('reports.html', properties=properties)

    return render_template('reports.html', properties=properties)


def send_unpaid_reminders():
    current_month = datetime.now().strftime('%B %Y')
    landlords = Landlord.query.all()

    for landlord in landlords:
        for prop in landlord.properties:
            for unit in prop.units:
                tenant = unit.tenant
                if tenant:
                    rent_log = RentLog.query.filter_by(
                        tenant_id=tenant.id,
                        month_paid_for=current_month
                    ).first()

                    if not rent_log or (rent_log and rent_log.status != 'Paid'):
                        message = (
                            f"Dear {tenant.name}, your rent for {current_month} "
                            f"is marked as '{rent_log.status if rent_log else 'Unpaid'}'. "
                            f"Please pay KES {unit.rent_amount} to avoid penalties."
                        )
                        send_sms(tenant.phone, message)


@main.route('/send_month_end_reminders')
def trigger_unpaid_reminders():
    send_unpaid_reminders()
    flash("Unpaid reminders sent.")
    return redirect(url_for('main.dashboard'))


@main.route('/generate_invoice/<int:tenant_id>', methods=['GET', 'POST'])
def generate_invoice(tenant_id):
    if 'landlord_id' not in session:
        flash('Please log in to generate invoices.')
        return redirect(url_for('main.login'))
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant or tenant.unit.property.landlord_id != session['landlord_id']:
        flash('Tenant not found or unauthorized.')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            month = request.form['month']
            year = request.form['year']
            rent_amount = float(request.form['rent_amount'])
            
            # Parse additional charges
            additional_charges = []
            charge_descriptions = request.form.getlist('charge_description[]')
            charge_amounts = request.form.getlist('charge_amount[]')
            
            for desc, amount in zip(charge_descriptions, charge_amounts):
                if desc.strip() and amount.strip():
                    additional_charges.append({
                        'description': desc.strip(),
                        'amount': float(amount)
                    })
            
            notes = request.form.get('notes', '').strip()
            
            # Generate invoice
            from app.scheduled_tasks import generate_custom_invoice, send_custom_invoice_email, send_custom_invoice_sms, update_usage_logs
            
            invoice_buffer, total_amount = generate_custom_invoice(
                tenant, month, year, rent_amount, additional_charges, notes
            )
            
            # Save invoice PDF to file
            invoice_number = generate_invoice_number()
            pdf_filename = f"invoice_{invoice_number}_{tenant.name.replace(' ', '_')}.pdf"
            invoices_dir = os.path.join(current_app.root_path, 'static', 'invoices')
            os.makedirs(invoices_dir, exist_ok=True)
            pdf_path = os.path.join(invoices_dir, pdf_filename)
            
            # Save the PDF buffer to file
            with open(pdf_path, 'wb') as f:
                f.write(invoice_buffer.getvalue())
            
            # Create invoice record in database
            invoice = Invoice(
                tenant_id=tenant_id,
                landlord_id=session['landlord_id'],
                invoice_number=invoice_number,
                month=month,
                year=int(year),
                base_rent=rent_amount,
                additional_charges=json.dumps(additional_charges),
                total_amount=total_amount,
                notes=notes,
                pdf_path=os.path.join('invoices', pdf_filename)
            )
            
            db.session.add(invoice)
            
            # Create unpaid payment record showing what should be paid
            month_paid_for = f"{month} {year}"
            
            # Check if there's already a payment record for this month
            existing_payment = RentLog.query.filter_by(
                tenant_id=tenant_id,
                month_paid_for=month_paid_for
            ).first()
            
            if existing_payment:
                # Update existing record with new invoice amount (but don't mark as paid)
                existing_payment.amount_paid = 0  # Reset to 0 since this is what was actually paid
                existing_payment.status = "Unpaid"
                # Don't update date_paid as no payment was made
            else:
                # Create new unpaid payment record
                rent_log = RentLog(
                    tenant_id=tenant_id,
                    amount_paid=0,  # No payment made yet
                    date_paid=datetime.now(),  # Date invoice was generated
                    month_paid_for=month_paid_for,
                    status="Unpaid"
                )
                
                db.session.add(rent_log)
            
            db.session.commit()
            
            # Send via email if tenant has email and landlord has permission
            email_sent = False
            if tenant.email and SubscriptionService.can_send_email(session['landlord_id']):
                email_sent = send_custom_invoice_email(tenant, invoice_buffer, month, year, total_amount, additional_charges)
                if email_sent:
                    update_usage_logs(session['landlord_id'], 'email_sent')
            
            # Send SMS if landlord has permission
            if SubscriptionService.can_send_sms(session['landlord_id']):
                send_custom_invoice_sms(tenant, month, year, total_amount, additional_charges)
                update_usage_logs(session['landlord_id'], 'sms_sent')
            
            # Success message and redirect
            if email_sent:
                flash(f"Invoice generated and sent to {tenant.name} via email and SMS! Invoice for KES {total_amount:,.2f} saved to tenant portal. Payment record created as 'Unpaid' - use 'Log Rent' to record actual payments received.", 'success')
            else:
                flash(f"Invoice generated for {tenant.name}! SMS sent. Invoice for KES {total_amount:,.2f} saved to tenant portal. Payment record created as 'Unpaid' - use 'Log Rent' to record actual payments received.", 'success')
            
            # Redirect to dashboard instead of downloading
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            flash(f'Error generating invoice: {str(e)}')
            return redirect(url_for('main.dashboard'))
    
    # GET request - show invoice form
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    
    return render_template('generate_invoice.html', 
                         tenant=tenant,
                         current_month=current_month,
                         current_year=current_year)


@main.route('/invoice_management')
def invoice_management():
    if 'landlord_id' not in session:
        flash('Please log in to access invoice management.')
        return redirect(url_for('main.login'))
    
    landlord_id = session['landlord_id']
    properties = Property.query.filter_by(landlord_id=landlord_id).all()
    
    # Get all tenants with their units and properties
    tenants = []
    for property_ in properties:
        for unit in property_.units:
            if unit.tenant:
                tenants.append({
                    'tenant': unit.tenant,
                    'unit': unit,
                    'property': property_
                })
    
    return render_template('invoice_management.html', tenants=tenants)


@main.route('/download_invoice/<int:invoice_id>')
def download_invoice(invoice_id):
    if 'landlord_id' not in session:
        flash('Please log in to download invoices.')
        return redirect(url_for('main.login'))
    
    invoice = Invoice.query.get(invoice_id)
    if not invoice or invoice.landlord_id != session['landlord_id']:
        flash('Invoice not found or unauthorized.')
        return redirect(url_for('main.dashboard'))
    
    # Check if PDF file exists
    pdf_path = os.path.join(current_app.root_path, 'static', invoice.pdf_path)
    if not os.path.exists(pdf_path):
        flash('Invoice file not found.')
        return redirect(url_for('main.dashboard'))
    
    # Send file for download
    filename = f"{invoice.tenant.name.replace(' ', '_')}_invoice_{invoice.month}_{invoice.year}.pdf"
    return send_file(pdf_path, as_attachment=True, download_name=filename, mimetype='application/pdf')


@main.route('/send_monthly_invoices')
def trigger_monthly_invoices():
    if 'landlord_id' not in session:
        flash('Please log in to send invoices.')
        return redirect(url_for('main.login'))
    
    flash("Please use the 'Invoice Management' feature for individual tenants with custom amounts.")
    return redirect(url_for('main.dashboard'))


@main.route('/send_late_reminders')
def trigger_late_reminders():
    if 'landlord_id' not in session:
        flash('Please log in to send reminders.')
        return redirect(url_for('main.login'))
    
    try:
        from app.scheduled_tasks import send_late_payment_reminders
        send_late_payment_reminders()
        flash("Late payment reminders sent successfully!")
    except Exception as e:
        flash(f"Error sending reminders: {str(e)}")
    
    return redirect(url_for('main.dashboard'))

def calculate_tenant_balance(tenant_id, selected_month=None):
    """Calculate tenant's balance including carry-forward payments and invoiced amounts"""
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return 0, 0, 0, 0, 0
    
    unit = tenant.unit
    monthly_rent = unit.rent_amount
    
    # Get all payments for this tenant
    all_payments = RentLog.query.filter_by(tenant_id=tenant_id).order_by(RentLog.date_paid).all()
    
    if not selected_month:
        selected_month = datetime.now().strftime('%B %Y')
    
    # Check if there's an invoice for the selected month with additional charges
    invoice_for_month = Invoice.query.filter_by(
        tenant_id=tenant_id,
        month=selected_month.split()[0],
        year=int(selected_month.split()[1])
    ).first()
    
    # Use invoice total if available, otherwise use monthly rent
    amount_due_for_month = invoice_for_month.total_amount if invoice_for_month else monthly_rent
    additional_charges = (invoice_for_month.total_amount - monthly_rent) if invoice_for_month and invoice_for_month.total_amount > monthly_rent else 0
    
    # Get payment for selected month
    month_payment = RentLog.query.filter_by(
        tenant_id=tenant_id,
        month_paid_for=selected_month
    ).first()
    
    month_paid = month_payment.amount_paid if month_payment else 0
    month_balance = amount_due_for_month - month_paid
    
    # Calculate total paid
    total_paid = sum(payment.amount_paid for payment in all_payments)
    
    # Calculate overall balance using actual invoice amounts
    # Get all invoices for this tenant
    all_invoices = Invoice.query.filter_by(tenant_id=tenant_id).all()
    
    # Calculate total invoiced amount
    total_invoiced = sum(inv.total_amount for inv in all_invoices)
    
    # If no invoices, use monthly rent for months with payments
    if total_invoiced == 0:
        unique_months = set(payment.month_paid_for for payment in all_payments)
        months_with_payments = len(unique_months)
        
        # If selected month has no payment, add it to what's owed
        if selected_month not in unique_months:
            months_owed = months_with_payments + 1
        else:
            months_owed = months_with_payments
        
        total_should_be_owed = months_owed * monthly_rent
    else:
        total_should_be_owed = total_invoiced
    
    overall_balance = total_should_be_owed - total_paid
    
    return month_balance, total_paid, overall_balance, additional_charges, amount_due_for_month

@main.route('/test_balance/<int:tenant_id>')
def test_balance(tenant_id):
    """Test route to verify balance calculation"""
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'error': 'Tenant not found'})
    
    # Test balance calculation
    month_balance, total_paid, overall_balance = calculate_tenant_balance(tenant_id)
    
    # Get all payments for this tenant
    all_payments = RentLog.query.filter_by(tenant_id=tenant_id).order_by(RentLog.date_paid).all()
    
    result = {
        'tenant_name': tenant.name,
        'unit_number': tenant.unit.unit_number,
        'monthly_rent': tenant.unit.rent_amount,
        'current_month_balance': month_balance,
        'total_paid': total_paid,
        'overall_balance': overall_balance,
        'payments': [
            {
                'amount': payment.amount_paid,
                'date': payment.date_paid.strftime('%Y-%m-%d'),
                'month_paid_for': payment.month_paid_for,
                'status': payment.status
            }
            for payment in all_payments
        ]
    }
    
    return jsonify(result)


@main.route('/debug/login_codes')
def debug_login_codes():
    """Debug route to show current login codes (development only)"""
    tenants_with_codes = Tenant.query.filter(
        Tenant.login_code.isnot(None),
        Tenant.login_code_expiry > datetime.utcnow()
    ).all()
    
    print(f"\n{'='*60}")
    print(f"ACTIVE LOGIN CODES DEBUG")
    print(f"{'='*60}")
    print(f"Current Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Active Codes: {len(tenants_with_codes)}")
    print(f"{'='*60}")
    
    for tenant in tenants_with_codes:
        print(f"Tenant: {tenant.name}")
        print(f"Email: {tenant.email}")
        print(f"Phone: {tenant.phone}")
        print(f"Code: {tenant.login_code}")
        print(f"Expires: {tenant.login_code_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Time Left: {tenant.login_code_expiry - datetime.utcnow()}")
        print(f"{'-'*40}")
    
    print(f"{'='*60}\n")
    
    return jsonify({
        'current_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'active_codes': len(tenants_with_codes),
        'codes': [
            {
                'tenant_name': tenant.name,
                'email': tenant.email,
                'phone': tenant.phone,
                'code': tenant.login_code,
                'expires': tenant.login_code_expiry.strftime('%Y-%m-%d %H:%M:%S'),
                'time_left': str(tenant.login_code_expiry - datetime.utcnow())
            }
            for tenant in tenants_with_codes
        ]
    })

@main.route('/upgrade')
def upgrade():
    if 'landlord_id' not in session:
        return redirect(url_for('main.login'))
    
    print(f"DEBUG: Upgrade route accessed for landlord {session['landlord_id']}")
    
    try:
        # Get landlord and current plan/usage
        landlord = Landlord.query.get(session['landlord_id'])
        current_plan = SubscriptionService.get_landlord_plan(session['landlord_id'])
        usage = SubscriptionService.get_usage_summary(session['landlord_id'])
        
        print(f"DEBUG: Current plan: {current_plan}")
        print(f"DEBUG: Usage: {usage}")
        
        # Check if user is in trial period
        is_trial_active = SubscriptionService.is_trial_active(session['landlord_id'])
        trial_days_remaining = 0
        if is_trial_active and landlord.trial_ends_at:
            trial_days_remaining = (landlord.trial_ends_at - datetime.utcnow()).days
        
        # If no current plan but trial is active, create a default trial plan
        if not current_plan and is_trial_active:
            # Create a default trial plan for display purposes
            from app.models import PricingPlan
            trial_plan = PricingPlan.query.filter_by(code='trial').first()
            if not trial_plan:
                # Create a trial plan if it doesn't exist
                trial_plan = PricingPlan(
                    name='Free Trial',
                    code='trial',
                    monthly_price=0,
                    yearly_price=0,
                    max_properties=999,
                    max_sms_per_month=50,
                    features='["Unlimited Properties", "50 SMS/month", "Basic Support"]',
                    is_active=True
                )
                db.session.add(trial_plan)
                db.session.commit()
            current_plan = trial_plan
        
        # If still no current plan, redirect to pricing
        if not current_plan:
            print(f"DEBUG: No current plan found")
            flash('No active subscription found. Please select a plan to continue.', 'error')
            return redirect(url_for('main.pricing'))
        
        # Check if user has reached plan limits
        has_reached_limits = False
        if current_plan and usage:
            # Check property limit
            if usage.get('properties_count', 0) >= current_plan.max_properties:
                has_reached_limits = True
            # Check SMS limit
            elif usage.get('sms_sent', 0) >= current_plan.max_sms_per_month:
                has_reached_limits = True
            # Check if they're trying to add more units than allowed
            elif usage.get('units_count', 0) >= current_plan.max_units_per_property:
                has_reached_limits = True
        
        # Get current plan features
        import json
        current_features = json.loads(current_plan.features) if current_plan.features else []
        print(f"DEBUG: Current features: {current_features}")
        print(f"DEBUG: Has reached limits: {has_reached_limits}")
        
        # Get all available pricing plans for comparison
        all_plans = SubscriptionService.get_pricing_plans()
        
        return render_template('upgrade.html', 
                             current_plan=current_plan, 
                             usage=usage, 
                             current_features=current_features,
                             is_trial_active=is_trial_active,
                             trial_days_remaining=trial_days_remaining,
                             has_reached_limits=has_reached_limits,
                             all_plans=all_plans)
    except Exception as e:
        print(f"DEBUG: Error in upgrade route: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading upgrade page: {e}', 'error')
        return redirect(url_for('main.dashboard'))

@main.route('/upgrade_plan/<plan>')
def upgrade_plan(plan):
    if 'landlord_id' not in session:
        flash('Please log in to upgrade your plan.', 'error')
        return redirect(url_for('main.login'))
    
    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Landlord not found.', 'error')
        return redirect(url_for('main.login'))
    
    # Get plan details
    plan_details = SubscriptionService.get_plan_by_code(plan)
    print(f"DEBUG: Plan details: {plan_details}")
    if not plan_details:
        flash('Invalid plan selected.', 'error')
        return redirect(url_for('main.upgrade'))
    
    return render_template('payment.html', 
                         plan=plan_details, 
                         landlord=landlord,
                         current_plan=SubscriptionService.get_landlord_plan(landlord.id))
                         

@main.route('/process_payment', methods=['POST'])
def process_payment():
    if 'landlord_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to upgrade your plan.'})
    
    try:
        landlord = Landlord.query.get(session['landlord_id'])
        if not landlord:
            return jsonify({'success': False, 'message': 'Landlord not found.'})
        
        # Get form data
        plan_code = request.form.get('plan_code')
        billing_cycle = request.form.get('billing_cycle', 'monthly')
        card_number = request.form.get('card_number')
        expiry_month = request.form.get('expiry_month')
        expiry_year = request.form.get('expiry_year')
        cvv = request.form.get('cvv')
        cardholder_name = request.form.get('cardholder_name')
        
        # Validate required fields
        if not all([plan_code, card_number, expiry_month, expiry_year, cvv, cardholder_name]):
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
        
        # Get plan details
        plan = SubscriptionService.get_plan_by_code(plan_code)
        if not plan:
            return jsonify({'success': False, 'message': 'Invalid plan selected.'})
        
        # Validate card details (basic validation)
        if len(card_number.replace(' ', '')) < 13 or len(card_number.replace(' ', '')) > 19:
            return jsonify({'success': False, 'message': 'Invalid card number.'})
        
        if len(cvv) < 3 or len(cvv) > 4:
            return jsonify({'success': False, 'message': 'Invalid CVV.'})
        
        # Calculate amount based on billing cycle
        amount = plan.yearly_price if billing_cycle == 'yearly' else plan.monthly_price
        
        # In a real application, you would integrate with a payment processor here
        # For now, we'll simulate a successful payment
        payment_reference = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{landlord.id}"
        
        # Create the subscription
        subscription = SubscriptionService.create_subscription(
            landlord_id=landlord.id,
            plan_code=plan_code,
            billing_cycle=billing_cycle,
            payment_method='card',
            payment_reference=payment_reference
        )
        
        if subscription:
            flash(f'Successfully upgraded to {plan.name} plan!', 'success')
            return jsonify({
                'success': True, 
                'message': f'Successfully upgraded to {plan.name} plan!',
                'redirect_url': url_for('main.dashboard')
            })
        else:
            return jsonify({'success': False, 'message': 'Failed to create subscription.'})
            
    except Exception as e:
        print(f"Payment processing error: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while processing your payment. Please try again.'})

@main.route('/test_upgrade')
def test_upgrade():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Upgrade</title>
    </head>
    <body>
        <h1>Test Upgrade Page</h1>
        <p>This is a simple test page to check if the issue is with the base template.</p>
        <p>If you can see this, the issue is with the upgrade template.</p>
    </body>
    </html>
    """

@main.route('/api/theme', methods=['POST'])
def update_theme():
    """API endpoint to update user theme preference"""
    if 'landlord_id' not in session:
        return jsonify({'success': False, 'message': 'User not authenticated'}), 401
    
    try:
        data = request.get_json()
        theme = data.get('theme')
        
        if theme not in ['light', 'dark']:
            return jsonify({'success': False, 'message': 'Invalid theme'}), 400
        
        # Store theme preference in session
        session['theme'] = theme
        
        # Optionally store in database for persistent preference
        landlord = Landlord.query.get(session['landlord_id'])
        if landlord:
            landlord.theme_preference = theme
            db.session.commit()
        
        return jsonify({'success': True, 'theme': theme})
        
    except Exception as e:
        print(f"Error updating theme: {e}")
        return jsonify({'success': False, 'message': 'Error updating theme'}), 500

@main.route('/theme-demo')
def theme_demo():
    """Demo page to showcase dark/light mode functionality"""
    return render_template('theme_demo.html')

def init_app(app):
    """Initialize the routes with the app"""
    app.register_blueprint(main)


# Employee Management Routes
@main.route('/employees')
def employees():
    if 'landlord_id' not in session:
        flash('Please log in to manage employees.', 'error')
        return redirect(url_for('main.login'))
    
    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Landlord not found.', 'error')
        return redirect(url_for('main.login'))
    
    # Get both active and inactive employees
    active_employees = Employee.query.filter_by(landlord_id=landlord.id, is_active=True).order_by(Employee.created_at.desc()).all()
    inactive_employees = Employee.query.filter_by(landlord_id=landlord.id, is_active=False).order_by(Employee.created_at.desc()).all()
    
    return render_template('employees.html', 
                         active_employees=active_employees, 
                         inactive_employees=inactive_employees, 
                         landlord=landlord)


@main.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    if 'landlord_id' not in session:
        flash('Please log in to add employees.', 'error')
        return redirect(url_for('main.login'))
    
    landlord = Landlord.query.get(session['landlord_id'])
    if not landlord:
        flash('Landlord not found.', 'error')
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form.get('phone')
            position = request.form.get('position', 'Property Manager')
            
            # Validate required fields
            if not name or not email:
                flash('Name and email are required.', 'error')
                return render_template('add_employee.html', landlord=landlord)
            
            # Check if email already exists (only active employees)
            existing_employee = Employee.query.filter_by(email=email, is_active=True).first()
            if existing_employee:
                flash('An employee with this email already exists.', 'error')
                return render_template('add_employee.html', landlord=landlord)
            
            # Generate password for employee (they can change it later)
            default_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            hashed_password = generate_password_hash(default_password)
            
            # Create new employee
            employee = Employee(
                name=name,
                email=email,
                phone=phone,
                password=hashed_password,
                position=position,
                landlord_id=landlord.id
            )
            
            db.session.add(employee)
            db.session.commit()
            
            # Send welcome email with login credentials
            email_sent = send_employee_welcome_email(employee, default_password, landlord.name)
            
            if email_sent:
                flash(f'Employee {name} added successfully! Welcome email sent with login credentials.', 'success')
            else:
                flash(f'Employee {name} added successfully! Default password: {default_password} (Email failed to send)', 'warning')
            
            return redirect(url_for('main.employees'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
            return render_template('add_employee.html', landlord=landlord)
    
    return render_template('add_employee.html', landlord=landlord)


@main.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
def edit_employee(employee_id):
    if 'landlord_id' not in session:
        flash('Please log in to edit employees.', 'error')
        return redirect(url_for('main.login'))
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Verify ownership
    if employee.landlord_id != session['landlord_id']:
        flash('Unauthorized access to this employee.', 'error')
        return redirect(url_for('main.employees'))
    
    if request.method == 'POST':
        try:
            employee.name = request.form['name']
            employee.email = request.form['email']
            employee.phone = request.form.get('phone')
            employee.position = request.form.get('position', 'Property Manager')
            
            # Check if email is being changed and if it's already in use (only active employees)
            new_email = request.form['email']
            if new_email != employee.email:
                existing_employee = Employee.query.filter_by(email=new_email, is_active=True).first()
                if existing_employee and existing_employee.id != employee.id:
                    flash('An employee with this email already exists.', 'error')
                    return render_template('edit_employee.html', employee=employee)
            
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('main.employees'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')
            return render_template('edit_employee.html', employee=employee)
    
    return render_template('edit_employee.html', employee=employee)


@main.route('/employees/<int:employee_id>/delete', methods=['POST'])
def delete_employee(employee_id):
    if 'landlord_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to delete employees.'})
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Verify ownership
    if employee.landlord_id != session['landlord_id']:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        # Soft delete - mark as inactive instead of actually deleting
        employee.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Employee deactivated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})


@main.route('/employees/<int:employee_id>/activate', methods=['POST'])
def activate_employee(employee_id):
    if 'landlord_id' not in session:
        return jsonify({'success': False, 'message': 'Please log in to activate employees.'})
    
    employee = Employee.query.get_or_404(employee_id)
    
    # Verify ownership
    if employee.landlord_id != session['landlord_id']:
        return jsonify({'success': False, 'message': 'Unauthorized access'})
    
    try:
        # Get landlord name for email
        landlord = Landlord.query.get(session['landlord_id'])
        landlord_name = landlord.name if landlord else 'Your Landlord'
        
        # Activate employee
        employee.is_active = True
        db.session.commit()
        
        # Send reactivation email
        email_sent = send_employee_reactivation_email(employee, landlord_name)
        
        if email_sent:
            return jsonify({'success': True, 'message': 'Employee activated successfully! Reactivation email sent.'})
        else:
            return jsonify({'success': True, 'message': 'Employee activated successfully! (Email failed to send)'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Employee Management Routes
@main.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Find employee by email
        employee = Employee.query.filter_by(email=email, is_active=True).first()
        
        if employee and check_password_hash(employee.password, password):
            # Store employee info in session
            session['employee_id'] = employee.id
            session['employee_name'] = employee.name
            session['employee_position'] = employee.position
            session['landlord_id'] = employee.landlord_id  # Employee works for this landlord
            
            flash(f'Welcome back, {employee.name}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials or employee not found.', 'error')
    
    return render_template('employee_login.html')


@main.route('/employee_logout')
def employee_logout():
    if 'employee_id' in session:
        employee_name = session.get('employee_name', 'Employee')
        session.pop('employee_id', None)
        session.pop('employee_name', None)
        session.pop('employee_position', None)
        session.pop('landlord_id', None)
        flash(f'{employee_name} has been logged out successfully.', 'success')
        return redirect(url_for('main.employee_login'))
    else:
        return redirect(url_for('main.employee_login'))

@main.route('/employee_reset_password', methods=['GET', 'POST'])
def employee_reset_password():
    if request.method == 'POST':
        email = request.form['email']
        
        # Find employee by email
        employee = Employee.query.filter_by(email=email, is_active=True).first()
        
        if employee:
            # Generate new password
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            employee.password = generate_password_hash(new_password)
            db.session.commit()
            
            # Send password via SMS (mock)
            message = f'Your SmartBiller password has been reset. New password: {new_password}'
            send_sms(employee.phone, message)
            
            flash(f'Password reset successful! New password sent to {employee.phone}', 'success')
        else:
            flash('No employee found with that email address.', 'error')
    
    return render_template('employee_reset_password.html')


@main.route('/employee_change_password', methods=['GET', 'POST'])
def employee_change_password():
    if 'employee_id' not in session:
        flash('Please log in to change your password.', 'error')
        return redirect(url_for('main.employee_login'))
    
    employee = Employee.query.get(session['employee_id'])
    if not employee:
        flash('Employee not found.', 'error')
        return redirect(url_for('main.employee_login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Verify current password
        if not check_password_hash(employee.password, current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('employee_change_password.html')
        
        # Check if new passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('employee_change_password.html')
        
        # Update password
        employee.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('employee_change_password.html')

@main.route('/test_email')
def test_email():
    """Test route to verify email functionality"""
    try:
        from app import mail
        from flask_mail import Message
        msg = Message(
            subject="SmartBiller Email Test",
            recipients=["test@example.com"],
            body="This is a test email from SmartBiller to verify email functionality is working."
        )
        mail.send(msg)
        return jsonify({"success": True, "message": "Test email sent successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Email test failed: {str(e)}"})

@main.route('/test_error_notification')
def test_error_notification():
    """Test route to verify error notification functionality"""
    try:
        # Simulate a critical error
        ErrorNotificationService.log_and_notify_error(
            error_type='TestError',
            error_message='This is a test error notification to verify the system is working.',
            stack_trace='Traceback (most recent call last):\n  File "test.py", line 1, in <module>\n    raise Exception("Test error")\nException: Test error',
            user_id=1,
            user_type='admin',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Test Browser)',
            url='/test_error_notification',
            method='GET',
            severity='critical'
        )
        return jsonify({"success": True, "message": "Test error notification sent successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error notification test failed: {str(e)}"})

@main.route('/test_daily_summary')
def test_daily_summary():
    """Test route to verify daily error summary functionality"""
    try:
        success = ErrorNotificationService.send_daily_error_summary()
        if success:
            return jsonify({"success": True, "message": "Daily error summary sent successfully"})
        else:
            return jsonify({"success": False, "message": "No errors to report in daily summary"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Daily summary test failed: {str(e)}"})

@main.route('/property_history')
def property_history():
    if 'landlord_id' not in session:
        flash('Please log in to view property history.')
        return redirect(url_for('main.login'))
    
    landlord_id = session['landlord_id']
    
    # Get all properties for this landlord
    properties = Property.query.filter_by(landlord_id=landlord_id).all()
    
    # Get all rent logs for all tenants across all properties
    all_rent_logs = []
    property_stats = {}
    
    for property in properties:
        property_total = 0
        property_payments = 0
        property_paid_count = 0
        
        for unit in property.units:
            if unit.tenant:
                tenant_logs = RentLog.query.filter_by(tenant_id=unit.tenant.id).order_by(RentLog.date_paid.desc()).all()
                
                for log in tenant_logs:
                    # Add property and unit info to the log object
                    log.property_name = property.name
                    log.unit_number = unit.unit_number
                    log.tenant_name = unit.tenant.name
                    all_rent_logs.append(log)
                    
                    # Calculate property stats
                    property_total += log.amount_paid
                    property_payments += 1
                    if log.status == 'Paid':
                        property_paid_count += 1
        
        property_stats[property.id] = {
            'name': property.name,
            'total_collected': property_total,
            'total_payments': property_payments,
            'paid_count': property_paid_count,
            'payment_rate': (property_paid_count / property_payments * 100) if property_payments > 0 else 0
        }
    
    # Sort by date (most recent first)
    all_rent_logs.sort(key=lambda x: x.date_paid, reverse=True)
    
    # Calculate overall stats
    total_collected = sum(log.amount_paid for log in all_rent_logs)
    total_payments = len(all_rent_logs)
    paid_payments = len([log for log in all_rent_logs if log.status == 'Paid'])
    payment_rate = (paid_payments / total_payments * 100) if total_payments > 0 else 0
    
    return render_template('property_history.html', 
                         rent_logs=all_rent_logs,
                         property_stats=property_stats,
                         total_collected=total_collected,
                         total_payments=total_payments,
                         paid_payments=paid_payments,
                         payment_rate=payment_rate)

# Admin Routes and Monitoring
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['admin_role'] = admin.role
            
            # Update last login
            admin.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log successful login
            log_system_event('info', 'auth', f'Admin login successful: {username}', 
                           admin.id, 'admin', request.remote_addr, request.user_agent.string)
            
            flash('Welcome to Admin Dashboard!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            # Log failed login attempt
            log_system_event('warning', 'auth', f'Failed admin login attempt: {username}', 
                           None, 'admin', request.remote_addr, request.user_agent.string)
            
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('admin/login.html')

@main.route('/admin/logout')
def admin_logout():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        log_system_event('info', 'auth', 'Admin logout', admin_id, 'admin', 
                        request.remote_addr, request.user_agent.string)
        
        session.pop('admin_id', None)
        session.pop('admin_role', None)
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.admin_login'))

@main.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get system statistics
    stats = get_system_statistics()
    
    # Get recent activities
    recent_logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
    
    # Get security alerts
    security_alerts = SecurityAlert.query.filter_by(resolved=False).order_by(SecurityAlert.created_at.desc()).limit(5).all()
    
    # Get error logs
    error_logs = ErrorLog.query.filter_by(resolved=False).order_by(ErrorLog.created_at.desc()).limit(5).all()
    
    # Get database health
    db_health = DatabaseHealth.query.order_by(DatabaseHealth.recorded_at.desc()).first()
    
    return render_template('admin/dashboard.html', 
                         stats=stats, 
                         recent_logs=recent_logs,
                         security_alerts=security_alerts,
                         error_logs=error_logs,
                         db_health=db_health)

@main.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get all user types with pagination
    page = request.args.get('page', 1, type=int)
    user_type = request.args.get('type', 'all')
    
    if user_type == 'landlords':
        users = Landlord.query.paginate(page=page, per_page=20, error_out=False)
    elif user_type == 'tenants':
        users = Tenant.query.paginate(page=page, per_page=20, error_out=False)
    elif user_type == 'employees':
        users = Employee.query.paginate(page=page, per_page=20, error_out=False)
    else:
        # Show landlords by default
        users = Landlord.query.paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users, user_type=user_type)

@main.route('/admin/analytics')
def admin_analytics():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get analytics data
    analytics = get_analytics_data()
    
    return render_template('admin/analytics.html', analytics=analytics)

@main.route('/admin/security')
def admin_security():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get security data
    login_attempts = LoginAttempt.query.order_by(LoginAttempt.created_at.desc()).limit(50).all()
    security_alerts = SecurityAlert.query.order_by(SecurityAlert.created_at.desc()).limit(20).all()
    
    return render_template('admin/security.html', 
                         login_attempts=login_attempts,
                         security_alerts=security_alerts)

@main.route('/admin/logs')
def admin_logs():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get logs with filters
    level = request.args.get('level', 'all')
    category = request.args.get('category', 'all')
    page = request.args.get('page', 1, type=int)
    
    query = SystemLog.query
    
    if level != 'all':
        query = query.filter_by(level=level)
    if category != 'all':
        query = query.filter_by(category=category)
    
    logs = query.order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)
    
    return render_template('admin/logs.html', logs=logs, level=level, category=category)

@main.route('/admin/errors')
def admin_errors():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    page = request.args.get('page', 1, type=int)
    resolved = request.args.get('resolved', 'unresolved')
    
    query = ErrorLog.query
    
    if resolved == 'resolved':
        query = query.filter_by(resolved=True)
    elif resolved == 'unresolved':
        query = query.filter_by(resolved=False)
    
    errors = query.order_by(ErrorLog.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/errors.html', errors=errors, resolved=resolved)

@main.route('/admin/error/<int:error_id>/resolve', methods=['POST'])
def resolve_error(error_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    error = ErrorLog.query.get_or_404(error_id)
    error.resolved = True
    error.resolved_at = datetime.utcnow()
    error.resolved_by = session['admin_id']
    db.session.commit()
    
    # Log the action
    log_system_event('info', 'error', f'Admin resolved error {error_id}', 
                     session['admin_id'], 'admin', request.remote_addr, request.user_agent.string)
    
    flash('Error marked as resolved.', 'success')
    return redirect(url_for('main.admin_errors'))

@main.route('/admin/change-password', methods=['GET', 'POST'])
def admin_change_password():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    admin = Admin.query.get(session['admin_id'])
    if not admin:
        flash('Admin user not found.', 'error')
        return redirect(url_for('main.admin_login'))
    
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate current password
        if not check_password_hash(admin.password, current_password):
            flash('Current password is incorrect.', 'error')
            return render_template('admin/change_password.html')
        
        # Validate new password
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'error')
            return render_template('admin/change_password.html')
        
        # Validate password confirmation
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return render_template('admin/change_password.html')
        
        # Update password
        try:
            admin.password = generate_password_hash(new_password)
            admin.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Log password change
            log_system_event('info', 'auth', f'Admin password changed: {admin.username}', 
                           admin.id, 'admin', request.remote_addr, request.user_agent.string)
            
            flash('Password updated successfully!', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            flash(f'Error updating password: {str(e)}', 'error')
            db.session.rollback()
    
    return render_template('admin/change_password.html')

@main.route('/admin/alert/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    alert = SecurityAlert.query.get_or_404(alert_id)
    alert.resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = session['admin_id']
    
    db.session.commit()
    
    flash('Security alert marked as resolved.', 'success')
    return redirect(url_for('main.admin_security'))

# Global error handler
@main.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler that logs errors and sends notifications"""
    try:
        # Get error details
        error_type = type(e).__name__
        error_message = str(e)
        stack_trace = traceback.format_exc()
        
        # Get request details
        user_id = session.get('landlord_id') or session.get('admin_id') or session.get('employee_id')
        user_type = 'landlord' if 'landlord_id' in session else 'admin' if 'admin_id' in session else 'employee' if 'employee_id' in session else 'guest'
        
        # Determine severity based on error type
        severity = 'critical' if error_type in ['DatabaseError', 'ConnectionError', 'SecurityViolation'] else 'high'
        
        # Log and notify about the error
        ErrorNotificationService.log_and_notify_error(
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            user_id=user_id,
            user_type=user_type,
            ip_address=request.remote_addr if request else None,
            user_agent=request.user_agent.string if request and request.user_agent else None,
            url=request.url if request else None,
            method=request.method if request else None,
            severity=severity
        )
        
        # Log system event
        log_system_event('error', 'system', f'Unhandled exception: {error_type} - {error_message}', 
                        user_id, user_type, request.remote_addr if request else None, 
                        request.user_agent.string if request and request.user_agent else None)
        
    except Exception as notification_error:
        print(f"Failed to handle exception notification: {notification_error}")
    
    # Return a generic error response
    return render_template('error.html', error="An unexpected error occurred. Please try again."), 500

# Helper functions for admin functionality
def log_system_event(level, category, message, user_id=None, user_type=None, ip_address=None, user_agent=None):
    """Log system events for monitoring"""
    try:
        log = SystemLog(
            level=level,
            category=category,
            message=message,
            user_id=user_id,
            user_type=user_type,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging system event: {e}")

def log_login_attempt(email, user_type, success, ip_address=None, user_agent=None, failure_reason=None):
    """Log login attempts for security monitoring"""
    try:
        attempt = LoginAttempt(
            email=email,
            user_type=user_type,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        db.session.add(attempt)
        db.session.commit()
    except Exception as e:
        print(f"Error logging login attempt: {e}")

def get_system_statistics():
    """Get comprehensive system statistics"""
    try:
        stats = {
            'total_landlords': Landlord.query.count(),
            'total_tenants': Tenant.query.count(),
            'total_employees': Employee.query.count(),
            'total_properties': Property.query.count(),
            'total_units': Unit.query.count(),
            'total_rent_logs': RentLog.query.count(),
            'total_invoices': Invoice.query.count(),
            'active_subscriptions': Subscription.query.filter_by(status='active').count(),
            'trial_users': Landlord.query.filter_by(is_trial_active=True).count(),
            'recent_logins': LoginAttempt.query.filter(
                LoginAttempt.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).count(),
            'failed_logins': LoginAttempt.query.filter(
                LoginAttempt.created_at >= datetime.utcnow() - timedelta(hours=24),
                LoginAttempt.success == False
            ).count(),
            'unresolved_errors': ErrorLog.query.filter_by(resolved=False).count(),
            'security_alerts': SecurityAlert.query.filter_by(resolved=False).count()
        }
        return stats
    except Exception as e:
        print(f"Error getting system statistics: {e}")
        return {}

def get_analytics_data():
    """Get analytics data for charts and reports"""
    try:
        # Get user growth over time
        user_growth_data = db.session.query(
            db.func.date(Landlord.created_at).label('date'),
            db.func.count(Landlord.id).label('count')
        ).group_by(db.func.date(Landlord.created_at)).order_by(db.func.date(Landlord.created_at)).all()
        
        # Calculate user growth percentage (comparing current month to previous month)
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        current_month_users = Landlord.query.filter(
            Landlord.created_at >= current_month
        ).count()
        
        last_month_users = Landlord.query.filter(
            Landlord.created_at >= last_month,
            Landlord.created_at < current_month
        ).count()
        
        user_growth_percentage = 0
        if last_month_users > 0:
            user_growth_percentage = ((current_month_users - last_month_users) / last_month_users) * 100
        elif current_month_users > 0:
            user_growth_percentage = 100  # New users this month
        
        # Get revenue data
        revenue_data = db.session.query(
            db.func.date(RentLog.date_paid).label('date'),
            db.func.sum(RentLog.amount_paid).label('amount')
        ).group_by(db.func.date(RentLog.date_paid)).order_by(db.func.date(RentLog.date_paid)).all()
        
        # Calculate monthly revenue
        monthly_revenue = db.session.query(
            db.func.sum(RentLog.amount_paid)
        ).filter(
            RentLog.date_paid >= current_month
        ).scalar() or 0
        
        # Get subscription statistics
        active_subscriptions = Subscription.query.filter_by(status='active').count()
        trial_users = Landlord.query.filter_by(is_trial_active=True).count()
        
        # Calculate conversion rate (trial to paid)
        total_landlords = Landlord.query.count()
        conversion_rate = 0
        if total_landlords > 0:
            conversion_rate = (active_subscriptions / total_landlords) * 100
        
        # Get active users (users who logged in within last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = LoginAttempt.query.filter(
            LoginAttempt.created_at >= thirty_days_ago,
            LoginAttempt.success == True
        ).distinct(LoginAttempt.email).count()
        
        # Get usage statistics
        usage_stats = {
            'sms_sent': UsageLog.query.with_entities(db.func.sum(UsageLog.sms_sent)).scalar() or 0,
            'emails_sent': UsageLog.query.with_entities(db.func.sum(UsageLog.email_sent)).scalar() or 0,
            'pdfs_generated': UsageLog.query.with_entities(db.func.sum(UsageLog.pdf_generated)).scalar() or 0,
            'api_calls': UsageLog.query.with_entities(db.func.sum(UsageLog.api_calls)).scalar() or 0
        }
        
        # Get plan distribution
        plan_distribution = db.session.query(
            Subscription.plan_type,
            db.func.count(Subscription.id)
        ).filter_by(status='active').group_by(Subscription.plan_type).all()
        
        plan_dist = {}
        for plan, count in plan_distribution:
            plan_dist[plan] = count
        
        # Get feature usage
        feature_usage = {
            'SMS Notifications': usage_stats['sms_sent'],
            'Email Invoices': usage_stats['emails_sent'],
            'PDF Generation': usage_stats['pdfs_generated'],
            'API Calls': usage_stats['api_calls']
        }
        
        # Performance metrics
        avg_response_time = 150  # Mock data - in real app, this would come from monitoring
        error_rate = ErrorLog.query.filter_by(resolved=False).count()
        uptime = 99.9  # Mock data
        
        # Convert date objects to strings for JSON serialization
        serializable_user_growth = []
        for date, count in user_growth_data:
            serializable_user_growth.append([date.isoformat() if hasattr(date, 'isoformat') else str(date), count])
        
        serializable_revenue_data = []
        for date, amount in revenue_data:
            serializable_revenue_data.append([date.isoformat() if hasattr(date, 'isoformat') else str(date), float(amount) if amount else 0])
        
        return {
            'user_growth': float(user_growth_percentage),
            'monthly_revenue': float(monthly_revenue),
            'conversion_rate': float(conversion_rate),
            'active_users': int(active_users),
            'user_growth_data': serializable_user_growth,
            'revenue_data': serializable_revenue_data,
            'usage_stats': usage_stats,
            'plan_distribution': plan_dist,
            'feature_usage': feature_usage,
            'avg_response_time': float(avg_response_time),
            'error_rate': int(error_rate),
            'uptime': float(uptime)
        }
    except Exception as e:
        print(f"Error getting analytics data: {e}")
        return {}

@main.route('/admin/subscriptions')
def admin_subscriptions():
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Get subscription data with filters
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    plan_filter = request.args.get('plan', 'all')
    
    # Build query
    query = Subscription.query.join(Landlord)
    
    if status_filter != 'all':
        query = query.filter(Subscription.status == status_filter)
    if plan_filter != 'all':
        query = query.filter(Subscription.plan_type == plan_filter)
    
    subscriptions = query.order_by(Subscription.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    # Get subscription statistics
    total_subscriptions = Subscription.query.count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    trial_users = Landlord.query.filter_by(is_trial_active=True).count()
    cancelled_subscriptions = Subscription.query.filter_by(status='cancelled').count()
    
    # Get revenue statistics
    monthly_revenue = db.session.query(db.func.sum(Subscription.amount)).filter(
        Subscription.status == 'active',
        Subscription.billing_cycle == 'monthly'
    ).scalar() or 0
    
    yearly_revenue = db.session.query(db.func.sum(Subscription.amount)).filter(
        Subscription.status == 'active',
        Subscription.billing_cycle == 'yearly'
    ).scalar() or 0
    
    # Get plan distribution
    plan_stats = db.session.query(
        Subscription.plan_type,
        db.func.count(Subscription.id)
    ).filter(Subscription.status == 'active').group_by(Subscription.plan_type).all()
    
    return render_template('admin/subscriptions.html', 
                         subscriptions=subscriptions,
                         status_filter=status_filter,
                         plan_filter=plan_filter,
                         stats={
                             'total': total_subscriptions,
                             'active': active_subscriptions,
                             'trial': trial_users,
                             'cancelled': cancelled_subscriptions,
                             'monthly_revenue': monthly_revenue,
                             'yearly_revenue': yearly_revenue,
                             'plan_distribution': plan_stats
                         })

@main.route('/admin/subscription/<int:subscription_id>')
def admin_subscription_detail(subscription_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    subscription = Subscription.query.get_or_404(subscription_id)
    landlord = Landlord.query.get(subscription.landlord_id)
    plan = PricingPlan.query.filter_by(code=subscription.plan_type).first()
    
    # Parse plan features JSON
    features = []
    if plan and plan.features:
        try:
            import json
            features = json.loads(plan.features)
        except (json.JSONDecodeError, TypeError):
            features = []
    
    # Get usage data
    usage_logs = UsageLog.query.filter_by(landlord_id=subscription.landlord_id).order_by(UsageLog.month.desc()).limit(12).all()
    
    # Get payment history
    payment_history = []  # This would be populated from a payment model if available
    
    return render_template('admin/subscription_detail.html',
                         subscription=subscription,
                         landlord=landlord,
                         plan=plan,
                         features=features,
                         usage_logs=usage_logs,
                         payment_history=payment_history)

@main.route('/admin/subscription/<int:subscription_id>/cancel', methods=['POST'])
def admin_cancel_subscription(subscription_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    subscription = Subscription.query.get_or_404(subscription_id)
    subscription.status = 'cancelled'
    subscription.end_date = datetime.utcnow()
    db.session.commit()
    
    # Log the action
    log_system_event('info', 'subscription', f'Admin cancelled subscription {subscription_id}', 
                     session['admin_id'], 'admin', request.remote_addr, request.user_agent.string)
    
    flash('Subscription cancelled successfully.', 'success')
    return redirect(url_for('main.admin_subscription_detail', subscription_id=subscription_id))

@main.route('/admin/subscription/<int:subscription_id>/reactivate', methods=['POST'])
def admin_reactivate_subscription(subscription_id):
    if 'admin_id' not in session:
        return redirect(url_for('main.admin_login'))
    
    subscription = Subscription.query.get_or_404(subscription_id)
    subscription.status = 'active'
    subscription.end_date = None
    db.session.commit()
    
    # Log the action
    log_system_event('info', 'subscription', f'Admin reactivated subscription {subscription_id}', 
                     session['admin_id'], 'admin', request.remote_addr, request.user_agent.string)
    
    flash('Subscription reactivated successfully.', 'success')
    return redirect(url_for('main.admin_subscription_detail', subscription_id=subscription_id))


