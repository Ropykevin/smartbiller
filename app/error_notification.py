import json
import traceback
from datetime import datetime, timedelta
from flask import current_app, request
from flask_mail import Message
from app import mail, db
from app.models import ErrorLog, SystemLog

class ErrorNotificationService:
    """Service for sending critical error notifications via email"""
    
    # Critical error types that should trigger email notifications
    CRITICAL_ERROR_TYPES = [
        'DatabaseError',
        'ConnectionError', 
        'AuthenticationError',
        'SecurityViolation',
        'PaymentError',
        'SystemError',
        'CriticalError'
    ]
    
    # Error severity levels
    SEVERITY_LEVELS = {
        'low': 1,
        'medium': 2, 
        'high': 3,
        'critical': 4
    }
    
    @staticmethod
    def should_notify(error_type, severity='medium'):
        """Determine if an error should trigger email notification"""
        # Always notify for critical errors
        if error_type in ErrorNotificationService.CRITICAL_ERROR_TYPES:
            return True
            
        # Notify for high/critical severity
        if severity in ['high', 'critical']:
            return True
            
        return False
    
    @staticmethod
    def send_error_notification(error_data, error_type, error_message, stack_trace=None, 
                              user_id=None, user_type=None, severity='medium'):
        """Send email notification for critical errors"""
        try:
            # Check if we should send notification
            if not ErrorNotificationService.should_notify(error_type, severity):
                return False
            
            # Create email subject
            subject = f"🚨 SmartBiller Critical Error Alert - {error_type}"
            
            # Build email body
            body = ErrorNotificationService._build_error_email_body(
                error_data, error_type, error_message, stack_trace, 
                user_id, user_type, severity
            )
            
            # Create message
            msg = Message(
                subject=subject,
                recipients=['ropykevin@gmail.com'],
                html=body
            )
            
            # Send email
            mail.send(msg)
            
            # Log the notification
            ErrorNotificationService._log_notification_sent(error_type, error_message)
            
            print(f"✅ Critical error notification sent to ropykevin@gmail.com for {error_type}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send error notification: {str(e)}")
            return False
    
    @staticmethod
    def _build_error_email_body(error_data, error_type, error_message, stack_trace, 
                               user_id, user_type, severity):
        """Build HTML email body for error notification"""
        
        # Get current timestamp
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Severity color mapping
        severity_colors = {
            'low': '#10B981',      # Green
            'medium': '#F59E0B',   # Yellow  
            'high': '#EF4444',     # Red
            'critical': '#DC2626'  # Dark Red
        }
        
        severity_color = severity_colors.get(severity, '#6B7280')
        
        # Build request info
        request_info = ""
        if request:
            request_info = f"""
            <tr>
                <td><strong>URL:</strong></td>
                <td>{request.url}</td>
            </tr>
            <tr>
                <td><strong>Method:</strong></td>
                <td>{request.method}</td>
            </tr>
            <tr>
                <td><strong>IP Address:</strong></td>
                <td>{request.remote_addr}</td>
            </tr>
            <tr>
                <td><strong>User Agent:</strong></td>
                <td>{request.user_agent.string if request.user_agent else 'N/A'}</td>
            </tr>
            """
        
        # Build stack trace (truncated for email)
        stack_trace_html = ""
        if stack_trace:
            # Limit stack trace to first 20 lines for email
            stack_lines = stack_trace.split('\n')[:20]
            stack_trace_html = f"""
            <tr>
                <td><strong>Stack Trace:</strong></td>
                <td>
                    <pre style="background: #f3f4f6; padding: 10px; border-radius: 5px; font-size: 12px; max-height: 300px; overflow-y: auto;">
{chr(10).join(stack_lines)}
{f'... (truncated - see admin panel for full trace)' if len(stack_trace.split(chr(10))) > 20 else ''}
                    </pre>
                </td>
            </tr>
            """
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>SmartBiller Critical Error Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: {severity_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .error-details {{ background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; }}
                td:first-child {{ font-weight: bold; width: 150px; }}
                .severity-badge {{ 
                    display: inline-block; 
                    padding: 4px 8px; 
                    border-radius: 4px; 
                    color: white; 
                    font-weight: bold;
                    background: {severity_color};
                }}
                .footer {{ background: #f3f4f6; padding: 15px; text-align: center; font-size: 12px; color: #6b7280; }}
                pre {{ white-space: pre-wrap; word-wrap: break-word; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚨 SmartBiller Critical Error Alert</h1>
                <p>System Error Detected - Immediate Attention Required</p>
            </div>
            
            <div class="content">
                <div class="error-details">
                    <h2>Error Information</h2>
                    <table>
                        <tr>
                            <td><strong>Error Type:</strong></td>
                            <td>{error_type}</td>
                        </tr>
                        <tr>
                            <td><strong>Severity:</strong></td>
                            <td><span class="severity-badge">{severity.upper()}</span></td>
                        </tr>
                        <tr>
                            <td><strong>Timestamp:</strong></td>
                            <td>{timestamp}</td>
                        </tr>
                        <tr>
                            <td><strong>Error Message:</strong></td>
                            <td>{error_message}</td>
                        </tr>
                        <tr>
                            <td><strong>User ID:</strong></td>
                            <td>{user_id or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong>User Type:</strong></td>
                            <td>{user_type or 'N/A'}</td>
                        </tr>
                        {request_info}
                        {stack_trace_html}
                    </table>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background: #fef3c7; border-left: 4px solid #f59e0b; border-radius: 4px;">
                    <h3>🔍 Recommended Actions</h3>
                    <ul>
                        <li>Check the admin panel for detailed error logs</li>
                        <li>Review system logs for related issues</li>
                        <li>Monitor system performance and database connections</li>
                        <li>Verify all external service integrations</li>
                        <li>Check for any recent deployments or configuration changes</li>
                    </ul>
                </div>
                
                <div style="margin: 20px 0; padding: 15px; background: #dbeafe; border-left: 4px solid #3b82f6; border-radius: 4px;">
                    <h3>📊 System Context</h3>
                    <p><strong>Environment:</strong> {current_app.config.get('FLASK_ENV', 'Unknown')}</p>
                    <p><strong>Database:</strong> {current_app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown').split('@')[0] if '@' in current_app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'Unknown'}</p>
                    <p><strong>Error ID:</strong> {error_data.get('id', 'N/A') if error_data else 'N/A'}</p>
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated alert from SmartBiller Error Monitoring System</p>
                <p>Generated on {timestamp}</p>
                <p>Please do not reply to this email. Contact the development team for support.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    @staticmethod
    def _log_notification_sent(error_type, error_message):
        """Log that a notification was sent"""
        try:
            log = SystemLog(
                level='info',
                category='notification',
                message=f'Critical error notification sent for {error_type}: {error_message[:100]}...',
                user_id=None,
                user_type='system',
                ip_address=None,
                user_agent=None
            )
            db.session.add(log)
            db.session.commit()
        except Exception as e:
            print(f"Failed to log notification: {str(e)}")
    
    @staticmethod
    def log_and_notify_error(error_type, error_message, stack_trace=None, 
                           user_id=None, user_type=None, ip_address=None, 
                           user_agent=None, url=None, method=None, severity='medium'):
        """Log error and send notification if critical"""
        
        try:
            # Log the error to database
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                user_id=user_id,
                user_type=user_type,
                ip_address=ip_address,
                user_agent=user_agent,
                url=url,
                method=method
            )
            db.session.add(error_log)
            db.session.commit()
            
            # Send notification if critical
            if ErrorNotificationService.should_notify(error_type, severity):
                ErrorNotificationService.send_error_notification(
                    error_data={'id': error_log.id},
                    error_type=error_type,
                    error_message=error_message,
                    stack_trace=stack_trace,
                    user_id=user_id,
                    user_type=user_type,
                    severity=severity
                )
            
            return error_log.id
            
        except Exception as e:
            print(f"Failed to log and notify error: {str(e)}")
            return None
    
    @staticmethod
    def send_daily_error_summary():
        """Send daily summary of errors to admin"""
        try:
            # Get errors from last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_errors = ErrorLog.query.filter(
                ErrorLog.created_at >= yesterday
            ).order_by(ErrorLog.created_at.desc()).all()
            
            if not recent_errors:
                return False
            
            # Group errors by type
            error_summary = {}
            for error in recent_errors:
                if error.error_type not in error_summary:
                    error_summary[error.error_type] = []
                error_summary[error.error_type].append(error)
            
            # Build summary email
            subject = f"📊 SmartBiller Daily Error Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"
            
            # Build error breakdown HTML
            error_breakdown_html = ""
            for error_type, errors in error_summary.items():
                error_rows = ""
                for error in errors[:5]:
                    error_message = error.error_message[:100]
                    if len(error.error_message) > 100:
                        error_message += "..."
                    
                    error_rows += f"""
                    <tr>
                        <td>{error.created_at.strftime('%H:%M:%S')}</td>
                        <td>{error_message}</td>
                        <td>{error.user_id or 'N/A'}</td>
                        <td>{error.ip_address or 'N/A'}</td>
                    </tr>
                    """
                
                if len(errors) > 5:
                    error_rows += f'<tr><td colspan="4"><em>... and {len(errors) - 5} more errors</em></td></tr>'
                
                error_breakdown_html += f"""
                <div class="error-group">
                    <h3>{error_type}</h3>
                    <p class="error-count">Count: {len(errors)}</p>
                    <table>
                        <tr>
                            <th>Time</th>
                            <th>Message</th>
                            <th>User</th>
                            <th>IP</th>
                        </tr>
                        {error_rows}
                    </table>
                </div>
                """
            
            body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Daily Error Summary</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .header {{ background: #1f2937; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; }}
                    .error-group {{ margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
                    .error-count {{ font-size: 18px; font-weight: bold; color: #dc2626; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                    th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #e5e7eb; }}
                    th {{ background: #f9fafb; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>📊 SmartBiller Daily Error Summary</h1>
                    <p>Error Report for {datetime.utcnow().strftime('%Y-%m-%d')}</p>
                </div>
                
                <div class="content">
                    <h2>Summary</h2>
                    <p>Total errors in the last 24 hours: <strong>{len(recent_errors)}</strong></p>
                    
                    <h2>Error Breakdown</h2>
                    {error_breakdown_html}
                    
                    <div style="margin-top: 30px; padding: 15px; background: #f3f4f6; border-radius: 8px;">
                        <h3>🔗 Quick Actions</h3>
                        <ul>
                            <li><a href="https://smartbiller.co.ke/admin/errors">View All Errors in Admin Panel</a></li>
                            <li><a href="https://smartbiller.co.ke/admin/logs">View System Logs</a></li>
                            <li><a href="https://smartbiller.co.ke/admin/analytics">View System Analytics</a></li>
                        </ul>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = Message(
                subject=subject,
                recipients=['ropykevin@gmail.com'],
                html=body
            )
            
            mail.send(msg)
            print(f"✅ Daily error summary sent to ropykevin@gmail.com")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send daily error summary: {str(e)}")
            return False 