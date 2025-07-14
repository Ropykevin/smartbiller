# SmartBiller Error Notification System

## 🚨 Overview

The SmartBiller Error Notification System automatically detects and reports critical errors to **ropykevin@gmail.com** via email. This ensures you're immediately notified of any system issues that require attention.

## ✨ Features

### **Automatic Error Detection**
- **Global Exception Handler**: Catches all unhandled exceptions
- **Critical Error Types**: Database errors, connection issues, security violations
- **Severity Levels**: Low, Medium, High, Critical
- **Smart Filtering**: Only sends notifications for important errors

### **Email Notifications**
- **Immediate Alerts**: Critical errors trigger instant email notifications
- **Detailed Reports**: Includes error type, message, stack trace, user info
- **HTML Formatting**: Professional, easy-to-read email templates
- **Request Context**: URL, method, IP address, user agent

### **Daily Summaries**
- **Daily Reports**: Summary of all errors from the past 24 hours
- **Error Breakdown**: Grouped by error type with counts
- **Quick Actions**: Direct links to admin panel for investigation

## 📧 Email Notifications

### **Critical Error Alerts**
When a critical error occurs, you'll receive an email with:

- **Error Type**: DatabaseError, ConnectionError, SecurityViolation, etc.
- **Severity Level**: Color-coded badges (Green, Yellow, Red, Dark Red)
- **Timestamp**: Exact time the error occurred
- **Error Message**: Detailed error description
- **User Information**: User ID, type, IP address
- **Request Details**: URL, method, user agent
- **Stack Trace**: First 20 lines (truncated for email)
- **Recommended Actions**: Steps to investigate and resolve

### **Daily Error Summaries**
Sent daily with:

- **Total Error Count**: Number of errors in the last 24 hours
- **Error Breakdown**: Grouped by error type
- **Top Errors**: Most frequent error types
- **Quick Links**: Direct access to admin panel sections

## 🔧 Configuration

### **Critical Error Types**
The system automatically notifies for these error types:
```python
CRITICAL_ERROR_TYPES = [
    'DatabaseError',
    'ConnectionError', 
    'AuthenticationError',
    'SecurityViolation',
    'PaymentError',
    'SystemError',
    'CriticalError'
]
```

### **Severity Levels**
- **Low**: Minor issues (no notification)
- **Medium**: Moderate issues (notification for critical types)
- **High**: Serious issues (always notified)
- **Critical**: System-threatening issues (always notified)

## 🧪 Testing

### **Test Error Notification**
```bash
# Visit this URL to test error notifications
http://localhost:5000/test_error_notification
```

### **Test Daily Summary**
```bash
# Visit this URL to test daily summaries
http://localhost:5000/test_daily_summary
```

### **Manual Daily Summary**
```bash
# Run daily error summary manually
python run_scheduled_tasks.py error_summary
```

## 📋 Setup Instructions

### **1. Email Configuration**
Ensure your email settings are configured in `.env`:
```env
MAIL_SERVER=smtp-relay.brevo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-brevo-username
MAIL_PASSWORD=your-brevo-smtp-key
MAIL_DEFAULT_SENDER=noreply@smartbiller.co.ke
```

### **2. Database Tables**
The system uses existing tables:
- `error_log`: Stores all errors
- `system_log`: Tracks notification events

### **3. Scheduled Tasks**
Add to your cron jobs for daily summaries:
```bash
# Daily error summary at 9:00 AM
0 9 * * * cd /path/to/smartbiller && python run_scheduled_tasks.py error_summary
```

## 📊 Admin Panel Integration

### **Error Management**
- **View All Errors**: `/admin/errors`
- **Error Details**: Click on any error for full details
- **Mark as Resolved**: Resolve errors from the admin panel
- **Filter by Status**: View resolved/unresolved errors

### **System Logs**
- **View System Logs**: `/admin/logs`
- **Filter by Level**: Error, Warning, Info, Critical
- **Filter by Category**: Auth, Payment, SMS, Email, System
- **Search and Pagination**: Easy navigation through logs

## 🚀 Usage Examples

### **Automatic Notifications**
The system automatically sends notifications when:

1. **Database Connection Fails**
   - Error Type: `ConnectionError`
   - Severity: Critical
   - Immediate notification sent

2. **Authentication Violation**
   - Error Type: `SecurityViolation`
   - Severity: Critical
   - Includes IP address and user agent

3. **Payment Processing Error**
   - Error Type: `PaymentError`
   - Severity: High
   - Includes transaction details

### **Manual Error Logging**
You can manually log errors in your code:
```python
from app.error_notification import ErrorNotificationService

try:
    # Your code here
    pass
except Exception as e:
    ErrorNotificationService.log_and_notify_error(
        error_type='CustomError',
        error_message=str(e),
        stack_trace=traceback.format_exc(),
        user_id=current_user.id,
        user_type='landlord',
        severity='high'
    )
```

## 📈 Monitoring Dashboard

### **Error Analytics**
- **Error Trends**: Track error frequency over time
- **Most Common Errors**: Identify recurring issues
- **Resolution Time**: Monitor how quickly errors are resolved
- **User Impact**: See which users are affected by errors

### **System Health**
- **Uptime Monitoring**: Track system availability
- **Performance Metrics**: Monitor response times
- **Error Rate**: Calculate error percentage
- **Alert Thresholds**: Set custom notification rules

## 🔒 Security Features

### **Privacy Protection**
- **IP Address Logging**: Track potential security threats
- **User Agent Tracking**: Identify suspicious activity
- **Request Context**: Full request details for investigation
- **Secure Logging**: No sensitive data in error messages

### **Rate Limiting**
- **Notification Limits**: Prevent email spam
- **Error Throttling**: Limit notifications for repeated errors
- **Daily Limits**: Maximum notifications per day
- **Smart Filtering**: Only important errors trigger notifications

## 📞 Support

### **Contact Information**
- **Email**: ropykevin@gmail.com (receives all notifications)
- **Support**: support@smartbiller.co.ke
- **Admin Panel**: https://smartbiller.co.ke/admin

### **Troubleshooting**
1. **No Email Notifications**: Check email configuration
2. **Too Many Notifications**: Adjust severity thresholds
3. **Missing Error Details**: Check database connectivity
4. **Daily Summary Issues**: Verify cron job setup

---

**Note**: This system ensures you're always aware of critical issues affecting your SmartBiller platform, allowing for quick response and resolution. 