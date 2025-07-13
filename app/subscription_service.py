import json
from datetime import datetime, timedelta
from .models import db, Landlord, Subscription, PricingPlan, UsageLog
from . import db

class SubscriptionService:
    """Service class to handle subscription and pricing logic"""
    
    @staticmethod
    def get_pricing_plans():
        """Get all active pricing plans"""
        return PricingPlan.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_plan_by_code(plan_code):
        """Get a specific pricing plan by code"""
        return PricingPlan.query.filter_by(code=plan_code, is_active=True).first()
    
    @staticmethod
    def get_landlord_subscription(landlord_id):
        """Get landlord's current subscription"""
        return Subscription.query.filter_by(landlord_id=landlord_id, status='active').first()
    
    @staticmethod
    def get_landlord_plan(landlord_id):
        """Get landlord's current plan details"""
        subscription = SubscriptionService.get_landlord_subscription(landlord_id)
        if subscription:
            return PricingPlan.query.filter_by(code=subscription.plan_type).first()
        return None
    
    @staticmethod
    def is_trial_active(landlord_id):
        """Check if landlord's trial is still active"""
        landlord = Landlord.query.get(landlord_id)
        if not landlord:
            return False
        return landlord.is_trial_active and datetime.utcnow() < landlord.trial_ends_at
    
    @staticmethod
    def has_active_subscription(landlord_id):
        """Check if landlord has an active subscription or trial"""
        if SubscriptionService.is_trial_active(landlord_id):
            return True
        
        subscription = SubscriptionService.get_landlord_subscription(landlord_id)
        return subscription is not None and subscription.status == 'active'
    
    @staticmethod
    def can_add_property(landlord_id):
        """Check if landlord can add more properties based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            return True  # Trial users can add unlimited properties
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        from app.models import Property
        current_properties = Property.query.filter_by(landlord_id=landlord_id).count()
        return current_properties < plan.max_properties
    
    @staticmethod
    def can_add_unit_to_property(landlord_id, property_id):
        """Check if landlord can add more units to a specific property based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            return True  # Trial users can add unlimited units
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        # Get current unit count for this property
        from .models import Property
        property = Property.query.get(property_id)
        if not property or property.landlord_id != landlord_id:
            return False
        
        current_units = property.units.count()
        
        # Basic plan: 100 units per property
        if plan.code == 'basic':
            return current_units < 100
        # Professional plan: 200 units per property  
        elif plan.code == 'professional':
            return current_units < 200
        # Enterprise plan: unlimited units
        else:
            return True
    
    @staticmethod
    def can_send_sms(landlord_id):
        """Check if landlord can send SMS based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            # Trial users get 50 SMS per month
            current_month = datetime.utcnow().strftime('%Y-%m')
            usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
            
            if not usage:
                return True  # No usage recorded yet
            
            return usage.sms_sent < 50  # Trial limit
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
        
        if not usage:
            return True  # No usage recorded yet
        
        return usage.sms_sent < plan.max_sms_per_month
    
    @staticmethod
    def can_generate_pdf(landlord_id):
        """Check if landlord can generate PDFs based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            return False  # Trial users can't generate PDFs
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        # Professional and Enterprise plans can generate PDFs
        return plan.code in ['professional', 'enterprise']
    
    @staticmethod
    def can_send_email(landlord_id):
        """Check if landlord can send emails based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            return False  # Trial users can't send emails
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        # Professional and Enterprise plans can send emails
        return plan.code in ['professional', 'enterprise']
    
    @staticmethod
    def can_use_api(landlord_id):
        """Check if landlord can use API based on their plan"""
        if SubscriptionService.is_trial_active(landlord_id):
            return False  # Trial users can't use API
        
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        if not plan:
            return False
        
        # Professional and Enterprise plans can use API
        return plan.code in ['professional', 'enterprise']
    
    @staticmethod
    def log_sms_usage(landlord_id):
        """Log SMS usage for the current month"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
        
        if usage:
            usage.sms_sent += 1
        else:
            usage = UsageLog(
                landlord_id=landlord_id,
                month=current_month,
                sms_sent=1
            )
            db.session.add(usage)
        
        db.session.commit()
    
    @staticmethod
    def log_pdf_usage(landlord_id):
        """Log PDF generation usage for the current month"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
        
        if usage:
            usage.pdf_generated += 1
        else:
            usage = UsageLog(
                landlord_id=landlord_id,
                month=current_month,
                pdf_generated=1
            )
            db.session.add(usage)
        
        db.session.commit()
    
    @staticmethod
    def log_api_usage(landlord_id):
        """Log API usage for the current month"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
        
        if usage:
            usage.api_calls += 1
        else:
            usage = UsageLog(
                landlord_id=landlord_id,
                month=current_month,
                api_calls=1
            )
            db.session.add(usage)
        
        db.session.commit()
    
    @staticmethod
    def create_subscription(landlord_id, plan_code, billing_cycle='monthly', payment_method=None, payment_reference=None):
        """Create a new subscription for a landlord"""
        plan = SubscriptionService.get_plan_by_code(plan_code)
        if not plan:
            raise ValueError(f"Invalid plan code: {plan_code}")
        
        # Cancel any existing active subscription
        existing_subscription = SubscriptionService.get_landlord_subscription(landlord_id)
        if existing_subscription:
            existing_subscription.status = 'cancelled'
            existing_subscription.end_date = datetime.utcnow()
        
        # Set amount based on billing cycle
        amount = plan.yearly_price if billing_cycle == 'yearly' else plan.monthly_price
        
        # Calculate end date
        if billing_cycle == 'yearly':
            end_date = datetime.utcnow() + timedelta(days=365)
        else:
            end_date = datetime.utcnow() + timedelta(days=30)
        
        # Create new subscription
        subscription = Subscription(
            landlord_id=landlord_id,
            plan_type=plan_code,
            status='active',
            start_date=datetime.utcnow(),
            end_date=end_date,
            billing_cycle=billing_cycle,
            amount=amount,
            payment_method=payment_method,
            payment_reference=payment_reference
        )
        
        # End trial if landlord was on trial
        landlord = Landlord.query.get(landlord_id)
        if landlord and landlord.is_trial_active:
            landlord.is_trial_active = False
        
        db.session.add(subscription)
        db.session.commit()
        
        return subscription
    
    @staticmethod
    def get_usage_summary(landlord_id):
        """Get usage summary for the current month"""
        from app.models import Property, Unit
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = UsageLog.query.filter_by(landlord_id=landlord_id, month=current_month).first()
        plan = SubscriptionService.get_landlord_plan(landlord_id)
        is_trial = SubscriptionService.is_trial_active(landlord_id)
        
        if not usage:
            properties_count = Property.query.filter_by(landlord_id=landlord_id).count()
            units_count = Unit.query.join(Property).filter(Property.landlord_id == landlord_id).count()
            usage = UsageLog(
                landlord_id=landlord_id,
                month=current_month,
                properties_count=properties_count,
                units_count=units_count
            )
        
        # Set limits based on trial or plan
        if is_trial:
            max_properties = float('inf')  # Unlimited during trial
            max_sms = 50  # 50 SMS per month during trial
            plan_name = 'Free Trial'
        else:
            max_properties = plan.max_properties if plan else 3
            max_sms = plan.max_sms_per_month if plan else 50
            plan_name = plan.name if plan else 'Basic'
        
        return {
            'properties_count': usage.properties_count or 0,
            'units_count': usage.units_count or 0,
            'sms_sent': usage.sms_sent or 0,
            'pdf_generated': usage.pdf_generated or 0,
            'api_calls': usage.api_calls or 0,
            'plan': plan_name,
            'max_properties': max_properties,
            'max_sms': max_sms,
            'can_generate_pdf': SubscriptionService.can_generate_pdf(landlord_id),
            'can_use_api': SubscriptionService.can_use_api(landlord_id),
            'is_trial': is_trial
        }
    
    @staticmethod
    def initialize_pricing_plans():
        """Initialize default pricing plans in the database"""
        plans_data = [
            {
                'name': 'Basic',
                'code': 'basic',
                'monthly_price': 500.0,
                'yearly_price': 5000.0,
                'max_properties': 3,  # Updated to 3 properties
                'max_sms_per_month': 50,
                'features': json.dumps([
                    'Up to 3 properties',
                    'Up to 100 units per property',
                    'Rent tracking & reminders',
                    'SMS notifications (50/month)',
                    'Basic reports & analytics',
                    'Email support',
                    'Mobile-responsive dashboard'
                ])
            },
            {
                'name': 'Professional',
                'code': 'professional',
                'monthly_price': 1200.0,
                'yearly_price': 12000.0,
                'max_properties': 20,
                'max_sms_per_month': 200,
                'features': json.dumps([
                    'Up to 20 properties',
                    'Up to 200 units per property',
                    'Advanced rent tracking',
                    'Bulk SMS notifications (200/month)',
                    'Detailed analytics & reports',
                    'PDF receipts & invoices',
                    'Priority email & phone support',
                    'Exit notice management',
                    'API access'
                ])
            },
            {
                'name': 'Enterprise',
                'code': 'enterprise',
                'monthly_price': 0.0,  # Custom pricing
                'yearly_price': 0.0,   # Custom pricing
                'max_properties': 999999,  # Unlimited
                'max_sms_per_month': 999999,  # Unlimited
                'features': json.dumps([
                    'Unlimited properties',
                    'Unlimited units per property',
                    'Custom integrations',
                    'White-label solution',
                    'Advanced reporting & analytics',
                    'Dedicated account manager',
                    'Custom development',
                    '24/7 phone support'
                ])
            }
        ]
        
        for plan_data in plans_data:
            existing_plan = PricingPlan.query.filter_by(code=plan_data['code']).first()
            if not existing_plan:
                plan = PricingPlan(**plan_data)
                db.session.add(plan)
            else:
                # Update existing plan with new limits
                existing_plan.max_properties = plan_data['max_properties']
                existing_plan.features = plan_data['features']
        
        db.session.commit() 