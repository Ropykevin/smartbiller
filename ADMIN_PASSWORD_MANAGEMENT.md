# SmartBiller Admin Password Management

This guide covers all methods for managing admin passwords in SmartBiller.

## 🔐 **Methods to Change Admin Password**

### **Method 1: Command Line Script (Recommended)**

The most secure way to manage admin passwords is using the command-line script:

```bash
# Create new admin user
python setup_admin.py create

# Change existing admin password
python setup_admin.py change-password

# List all admin users
python setup_admin.py list

# Reset admin password (for forgotten passwords)
python setup_admin.py reset
```

#### **Creating a New Admin User**
```bash
python setup_admin.py create
```
This will prompt you for:
- Username (default: admin)
- Email (default: admin@smartbiller.co.ke)
- Password (minimum 6 characters)
- Role (admin/super_admin)

#### **Changing Admin Password**
```bash
python setup_admin.py change-password
```
This will:
1. List all active admin users
2. Ask you to select which admin to change
3. Verify current password
4. Set new password

#### **Resetting Admin Password**
```bash
python setup_admin.py reset
```
Use this when you've forgotten the password:
1. List all active admin users
2. Select admin to reset
3. Confirm the reset
4. Set new password

### **Method 2: Admin Panel Web Interface**

1. **Login to Admin Panel**
   - Go to: `http://your-domain.com/admin/login`
   - Enter admin credentials

2. **Access Password Change**
   - In the sidebar, click "Change Password" under the admin info
   - Or go directly to: `http://your-domain.com/admin/change-password`

3. **Change Password**
   - Enter current password
   - Enter new password (minimum 6 characters)
   - Confirm new password
   - Click "Update Password"

### **Method 3: Database Direct Update (Emergency Only)**

⚠️ **Warning**: Only use this method in emergencies when other methods fail.

```sql
-- Connect to your database
psql -U smartbiller -d smartbiller

-- Update admin password (replace 'new_password' with actual password)
UPDATE admin 
SET password = 'pbkdf2:sha256:600000$your_hash_here', 
    updated_at = NOW() 
WHERE username = 'admin';
```

**To generate the password hash:**
```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('your_new_password'))
```

## 🛡️ **Security Best Practices**

### **Password Requirements**
- Minimum 6 characters
- Recommended: 12+ characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid common words or personal information

### **Password Change Frequency**
- Change admin passwords every 90 days
- Change immediately after any security incident
- Use different passwords for different admin accounts

### **Access Control**
- Limit admin access to trusted personnel only
- Use role-based access (admin vs super_admin)
- Monitor admin login attempts
- Enable two-factor authentication if possible

## 📋 **Admin User Management**

### **Creating Multiple Admin Users**
```bash
# Create super admin
python setup_admin.py create
# Username: superadmin
# Role: super_admin

# Create regular admin
python setup_admin.py create
# Username: admin
# Role: admin
```

### **Listing Admin Users**
```bash
python setup_admin.py list
```
Shows:
- Username and email
- Role (admin/super_admin)
- Status (active/inactive)
- Last login time
- Creation date

### **Admin Roles**
- **admin**: Standard admin privileges
- **super_admin**: Full system access (can manage other admins)

## 🔧 **Troubleshooting**

### **Common Issues**

#### **"Admin user not found" Error**
```bash
# Check if admin exists
python setup_admin.py list

# If no admins exist, create one
python setup_admin.py create
```

#### **"Current password is incorrect"**
- Double-check the current password
- Use the reset method if password is forgotten:
```bash
python setup_admin.py reset
```

#### **Database Connection Issues**
```bash
# Check database connection
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✅ Database connection successful')
    except Exception as e:
        print(f'❌ Database error: {e}')
"
```

#### **Permission Denied Errors**
```bash
# Check file permissions
ls -la setup_admin.py

# Make executable if needed
chmod +x setup_admin.py
```

### **Emergency Recovery**

If all admin access is lost:

1. **Stop the application**
   ```bash
   docker-compose down
   ```

2. **Access database directly**
   ```bash
   docker-compose exec db psql -U smartbiller -d smartbiller
   ```

3. **Create emergency admin**
   ```sql
   INSERT INTO admin (username, email, password, role, is_active, created_at, updated_at)
   VALUES ('emergency_admin', 'emergency@smartbiller.co.ke', 
           'pbkdf2:sha256:600000$your_hash_here', 'super_admin', true, NOW(), NOW());
   ```

4. **Restart application**
   ```bash
   docker-compose up -d
   ```

## 📊 **Monitoring & Logging**

### **Password Change Logs**
All password changes are logged in the system:
- **Location**: `/admin/logs`
- **Category**: `auth`
- **Level**: `info`

### **Security Monitoring**
- Failed login attempts are tracked
- Suspicious activity is flagged
- Security alerts are generated

### **Audit Trail**
```sql
-- View recent password changes
SELECT * FROM system_log 
WHERE category = 'auth' 
AND message LIKE '%password%'
ORDER BY created_at DESC;
```

## 🚀 **Quick Start Guide**

### **First Time Setup**
1. **Create initial admin**
   ```bash
   python setup_admin.py create
   ```

2. **Access admin panel**
   - Go to: `http://your-domain.com/admin/login`
   - Login with created credentials

3. **Change default password**
   - Use the web interface or command line
   - Set a strong, unique password

4. **Verify access**
   - Test all admin functions
   - Check system logs

### **Regular Maintenance**
1. **Monthly password review**
   ```bash
   python setup_admin.py list
   ```

2. **Quarterly password changes**
   ```bash
   python setup_admin.py change-password
   ```

3. **Security audit**
   - Review admin logs
   - Check for suspicious activity
   - Update security settings

## 📞 **Support**

### **Getting Help**
1. Check this documentation
2. Review system logs: `/admin/logs`
3. Check error logs: `/admin/errors`
4. Contact system administrator

### **Emergency Contacts**
- **System Admin**: admin@smartbiller.co.ke
- **Security Team**: security@smartbiller.co.ke
- **Technical Support**: support@smartbiller.co.ke

## 🔒 **Security Checklist**

- [ ] Admin passwords are at least 6 characters
- [ ] Passwords include mixed case, numbers, symbols
- [ ] Passwords are changed every 90 days
- [ ] Different passwords for different admin accounts
- [ ] Failed login attempts are monitored
- [ ] Security alerts are enabled
- [ ] Admin access is limited to trusted personnel
- [ ] Regular security audits are performed
- [ ] Emergency recovery procedures are documented
- [ ] All password changes are logged

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Maintainer**: SmartBiller Development Team 