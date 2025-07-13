# SmartBiller - Property Management SaaS

A comprehensive Flask-based SaaS application for property management, rent tracking, and tenant communication.

## 🏠 Overview

SmartBiller is a modern property management platform designed for landlords and property managers. It provides tools for managing properties, tracking rent payments, communicating with tenants, and generating reports.

## ✨ Features

### 🎯 Core Features
- **Property Management**: Add and manage multiple properties
- **Unit Management**: Track individual units with detailed information
- **Tenant Management**: Manage tenant information and rent payments
- **Rent Tracking**: Monitor rent payments and outstanding balances
- **SMS Notifications**: Send reminders and notifications to tenants
- **Exit Notice Management**: Handle tenant exit requests
- **Reporting**: Generate detailed reports and analytics

### 💳 Subscription Plans
- **Free Trial**: 30-day free trial with unlimited properties
- **Basic Plan**: Up to 3 properties, 50 SMS/month
- **Professional Plan**: Up to 20 properties, 200 SMS/month, PDF generation
- **Enterprise Plan**: Unlimited properties, custom pricing

### 🔐 Security Features
- Secure authentication system
- Role-based access (Landlord/Tenant)
- SMS-based tenant verification
- Encrypted password storage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smartbiller
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost/smartbiller
   OPENAI_API_KEY=your-openai-api-key
   ```

5. **Initialize the database**
   ```bash
   flask db migrate -m "Add logged_by_employee_id to rent_log"
   flask db upgrade
   python setup_subscription.py
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
smartbiller/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models
│   ├── routes.py                # Application routes
│   ├── subscription_service.py  # Subscription logic
│   ├── sms_service.py          # SMS functionality
│   ├── static/                  # Static files (CSS, JS, images)
│   └── templates/               # HTML templates
├── migrations/                  # Database migrations
├── instance/                    # Instance-specific files
├── requirements.txt             # Python dependencies
├── run.py                      # Application entry point
└── README.md                   # This file
```

## 🗄️ Database Models

### Core Models
- **Landlord**: User accounts and subscription information
- **Property**: Property details and management
- **Unit**: Individual units within properties
- **Tenant**: Tenant information and rent history
- **RentLog**: Rent payment tracking
- **ExitNotice**: Tenant exit request management
- **PricingPlan**: Subscription plan definitions
- **Subscription**: User subscription details
- **UsageLog**: Feature usage tracking

## 🔧 Configuration

### Environment Variables
- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for chatbot

### Email Configuration
For employee welcome emails and invoice delivery, configure these email settings:
- `MAIL_SERVER`: SMTP server (default: smtp.gmail.com)
- `MAIL_PORT`: SMTP port (default: 587)
- `MAIL_USE_TLS`: Use TLS (default: True)
- `MAIL_USE_SSL`: Use SSL (default: False)
- `MAIL_USERNAME`: Email username
- `MAIL_PASSWORD`: Email password/app password
- `MAIL_DEFAULT_SENDER`: Default sender email

### Database Configuration
The application uses PostgreSQL with SQLAlchemy ORM. Configure your database connection in the `.env` file.

## 📱 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Property Management
- `GET /dashboard` - Main dashboard
- `POST /add_property` - Add new property
- `POST /property/<id>/add_unit` - Add unit to property
- `GET /unit/<id>/edit` - Edit unit details

### Tenant Management
- `POST /unit/<id>/add_tenant` - Add tenant to unit
- `POST /tenant/<id>/log_rent` - Log rent payment
- `GET /tenant/<id>/update` - Update tenant information

### Subscription & Billing
- `GET /pricing` - View pricing plans
- `GET /upgrade` - Upgrade subscription
- `POST /process_payment` - Process payment

### Tenant Portal
- `GET /tenant_login` - Tenant login
- `POST /tenant_verify` - Verify tenant SMS code
- `GET /tenant_dashboard` - Tenant dashboard
- `POST /tenant/exit_notice` - Submit exit notice

## 🎨 Frontend

### Technologies Used
- **HTML5/CSS3**: Modern, responsive design
- **Tailwind CSS**: Utility-first CSS framework
- **JavaScript**: Interactive features
- **Font Awesome**: Icons

### Key Templates
- `base.html`: Base template with navigation
- `dashboard.html`: Main landlord dashboard
- `tenant_dashboard.html`: Tenant portal
- `pricing.html`: Subscription plans
- `upgrade.html`: Plan upgrade interface

## 🔒 Security

### Authentication
- Password hashing with Werkzeug
- Session-based authentication
- SMS verification for tenants

### Data Protection
- SQL injection prevention with SQLAlchemy
- XSS protection with template escaping
- CSRF protection

## 📊 Subscription System

### Trial Period
- 30-day free trial for new users
- Unlimited properties during trial
- 50 SMS per month during trial
- No credit card required

### Plan Limits
- **Basic**: 3 properties, 50 SMS/month
- **Professional**: 20 properties, 200 SMS/month
- **Enterprise**: Unlimited properties, unlimited SMS

### Usage Tracking
- Property count monitoring
- SMS usage tracking
- PDF generation tracking
- API call monitoring

## 🚀 Deployment

### Production Setup
1. Set up PostgreSQL database
2. Configure environment variables
3. Set up reverse proxy (nginx)
4. Use WSGI server (gunicorn)
5. Set up SSL certificates

### Docker Deployment
```bash
# Build image
docker build -t smartbiller .

# Run container
docker run -p 5000:5000 smartbiller
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Test Coverage
- Unit tests for models
- Integration tests for routes
- API endpoint testing

## 📈 Monitoring

### Application Monitoring
- Flask debug mode for development
- Error logging and tracking
- Performance monitoring

### Database Monitoring
- Query performance tracking
- Connection pool monitoring
- Migration tracking

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- Check the [Documentation](docs/)
- Review [FAQ](docs/FAQ.md)
- Open an issue on GitHub
- Contact support team

### Common Issues
- Database connection problems
- SMS service configuration
- Payment processing issues
- Template rendering errors

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Core property management features
- Subscription system
- SMS notifications
- Tenant portal

## 📞 Contact

- **Email**: support@smartbiller.com
- **Website**: https://smartbiller.com
- **GitHub**: https://github.com/smartbiller

---

**SmartBiller** - Simplifying Property Management 🏠✨ 