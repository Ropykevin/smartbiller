# Brevo Email Setup Guide for SmartBiller

## 🚀 **Why Brevo?**

Brevo (formerly Sendinblue) is a powerful email service provider that offers:
- **High deliverability** - Better than Gmail for business emails
- **Professional sending** - No daily limits like Gmail
- **Email templates** - Beautiful HTML emails
- **Analytics** - Track email opens and clicks
- **SMTP API** - Easy integration with Flask
- **Free tier** - 300 emails/day free

## 📋 **Setup Steps**

### **Step 1: Create Brevo Account**
1. Go to [Brevo.com](https://www.brevo.com/)
2. Click **"Start for free"**
3. Sign up with your email
4. Verify your email address

### **Step 2: Get SMTP Credentials**
1. Login to your Brevo dashboard
2. Go to **Settings** → **SMTP & API**
3. Click **"SMTP"** tab
4. Note down your credentials:
   - **SMTP Server:** `smtp-relay.brevo.com`
   - **Port:** `587`
   - **Username:** Your Brevo username (usually your email)
   - **SMTP Key:** Click "Generate" to create a new SMTP key

### **Step 3: Update Your .env File**
Replace your current email settings with:

```env
# Email Configuration (Brevo/Sendinblue)
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-brevo-username
MAIL_PASSWORD=your-brevo-smtp-key
MAIL_DEFAULT_SENDER=noreply@smartbiller.co.ke
```

**Replace:**
- `your-brevo-username` with your Brevo username
- `your-brevo-smtp-key` with your SMTP key from Brevo

### **Step 4: Test Email Configuration**
Run this command to test your Brevo setup:

```bash
python -c "
from app import create_app
from flask_mail import Message
app = create_app()
app.app_context().push()
from app import mail

try:
    msg = Message(
        subject='SmartBiller Brevo Test',
        recipients=['test@example.com'],
        body='This is a test email from SmartBiller using Brevo.'
    )
    mail.send(msg)
    print('✅ Brevo email sent successfully!')
except Exception as e:
    print(f'❌ Brevo email error: {e}')
"
```

## 🔧 **Brevo Dashboard Features**

### **Email Templates**
1. Go to **Templates** in Brevo dashboard
2. Create templates for:
   - Employee welcome emails
   - Reactivation emails
   - Password reset emails
   - Invoice notifications

### **Sender Verification**
1. Go to **Settings** → **Senders & IP**
2. Add your domain: `smartbiller.co.ke`
3. Verify domain ownership
4. Set up SPF and DKIM records

### **Email Analytics**
- Track email opens and clicks
- Monitor delivery rates
- View bounce reports
- Analyze engagement

## 📧 **Email Types in SmartBiller**

### **1. Employee Welcome Email**
- **Trigger:** When adding new employee
- **Content:** Login credentials, position, access instructions
- **Template:** `send_employee_welcome_email()`

### **2. Employee Reactivation Email**
- **Trigger:** When reactivating employee
- **Content:** Account restored, login instructions
- **Template:** `send_employee_reactivation_email()`

### **3. Invoice Delivery**
- **Trigger:** When generating invoices
- **Content:** PDF invoice attachment
- **Template:** Invoice delivery system

### **4. Password Reset**
- **Trigger:** When employee requests password reset
- **Content:** New temporary password
- **Template:** Password reset system

## 🎨 **Email Template Design**

### **HTML Structure**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SmartBiller Email</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .content { background: #f9f9f9; padding: 30px; }
        .button { background: #4CAF50; color: white; padding: 15px 30px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Email content here -->
    </div>
</body>
</html>
```

### **Best Practices**
- ✅ Use responsive design
- ✅ Include clear call-to-action buttons
- ✅ Add your logo and branding
- ✅ Keep subject lines under 50 characters
- ✅ Test emails across different clients

## 🔒 **Security & Compliance**

### **GDPR Compliance**
- Include unsubscribe links
- Clear privacy policy
- Opt-in consent management
- Data retention policies

### **Email Authentication**
- Set up SPF records
- Configure DKIM signing
- Enable DMARC policy
- Monitor reputation

## 📊 **Monitoring & Analytics**

### **Brevo Dashboard**
- **Delivery Rate:** Track successful sends
- **Open Rate:** Monitor email engagement
- **Click Rate:** Measure link interactions
- **Bounce Rate:** Identify invalid emails

### **SmartBiller Integration**
```python
# Track email sends in your app
def send_email_with_tracking(subject, recipients, html_content):
    try:
        msg = Message(subject, recipients, html=html_content)
        mail.send(msg)
        
        # Log successful send
        log_email_send(subject, recipients, 'success')
        return True
    except Exception as e:
        # Log failed send
        log_email_send(subject, recipients, 'failed', str(e))
        return False
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Authentication Failed**
```
Error: (535, b'5.7.8 Username and Password not accepted')
```
**Solution:** Check your Brevo SMTP credentials

#### **2. Connection Timeout**
```
Error: Connection timeout
```
**Solution:** Verify SMTP server and port settings

#### **3. Email Not Delivered**
```
Error: Email sent but not received
```
**Solution:** Check spam folder, verify sender domain

### **Debug Commands**
```bash
# Test SMTP connection
python -c "
import smtplib
s = smtplib.SMTP('smtp-relay.brevo.com', 587)
s.starttls()
s.login('your-username', 'your-smtp-key')
print('✅ SMTP connection successful')
s.quit()
"
```

## 📈 **Performance Optimization**

### **Email Sending Limits**
- **Free Plan:** 300 emails/day
- **Starter Plan:** 20,000 emails/month
- **Business Plan:** 100,000 emails/month

### **Best Practices**
- ✅ Send emails in batches
- ✅ Use email templates
- ✅ Monitor bounce rates
- ✅ Clean email lists regularly
- ✅ Warm up new domains gradually

## 🎯 **Next Steps**

1. **Set up Brevo account** and get SMTP credentials
2. **Update your .env file** with Brevo settings
3. **Test email functionality** with the test command
4. **Verify your domain** in Brevo dashboard
5. **Monitor email analytics** and delivery rates
6. **Create email templates** for different scenarios

---

**Brevo Integration Complete!** 🎉

Your SmartBiller application will now use Brevo for all email communications, providing better deliverability and professional email management. 