from . import db
from datetime import datetime, timedelta
import random
import string

class Landlord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))  # Optional phone field for contact info
    password = db.Column(db.String(255), nullable=False)
    avatar_path = db.Column(db.String(255))  # New field for profile image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    properties = db.relationship('Property', backref='landlord', lazy=True)
    
    # Subscription fields - temporarily commented out until migration is complete
    subscription = db.relationship('Subscription', backref='landlord', uselist=False, lazy=True)
    trial_ends_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    is_trial_active = db.Column(db.Boolean, default=True)
    
    # Theme preference
    theme_preference = db.Column(db.String(10), default='light')  # 'light' or 'dark'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    plan_type = db.Column(db.String(20), nullable=False)  # 'basic', 'professional', 'enterprise'
    status = db.Column(db.String(20), default='active')  # 'active', 'cancelled', 'expired', 'trial'
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    billing_cycle = db.Column(db.String(10), default='monthly')  # 'monthly', 'yearly'
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # 'mpesa', 'bank_transfer', 'card'
    payment_reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PricingPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # 'Basic', 'Professional', 'Enterprise'
    code = db.Column(db.String(20), unique=True, nullable=False)  # 'basic', 'professional', 'enterprise'
    monthly_price = db.Column(db.Float, nullable=False)
    yearly_price = db.Column(db.Float, nullable=False)
    max_properties = db.Column(db.Integer, nullable=False)
    max_units_per_property = db.Column(db.Integer, nullable=False, default=100)  # Added this field
    max_sms_per_month = db.Column(db.Integer, nullable=False)
    features = db.Column(db.Text)  # JSON string of features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    properties_count = db.Column(db.Integer, default=0)
    units_count = db.Column(db.Integer, default=0)
    sms_sent = db.Column(db.Integer, default=0)
    email_sent = db.Column(db.Integer, default=0)  # Track email usage
    pdf_generated = db.Column(db.Integer, default=0)
    api_calls = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    landlord = db.relationship('Landlord', backref='usage_logs')

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    payment_method = db.Column(db.String(50))
    payment_destination = db.Column(db.String(100))
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    units = db.relationship('Unit', backref='property', lazy=True)
    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade='all, delete-orphan')

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(50), nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    
    # Enhanced unit details
    size = db.Column(db.Float)  # Size in square feet
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    floor_number = db.Column(db.Integer)
    unit_type = db.Column(db.String(50))  # Studio, 1BR, 2BR, etc.
    amenities = db.Column(db.Text)  # JSON string of amenities
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Available')  # Available, Occupied, Maintenance
    
    # Additional features
    parking_spaces = db.Column(db.Integer, default=0)
    balcony = db.Column(db.Boolean, default=False)
    furnished = db.Column(db.Boolean, default=False)
    air_conditioning = db.Column(db.Boolean, default=False)
    heating = db.Column(db.Boolean, default=False)
    internet_included = db.Column(db.Boolean, default=False)
    utilities_included = db.Column(db.Boolean, default=False)
    
    # Financial details
    deposit_amount = db.Column(db.Float)
    late_fee = db.Column(db.Float)
    grace_period_days = db.Column(db.Integer, default=5)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = db.relationship('Tenant', backref='unit', uselist=False, lazy=True)
    images = db.relationship('UnitImage', backref='unit', lazy=True, cascade='all, delete-orphan')

class UnitImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(100))
    image_type = db.Column(db.String(50))  # 'interior', 'exterior', 'maintenance', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('unit.id'), nullable=False)
    
    # Additional tenant information
    email = db.Column(db.String(120), unique=True, nullable=False)  # Now required and unique for login
    id_number = db.Column(db.String(20))
    emergency_contact = db.Column(db.String(200))
    occupation = db.Column(db.String(100))
    employer = db.Column(db.String(100))
    move_in_date = db.Column(db.DateTime)
    
    avatar_path = db.Column(db.String(255))  # New field for profile image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    rent_logs = db.relationship('RentLog', backref='tenant', lazy=True)
    login_code = db.Column(db.String(6))
    login_code_expiry = db.Column(db.DateTime)

class RentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    date_paid = db.Column(db.DateTime, nullable=False)
    month_paid_for = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Unpaid')
    receipt_number = db.Column(db.String(50))
    logged_by_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # Track who logged the payment
    notes = db.Column(db.Text)  # Additional notes about the payment (failed attempts, reasons, etc.)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('RentLogImage', backref='rent_log', lazy=True, cascade='all, delete-orphan')

class RentLogImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rent_log_id = db.Column(db.Integer, db.ForeignKey('rent_log.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_receipt_number():
    """Generate a unique receipt number"""
    prefix = "RCP"
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

def generate_invoice_number():
    """Generate a unique invoice number"""
    prefix = "INV"
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}{timestamp}{random_suffix}"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, default=generate_invoice_number)
    month = db.Column(db.String(20), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    base_rent = db.Column(db.Float, nullable=False)
    additional_charges = db.Column(db.Text)  # JSON string of additional charges
    total_amount = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    pdf_path = db.Column(db.String(255))  # Path to saved PDF file
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='invoices')
    landlord = db.relationship('Landlord', backref='invoices')

class ExitNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenant.id'), nullable=False)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    notice_date = db.Column(db.DateTime, default=datetime.utcnow)
    intended_exit_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    additional_comments = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Completed
    landlord_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = db.relationship('Tenant', backref='exit_notices')
    landlord = db.relationship('Landlord', backref='exit_notices')

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    position = db.Column(db.String(100))  # e.g., "Property Manager", "Accountant", "Assistant"
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    landlord = db.relationship('Landlord', backref='employees')
    rent_logs = db.relationship('RentLog', backref='logged_by_employee', lazy=True) 