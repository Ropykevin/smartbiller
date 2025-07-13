# SmartBiller API Documentation

## Overview

SmartBiller provides a RESTful API for property management operations. This document describes all available endpoints, request/response formats, and authentication methods.

## Base URL

```
http://localhost:5000
```

## Authentication

Most endpoints require authentication. The application uses session-based authentication.

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

email=user@example.com&password=password123
```

### Registration
```http
POST /register
Content-Type: application/x-www-form-urlencoded

name=Ropy Kevin&email=john@example.com&password=password123
```

## Landlord Endpoints

### Dashboard

#### Get Dashboard Data
```http
GET /dashboard
```

**Response:**
```json
{
  "landlord": {
    "id": 1,
    "name": "Ropy Kevin",
    "email": "john@example.com"
  },
  "properties": [
    {
      "id": 1,
      "name": "Sunset Apartments",
      "location": "Nairobi, Kenya",
      "units_count": 10
    }
  ],
  "usage": {
    "properties_count": 3,
    "units_count": 25,
    "sms_sent": 15,
    "plan": "Free Trial",
    "max_properties": "inf",
    "max_sms": 50
  },
  "trial": {
    "is_active": true,
    "days_remaining": 25
  }
}
```

### Property Management

#### Add Property
```http
POST /add_property
Content-Type: application/x-www-form-urlencoded

name=Sunset Apartments&location=Nairobi, Kenya&payment_method=mpesa&payment_destination=254700000000
```

**Response:**
```json
{
  "success": true,
  "message": "Property added successfully!",
  "property_id": 1
}
```

#### Get Properties
```http
GET /dashboard
```

**Response:** HTML dashboard with property list

#### Add Unit to Property
```http
POST /property/1/add_unit
Content-Type: application/x-www-form-urlencoded

unit_number=A1&rent_amount=25000&size=500&bedrooms=2&bathrooms=1
```

**Response:**
```json
{
  "success": true,
  "message": "Unit created successfully!",
  "unit_id": 1
}
```

#### Edit Unit
```http
POST /unit/1/edit
Content-Type: application/x-www-form-urlencoded

unit_number=A1&rent_amount=27000&size=500&bedrooms=2&bathrooms=1
```

#### Delete Unit
```http
POST /unit/1/delete
```

### Tenant Management

#### Add Tenant to Unit
```http
POST /unit/1/add_tenant
Content-Type: application/x-www-form-urlencoded

name=Ivy Maundu&phone=254700000001&email=jane@example.com&id_number=12345678&emergency_contact=254700000002&occupation=Engineer&employer=Tech Corp&move_in_date=2024-01-01
```

#### Log Rent Payment
```http
POST /tenant/1/log_rent
Content-Type: application/x-www-form-urlencoded

amount_paid=25000&date_paid=2024-01-15&month_paid_for=January 2024&status=Paid
```

#### Update Tenant Information
```http
POST /tenant/1/update
Content-Type: application/x-www-form-urlencoded

name=Ivy Maundu&phone=254700000001&email=jane@example.com&emergency_contact=254700000002
```

### Exit Notice Management

#### Get Exit Notices
```http
GET /landlord/exit_notices
```

#### Respond to Exit Notice
```http
POST /landlord/exit_notice/1/respond
Content-Type: application/x-www-form-urlencoded

status=Approved&landlord_response=Exit notice approved. Please ensure unit is cleaned before moving out.
```

### Subscription & Billing

#### Get Pricing Plans
```http
GET /pricing
```

**Response:** HTML page with pricing information

#### Upgrade Plan
```http
GET /upgrade_plan/professional
```

**Response:** HTML payment form

#### Process Payment
```http
POST /process_payment
Content-Type: application/x-www-form-urlencoded

plan_code=professional&billing_cycle=monthly&card_number=4111111111111111&expiry_month=12&expiry_year=2025&cvv=123&cardholder_name=Ropy Kevin
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully upgraded to Professional plan!",
  "redirect_url": "/dashboard"
}
```

### Reports

#### Generate Reports
```http
POST /reports
Content-Type: application/x-www-form-urlencoded

report_type=rent_collection&start_date=2024-01-01&end_date=2024-01-31&property_id=1
```

### SMS & Notifications

#### Send Reminders
```http
GET /send_reminders
```

**Response:**
```json
{
  "success": true,
  "message": "Reminders sent successfully",
  "sent_count": 5
}
```

#### Send Month-End Reminders
```http
GET /send_month_end_reminders
```

## Tenant Endpoints

### Authentication

#### Tenant Login
```http
POST /tenant_login
Content-Type: application/x-www-form-urlencoded

phone=254700000001
```

**Response:** SMS verification code sent

#### Verify SMS Code
```http
POST /tenant_verify
Content-Type: application/x-www-form-urlencoded

code=123456
```

### Tenant Dashboard

#### Get Tenant Dashboard
```http
GET /tenant_dashboard
```

**Response:**
```json
{
  "tenant": {
    "id": 1,
    "name": "Ivy Maundu",
    "phone": "254700000001",
    "unit": {
      "id": 1,
      "unit_number": "A1",
      "rent_amount": 25000,
      "property": {
        "name": "Sunset Apartments"
      }
    }
  },
  "rent_history": [
    {
      "id": 1,
      "amount_paid": 25000,
      "date_paid": "2024-01-15",
      "month_paid_for": "January 2024",
      "status": "Paid"
    }
  ],
  "balance": {
    "current_month": 0,
    "total_outstanding": 0
  }
}
```

### Exit Notice

#### Submit Exit Notice
```http
POST /tenant/exit_notice
Content-Type: application/x-www-form-urlencoded

intended_exit_date=2024-03-01&reason=Relocating for work&additional_comments=Need to move closer to new job location
```

**Response:**
```json
{
  "success": true,
  "message": "Exit notice submitted successfully! Your landlord will be notified."
}
```

### Receipts

#### Get Receipt
```http
GET /tenant/receipt/1
```

**Response:** PDF receipt file

## Error Responses

### Authentication Error
```json
{
  "error": "Unauthorized access",
  "code": 401
}
```

### Validation Error
```json
{
  "error": "Invalid input data",
  "details": {
    "email": "Invalid email format",
    "phone": "Phone number is required"
  },
  "code": 400
}
```

### Server Error
```json
{
  "error": "Internal server error",
  "code": 500
}
```

## Rate Limiting

- **SMS sending**: 50 SMS per month (trial), 200 SMS per month (professional)
- **API calls**: Limited based on subscription plan
- **File uploads**: 10MB per file

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Data Formats

### Date Format
All dates are in ISO 8601 format: `YYYY-MM-DD`

### Currency
All monetary values are in Kenyan Shillings (KES)

### Phone Numbers
Phone numbers should be in international format: `254700000000`

## Webhooks

SmartBiller supports webhooks for real-time notifications:

### Payment Webhook
```http
POST /webhooks/payment
Content-Type: application/json

{
  "event": "payment.success",
  "data": {
    "subscription_id": 1,
    "amount": 1200,
    "currency": "KES",
    "status": "completed"
  }
}
```

### SMS Webhook
```http
POST /webhooks/sms
Content-Type: application/json

{
  "event": "sms.delivered",
  "data": {
    "message_id": "msg_123",
    "phone": "254700000000",
    "status": "delivered"
  }
}
```

## SDK Examples

### Python
```python
import requests

# Login
session = requests.Session()
response = session.post('http://localhost:5000/login', data={
    'email': 'user@example.com',
    'password': 'password123'
})

# Add property
response = session.post('http://localhost:5000/add_property', data={
    'name': 'Sunset Apartments',
    'location': 'Nairobi, Kenya'
})
```

### JavaScript
```javascript
// Login
const response = await fetch('/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'email=user@example.com&password=password123'
});

// Add property
const propertyResponse = await fetch('/add_property', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'name=Sunset Apartments&location=Nairobi, Kenya'
});
```

## Support

For API support, contact:
- Email: api@smartbiller.com
- Documentation: https://docs.smartbiller.com/api
- Status page: https://status.smartbiller.com 