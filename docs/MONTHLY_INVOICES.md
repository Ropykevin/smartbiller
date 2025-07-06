# Monthly Invoice System

SmartBiller provides a comprehensive monthly invoice system for automated rent collection and payment tracking.

## Overview

The monthly invoice system includes:
- **Automated invoice generation** with professional PDF formatting
- **Email delivery** to tenants with email addresses
- **SMS notifications** for all tenants
- **Late payment reminders** for overdue payments
- **Usage tracking** for subscription billing

## Features

### 1. Automated Monthly Invoices
- **Schedule**: Generated on the 1st of each month at 9:00 AM
- **Format**: Professional PDF with property and tenant details
- **Content**: Monthly rent amount, payment status, due date, contact information
- **Delivery**: Email (if tenant has email) + SMS notification

### 2. Late Payment Reminders
- **Schedule**: Daily at 10:00 AM (active after the 5th of each month)
- **Trigger**: Automatically detects unpaid or partially paid rent
- **Message**: Urgent reminder with penalty warnings
- **Delivery**: SMS only (to avoid spam)

### 3. Manual Triggers
Landlords can manually trigger invoice sending and reminders from the dashboard:
- **Send Invoices**: Generate and send monthly invoices immediately
- **Late Reminders**: Send overdue payment alerts
- **Send Reminders**: General payment reminders

## Setup Instructions

### 1. Email Configuration
Set up SMTP credentials in your environment:

```bash
export EMAIL_PASSWORD="your_smtp_password"
```

### 2. Automated Tasks Setup
Run the cron job setup script:

```bash
chmod +x setup_cron_jobs.sh
./setup_cron_jobs.sh
```

### 3. Manual Testing
Test the system manually:

```bash
# Send monthly invoices
python3 run_scheduled_tasks.py monthly_invoices

# Send late payment reminders
python3 run_scheduled_tasks.py late_reminders

# Run both tasks
python3 run_scheduled_tasks.py all
```

## Subscription Plan Limits

### Basic Plan
- ❌ Email invoices (not available)
- ✅ SMS reminders (50/month)
- ❌ PDF generation (not available)

### Professional Plan
- ✅ Email invoices (unlimited)
- ✅ SMS reminders (200/month)
- ✅ PDF generation (unlimited)

### Enterprise Plan
- ✅ Email invoices (unlimited)
- ✅ SMS reminders (unlimited)
- ✅ PDF generation (unlimited)

## Invoice Content

### PDF Invoice Includes:
1. **Header**: SmartBiller branding and property information
2. **Tenant Details**: Name, phone, unit number, monthly rent
3. **Invoice Details**: 
   - Month and year
   - Monthly rent amount
   - Amount paid (if any)
   - Balance due
   - Payment status
4. **Payment Instructions**: Due date, payment methods, contact info
5. **Footer**: Generation date and SmartBiller branding

### SMS Message Format:
```
Dear [Tenant Name], your rent invoice for [Month Year] has been generated. 
Amount: KES [Amount]. Please pay by the 5th to avoid late fees.
```

## File Structure

```
smartbiller/
├── app/
│   ├── scheduled_tasks.py      # Automated task functions
│   ├── sms_service.py          # SMS sending service
│   └── subscription_service.py # Plan limits and permissions
├── run_scheduled_tasks.py      # CLI script for manual execution
├── setup_cron_jobs.sh          # Cron job setup script
└── logs/                       # Task execution logs
    ├── monthly_invoices.log
    └── late_reminders.log
```

## Database Schema

### UsageLog Model
Tracks usage for subscription billing:
```python
class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    landlord_id = db.Column(db.Integer, db.ForeignKey('landlord.id'))
    month = db.Column(db.String(7))  # YYYY-MM format
    sms_sent = db.Column(db.Integer, default=0)
    email_sent = db.Column(db.Integer, default=0)  # New field
    pdf_generated = db.Column(db.Integer, default=0)
    # ... other fields
```

### Tenant Model
Includes email field for invoice delivery:
```python
class Tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))  # Optional for invoice delivery
    # ... other fields
```

## Monitoring and Logs

### Log Files
- `logs/monthly_invoices.log`: Monthly invoice generation logs
- `logs/late_reminders.log`: Late payment reminder logs

### Dashboard Integration
- Quick action buttons for manual triggering
- Usage statistics display
- Success/error message feedback

## Troubleshooting

### Common Issues

1. **Email Not Sending**
   - Check SMTP credentials
   - Verify tenant email addresses
   - Check subscription plan limits

2. **SMS Not Sending**
   - Verify Africa's Talking API credentials
   - Check SMS usage limits
   - Ensure tenant phone numbers are valid

3. **PDF Generation Fails**
   - Check disk space
   - Verify ReportLab installation
   - Check subscription plan permissions

### Manual Override
If automated tasks fail, landlords can:
1. Use dashboard buttons for immediate sending
2. Run CLI commands manually
3. Check logs for error details

## Security Considerations

1. **Email Security**: SMTP credentials stored as environment variables
2. **SMS Security**: API keys stored securely
3. **Data Privacy**: Tenant information protected
4. **Access Control**: Subscription-based feature access

## Future Enhancements

1. **Custom Invoice Templates**: Landlord-branded invoices
2. **Payment Integration**: Direct payment links in invoices
3. **Multi-language Support**: Localized invoice content
4. **Advanced Scheduling**: Custom reminder schedules
5. **Analytics Dashboard**: Invoice delivery statistics 