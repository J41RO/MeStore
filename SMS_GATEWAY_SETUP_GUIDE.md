# 📱 SMS Gateway Setup Guide - MeStore Twilio Integration

## 🎯 Overview

This guide provides comprehensive instructions to configure the SMS Gateway for real SMS verification using Twilio integration. The system supports both development (simulation) and production modes.

## 🔧 Prerequisites

1. **Twilio Account**: Sign up at [https://www.twilio.com](https://www.twilio.com)
2. **Phone Number**: Purchase a Twilio phone number for SMS sending
3. **Redis**: For rate limiting and caching (already configured in MeStore)

## 📋 Step 1: Twilio Account Setup

### 1.1 Create Twilio Account
1. Go to [Twilio Console](https://console.twilio.com)
2. Create account and verify your email
3. Complete phone verification

### 1.2 Get Account Credentials
1. Go to **Account Dashboard**
2. Note down:
   - `Account SID`
   - `Auth Token`

### 1.3 Purchase Phone Number
1. Go to **Phone Numbers** > **Manage** > **Buy a number**
2. Select Colombia (+57) or your preferred country
3. Choose a number with SMS capabilities
4. Note down the purchased number (format: +57xxxxxxxxxx)

### 1.4 (Optional) Create Verify Service
For enhanced security:
1. Go to **Verify** > **Services**
2. Create new service
3. Note down the `Service SID`

## 🔐 Step 2: Environment Configuration

### 2.1 Update .env file

Add these variables to your `.env` file:

```bash
# ===== SMS/OTP CONFIGURATION =====
# Twilio Configuration (Required for production SMS)
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=+573001234567
TWILIO_VERIFY_SERVICE_SID=VA1234567890abcdef1234567890abcdef

# SMS Settings
SMS_ENABLED=true
SMS_RATE_LIMIT_PER_NUMBER=5
SMS_RATE_LIMIT_WINDOW=3600

# OTP Settings
OTP_EXPIRATION_MINUTES=10
OTP_MAX_ATTEMPTS=5
EMAIL_OTP_ENABLED=true
```

### 2.2 Environment Variables Explanation

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID | `AC1234...` | Yes |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token | `abc123...` | Yes |
| `TWILIO_FROM_NUMBER` | Your Twilio phone number | `+573001234567` | Yes |
| `TWILIO_VERIFY_SERVICE_SID` | Verify service SID | `VA1234...` | Optional |
| `SMS_ENABLED` | Enable/disable SMS service | `true` | No (default: true) |
| `SMS_RATE_LIMIT_PER_NUMBER` | SMS limit per number per hour | `5` | No (default: 5) |
| `SMS_RATE_LIMIT_WINDOW` | Rate limit window in seconds | `3600` | No (default: 3600) |

## 🚀 Step 3: Testing Configuration

### 3.1 Test SMS Service Status

Create a test script to verify configuration:

```python
# test_sms_service.py
import os
from app.services.sms_service import SMSService
from app.core.redis import RedisService

# Test SMS service initialization
sms_service = SMSService()
status = sms_service.get_service_status()

print("📱 SMS Service Status:")
for key, value in status.items():
    print(f"  {key}: {value}")

# Test phone number validation
test_numbers = [
    "3001234567",      # Colombian mobile
    "+573001234567",   # International format
    "6012345678",      # Colombian landline
    "invalid"          # Invalid number
]

print("\n📞 Phone Number Validation:")
for number in test_numbers:
    is_valid = sms_service.validate_phone_number(number)
    formatted = sms_service._format_colombian_phone(number)
    print(f"  {number} -> Valid: {is_valid}, Formatted: {formatted}")
```

### 3.2 Test OTP SMS (Development Mode)

```python
# test_otp_sms.py
from app.services.sms_service import SMSService

sms_service = SMSService()

# This will run in simulation mode if Twilio credentials are not configured
success, message = sms_service.send_otp_sms(
    phone_number="+573001234567",
    otp_code="123456",
    user_name="Test User"
)

print(f"SMS Result: {success}")
print(f"Message: {message}")
```

## 🎛️ Step 4: Development vs Production

### 4.1 Development Mode (Simulation)

When Twilio credentials are missing or invalid:
- SMS service runs in **simulation mode**
- Messages are logged to console
- No real SMS is sent
- Rate limiting still applies
- Perfect for development and testing

Example console output:
```
📱 SIMULACIÓN SMS OTP:
   Para: +573001234567
   Código: 123456
   Usuario: Test User
   Mensaje: MeStore: Hola Test User, tu código de verificación es 123456. Válido por 10 minutos. No compartir.
   Timestamp: 2025-01-15 10:30:00.123456
```

### 4.2 Production Mode

When Twilio credentials are properly configured:
- Real SMS messages are sent
- Twilio API connection is tested on startup
- All errors are properly handled and logged
- Rate limiting prevents abuse

## 📊 Step 5: API Endpoints

The following endpoints are now available:

### Send SMS Verification
```http
POST /api/v1/auth/send-verification-sms
Authorization: Bearer <token>
Content-Type: application/json

{
  "otp_type": "SMS"
}
```

### Verify SMS Code
```http
POST /api/v1/auth/verify-phone-otp
Authorization: Bearer <token>
Content-Type: application/json

{
  "otp_code": "123456"
}
```

### Send Email Verification
```http
POST /api/v1/auth/send-verification-email
Authorization: Bearer <token>
Content-Type: application/json

{
  "otp_type": "EMAIL"
}
```

### Verify Email Code
```http
POST /api/v1/auth/verify-email-otp
Authorization: Bearer <token>
Content-Type: application/json

{
  "otp_code": "123456"
}
```

## 🛡️ Step 6: Security Features

### 6.1 Rate Limiting
- **5 SMS per hour** per phone number (configurable)
- Redis-based tracking
- Applies to both simulation and production modes

### 6.2 Phone Number Validation
- Colombian format support (+57)
- International format validation
- Mobile and landline support

### 6.3 OTP Security
- 6-digit numeric codes
- 10-minute expiration
- Maximum 5 verification attempts
- Automatic cleanup of expired codes

## 🔍 Step 7: Monitoring and Troubleshooting

### 7.1 Service Status Check

```python
from app.services.sms_service import SMSService

sms_service = SMSService()
status = sms_service.get_service_status()
print(json.dumps(status, indent=2))
```

### 7.2 Rate Limit Status

```python
rate_status = sms_service.get_rate_limit_status("+573001234567")
print(json.dumps(rate_status, indent=2))
```

### 7.3 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Service in simulation mode" | Missing Twilio credentials | Add credentials to .env |
| "Rate limit exceeded" | Too many SMS requests | Wait or increase limit |
| "Invalid phone number" | Wrong format | Use Colombian format |
| "Authentication error" | Wrong Twilio credentials | Verify SID and Token |

### 7.4 Logs Location

SMS service logs are written to:
- Application logs: Check FastAPI console
- Twilio logs: Available in Twilio Console

## 🎯 Step 8: Frontend Integration

The frontend components are already configured and expect these endpoints:
- `/api/v1/auth/send-verification-sms` - Send SMS OTP
- `/api/v1/auth/verify-phone-otp` - Verify SMS code

The OTP verification component (`OTPVerification.tsx`) handles:
- SMS/Email type selection
- Code input with 6-digit interface
- Automatic resend with cooldown
- Error handling and user feedback

## 🚀 Step 9: Production Deployment

### 9.1 Environment Setup
1. Ensure all Twilio credentials are set in production environment
2. Set `ENVIRONMENT=production` in .env
3. Configure proper Redis connection for rate limiting
4. Monitor Twilio usage and billing

### 9.2 Security Checklist
- [ ] Twilio credentials secured (not in version control)
- [ ] Rate limiting configured appropriately
- [ ] Redis properly secured
- [ ] Logs properly configured
- [ ] Error monitoring in place

## 📈 Step 10: Scaling Considerations

### 10.1 High Volume
- Consider Twilio SendGrid for email
- Implement message queuing for high traffic
- Monitor Twilio rate limits
- Consider multiple phone numbers

### 10.2 International Support
- Add support for additional country phone formats
- Configure timezone-aware messaging
- Localize SMS templates

## 🔗 Additional Resources

- [Twilio SMS API Documentation](https://www.twilio.com/docs/sms)
- [Twilio Verify Service](https://www.twilio.com/docs/verify)
- [Colombian Phone Number Formats](https://www.twilio.com/docs/glossary/what-e164)

## 📞 Support

For technical support with the SMS Gateway integration:
1. Check application logs first
2. Verify Twilio Console for delivery status
3. Test with simulation mode to isolate issues
4. Review rate limiting status

---

**🎉 Congratulations!** Your SMS Gateway is now configured and ready for real SMS verification in MeStore.