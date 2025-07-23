-- SmartBiller Pricing Plans Manual Setup
-- Run this SQL script to manually add pricing plans to your database

-- Connect to your database first:
-- psql -U smartbiller -d smartbiller
-- Or via Docker: docker-compose exec db psql -U smartbiller -d smartbiller

-- Clear any existing pricing plans (optional)
-- DELETE FROM pricing_plan;

-- Insert Basic Plan
INSERT INTO pricing_plan (
    name, 
    code, 
    monthly_price, 
    yearly_price, 
    max_properties, 
    max_sms_per_month, 
    features, 
    is_active, 
    created_at
) VALUES (
    'Basic',
    'basic',
    500.0,
    5000.0,
    3,
    50,
    '["Up to 3 properties", "Up to 100 units per property", "Rent tracking & reminders", "SMS notifications (50/month)", "Basic reports & analytics", "Email support", "Mobile-responsive dashboard"]',
    true,
    NOW()
);

-- Insert Professional Plan
INSERT INTO pricing_plan (
    name, 
    code, 
    monthly_price, 
    yearly_price, 
    max_properties, 
    max_sms_per_month, 
    features, 
    is_active, 
    created_at
) VALUES (
    'Professional',
    'professional',
    1200.0,
    12000.0,
    20,
    200,
    '["Up to 20 properties", "Up to 200 units per property", "Advanced rent tracking", "Bulk SMS notifications (200/month)", "Detailed analytics & reports", "PDF receipts & invoices", "Priority email & phone support", "Exit notice management", "API access"]',
    true,
    NOW()
);

-- Insert Enterprise Plan
INSERT INTO pricing_plan (
    name, 
    code, 
    monthly_price, 
    yearly_price, 
    max_properties, 
    max_sms_per_month, 
    features, 
    is_active, 
    created_at
) VALUES (
    'Enterprise',
    'enterprise',
    0.0,
    0.0,
    999999,
    999999,
    '["Unlimited properties", "Unlimited units per property", "Custom integrations", "White-label solution", "Advanced reporting & analytics", "Dedicated account manager", "Custom development", "24/7 phone support"]',
    true,
    NOW()
);

-- Optional: Insert a trial plan for display purposes
INSERT INTO pricing_plan (
    name, 
    code, 
    monthly_price, 
    yearly_price, 
    max_properties, 
    max_sms_per_month, 
    features, 
    is_active, 
    created_at
) VALUES (
    'Free Trial',
    'trial',
    0.0,
    0.0,
    999,
    50,
    '["Unlimited Properties", "50 SMS/month", "Basic Support"]',
    true,
    NOW()
);

-- Verify the data was inserted
SELECT id, name, code, monthly_price, yearly_price, max_properties, max_sms_per_month, is_active 
FROM pricing_plan 
ORDER BY monthly_price;

-- Check if max_units_per_property column exists and add it if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'pricing_plan' 
        AND column_name = 'max_units_per_property'
    ) THEN
        ALTER TABLE pricing_plan ADD COLUMN max_units_per_property INTEGER DEFAULT 100;
        
        -- Update existing plans with appropriate limits
        UPDATE pricing_plan SET max_units_per_property = 100 WHERE code = 'basic';
        UPDATE pricing_plan SET max_units_per_property = 200 WHERE code = 'professional';
        UPDATE pricing_plan SET max_units_per_property = 999999 WHERE code = 'enterprise';
        UPDATE pricing_plan SET max_units_per_property = 999 WHERE code = 'trial';
        
        RAISE NOTICE 'Added max_units_per_property column and updated existing plans';
    ELSE
        RAISE NOTICE 'max_units_per_property column already exists';
    END IF;
END
$$;

-- Final verification
SELECT 
    name,
    code,
    monthly_price,
    max_properties,
    max_units_per_property,
    max_sms_per_month,
    is_active
FROM pricing_plan 
ORDER BY monthly_price; 