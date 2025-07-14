# SmartBiller Admin Monitoring System

## Overview

The SmartBiller Admin Monitoring System provides comprehensive monitoring, analytics, and management capabilities for the SmartBiller property management platform. This system allows administrators to monitor system health, track user activities, manage security, and analyze performance metrics.

## Features

### 🔐 **Admin Authentication**
- Secure admin login system
- Role-based access control (admin, super_admin)
- Session management and security logging
- Password change enforcement

### 📊 **System Monitoring**
- Real-time system statistics
- Database health monitoring
- Performance metrics tracking
- Error logging and resolution

### 👥 **User Management**
- Monitor all user types (landlords, tenants, employees)
- User activity tracking
- Account status management
- Bulk user operations

### 🛡️ **Security Monitoring**
- Login attempt tracking
- Security alert system
- Suspicious activity detection
- IP address monitoring
- User agent tracking

### 📈 **Analytics & Reporting**
- User growth analytics
- Revenue tracking
- Usage statistics
- Performance metrics
- Custom report generation

### 📝 **Logging System**
- Comprehensive system logging
- Error tracking and resolution
- API usage monitoring
- Audit trail maintenance

## Installation & Setup

### 1. Database Migration

Run the database migration to create admin tables:

```bash
# Run the migration
flask db upgrade

# Or manually run the migration
python -m flask db upgrade
```

### 2. Create Admin User

Run the setup script to create the initial admin user:

```bash
python setup_admin.py
```

This will create:
- Admin user: `admin`
- Password: `admin123`
- Email: `admin@smartbiller.co.ke`

**⚠️ IMPORTANT**: Change the default password immediately after first login!

### 3. Access Admin Portal

Navigate to: `http://your-domain.com/admin/login`

## Admin Portal Sections

### 🏠 **Dashboard**
- System overview with key metrics
- Recent activities and alerts
- Database health status
- Quick action buttons

**Key Metrics:**
- Total landlords, tenants, employees
- Active subscriptions and trial users
- Recent logins and failed attempts
- Unresolved errors and security alerts

### 👥 **User Management**
- View all users by type (landlords, tenants, employees)
- Filter and search users
- Monitor user status and activity
- Bulk operations

**Features:**
- Paginated user lists
- User type filtering
- Status indicators
- Quick actions (view, edit, activate/deactivate)

### 📊 **Analytics**
- User growth charts
- Revenue analytics
- Usage statistics
- Performance metrics

**Charts & Reports:**
- User registration trends
- Revenue tracking
- SMS/Email usage
- API call statistics

### 🛡️ **Security**
- Login attempt monitoring
- Security alerts management
- IP address tracking
- Suspicious activity detection

**Security Features:**
- Failed login tracking
- IP-based security alerts
- User agent monitoring
- Alert resolution system

### 📝 **System Logs**
- Comprehensive system logging
- Filter by log level and category
- Search and pagination
- Export capabilities

**Log Categories:**
- Authentication (auth)
- Payment processing (payment)
- SMS notifications (sms)
- Email delivery (email)
- System operations (system)

### ⚠️ **Error Management**
- Error tracking and resolution
- Stack trace analysis
- Error categorization
- Resolution workflow

**Error Types:**
- Database errors
- API errors
- Authentication errors
- System errors

## Database Schema

### Core Admin Tables

#### `admin`
- Admin user accounts
- Role-based access control
- Login tracking

#### `system_log`
- Comprehensive system logging
- User activity tracking
- IP and user agent logging

#### `login_attempt`
- Login attempt tracking
- Success/failure logging
- Security monitoring

#### `system_metrics`
- Performance metrics
- Usage statistics
- System health data

#### `api_usage`
- API endpoint monitoring
- Response time tracking
- Usage analytics

#### `error_log`
- Error tracking
- Stack trace storage
- Resolution workflow

#### `database_health`
- Database performance metrics
- Connection monitoring
- Disk usage tracking

#### `security_alert`
- Security incident tracking
- Alert severity levels
- Resolution management

## Security Features

### 🔐 **Authentication Security**
- Password hashing with Werkzeug
- Session-based authentication
- Login attempt limiting
- Account lockout protection

### 🛡️ **Monitoring & Alerting**
- Real-time security monitoring
- Automated alert generation
- IP-based threat detection
- Suspicious activity identification

### 📊 **Audit Trail**
- Comprehensive activity logging
- User action tracking
- System change monitoring
- Compliance reporting

## API Endpoints

### Admin Authentication
```
POST /admin/login          # Admin login
GET  /admin/logout         # Admin logout
```

### Dashboard & Monitoring
```
GET  /admin/dashboard      # Admin dashboard
GET  /admin/users          # User management
GET  /admin/analytics      # Analytics data
GET  /admin/security       # Security monitoring
GET  /admin/logs           # System logs
GET  /admin/errors         # Error management
```

### Error & Alert Management
```
POST /admin/error/<id>/resolve    # Resolve error
POST /admin/alert/<id>/resolve    # Resolve alert
```

## Monitoring & Alerts

### System Health Monitoring
- Database connection monitoring
- Response time tracking
- Error rate monitoring
- Disk usage alerts

### Security Monitoring
- Failed login detection
- Suspicious IP tracking
- Unusual activity patterns
- Account compromise alerts

### Performance Monitoring
- API response times
- Database query performance
- System resource usage
- User experience metrics

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Admin System Configuration
ADMIN_EMAIL=admin@smartbiller.co.ke
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Security Settings
MAX_LOGIN_ATTEMPTS=5
LOGIN_TIMEOUT_MINUTES=15
SECURITY_ALERT_EMAIL=security@smartbiller.co.ke

# Monitoring Settings
METRICS_COLLECTION_INTERVAL=300  # 5 minutes
LOG_RETENTION_DAYS=90
ERROR_ALERT_THRESHOLD=10
```

### Logging Configuration

```python
# In your app configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/smartbiller.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
```

## Maintenance

### Regular Tasks

1. **Password Updates**
   - Change admin passwords regularly
   - Enforce strong password policies
   - Monitor password change compliance

2. **Log Management**
   - Review system logs weekly
   - Archive old logs monthly
   - Monitor log storage usage

3. **Security Reviews**
   - Review security alerts daily
   - Investigate failed login attempts
   - Monitor suspicious activities

4. **Performance Monitoring**
   - Check database health metrics
   - Monitor API response times
   - Review error rates

### Backup Procedures

```bash
# Backup admin data
pg_dump -t admin -t system_log -t login_attempt -t security_alert smartbiller > admin_backup.sql

# Restore admin data
psql smartbiller < admin_backup.sql
```

## Troubleshooting

### Common Issues

1. **Admin Login Fails**
   - Check database connection
   - Verify admin user exists
   - Check password hash

2. **Logs Not Appearing**
   - Check database permissions
   - Verify logging configuration
   - Check disk space

3. **Performance Issues**
   - Monitor database connections
   - Check query performance
   - Review system resources

### Debug Commands

```python
# Check admin user
from app.models import Admin
admin = Admin.query.filter_by(username='admin').first()
print(admin.email, admin.is_active)

# Check recent logs
from app.models import SystemLog
logs = SystemLog.query.order_by(SystemLog.created_at.desc()).limit(10).all()
for log in logs:
    print(f"{log.created_at}: {log.level} - {log.message}")

# Check security alerts
from app.models import SecurityAlert
alerts = SecurityAlert.query.filter_by(resolved=False).all()
for alert in alerts:
    print(f"{alert.severity}: {alert.title}")
```

## Security Best Practices

1. **Access Control**
   - Use strong passwords
   - Enable two-factor authentication
   - Regular access reviews

2. **Monitoring**
   - Monitor login attempts
   - Track suspicious activities
   - Review security alerts

3. **Data Protection**
   - Encrypt sensitive data
   - Regular backups
   - Secure data transmission

4. **Incident Response**
   - Document security procedures
   - Train staff on security
   - Regular security audits

## Support

For admin system support:

1. **Documentation**: Check this README
2. **Logs**: Review system logs for errors
3. **Database**: Check admin tables for issues
4. **Security**: Monitor security alerts

## Version History

- **v1.0**: Initial admin system implementation
- **v1.1**: Added security monitoring
- **v1.2**: Enhanced analytics and reporting
- **v1.3**: Improved error management

---

**SmartBiller Admin System** - Professional property management monitoring and administration. 