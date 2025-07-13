# Gmail SMTP Email Setup Guide

## 🔧 **Fix for "Username and Password not accepted" Error**

### **Step 1: Enable 2-Factor Authentication**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security**
3. Enable **2-Step Verification** if not already enabled

### **Step 2: Generate App Password**
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification**
3. Scroll down to **"App passwords"**
4. Click **"Generate"** or **"Create app password"**
5. Select **"Mail"** as the app type
6. Enter **"SmartBiller"** as the device name
7. Click **"Generate"**
8. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### **Step 3: Update Your .env File**
Create or update your `.env` file with the following email settings:

```env
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` with your actual Gmail address
- `your-16-character-app-password` with the app password you generated

### **Step 4: Test Email Configuration**
Run this command to test your email setup:

```bash
python -c "
from app import create_app
from flask_mail import Message
app = create_app()
app.app_context().push()
from app import mail

try:
    msg = Message(
        subject='SmartBiller Email Test',
        recipients=['test@example.com'],
        body='This is a test email from SmartBiller.'
    )
    mail.send(msg)
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Email error: {e}')
"
```

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Username and Password not accepted"**
**Solution:** Use App Password instead of regular password

### **Issue 2: "Less secure app access"**
**Solution:** Use App Password (more secure than enabling less secure apps)

### **Issue 3: "Authentication failed"**
**Solution:** 
1. Make sure 2-Factor Authentication is enabled
2. Generate a fresh App Password
3. Remove spaces from the App Password

### **Issue 4: "Connection timeout"**
**Solution:**
1. Check your internet connection
2. Try different port: `MAIL_PORT=465` and `MAIL_USE_SSL=True`
3. Check firewall settings

## 🔒 **Security Best Practices**

1. **Never use your regular Gmail password**
2. **Use App Passwords for each application**
3. **Keep your .env file secure and never commit it to version control**
4. **Regularly rotate App Passwords**

## 📧 **Alternative Email Providers**

If Gmail continues to cause issues, you can use other providers:

### **Outlook/Hotmail:**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### **Yahoo:**
```env
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-app-password
```

## ✅ **Verification Checklist**

- [ ] 2-Factor Authentication enabled
- [ ] App Password generated
- [ ] .env file updated with correct credentials
- [ ] Email test successful
- [ ] No spaces in App Password
- [ ] Correct port and TLS settings

## 🆘 **Still Having Issues?**

1. **Check Gmail Account Activity** for blocked login attempts
2. **Try a different Gmail account** for testing
3. **Use a different email provider** temporarily
4. **Check server logs** for detailed error messages

---

**Note:** This setup is required for features like:
- Employee welcome emails
- Invoice delivery
- Password reset emails
- System notifications 