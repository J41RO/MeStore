#!/usr/bin/env python3
"""
Twilio Configuration Setup and Testing Script for MeStore
=========================================================

This script helps you set up and test your Twilio configuration safely.
"""

import os
import asyncio
from typing import Dict, Any
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_banner():
    """Print setup banner."""
    print("🚀 MeStore Twilio Configuration Setup")
    print("=" * 50)
    print()

def check_environment():
    """Check if all required environment variables are set."""
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_FROM_NUMBER'
    ]

    missing_vars = []
    current_values = {}

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mask sensitive values for display
            if 'TOKEN' in var:
                current_values[var] = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***masked***"
            else:
                current_values[var] = value

    print("📋 Environment Variables Check:")
    print("-" * 30)

    for var in required_vars:
        status = "✅" if var not in missing_vars else "❌"
        value = current_values.get(var, "NOT SET")
        print(f"{status} {var}: {value}")

    print()

    if missing_vars:
        print("❌ Missing required variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("📝 Please set these in your .env.local file or environment")
        print("💡 See .env.twilio.example for reference")
        return False

    print("✅ All required environment variables are set!")
    return True

async def test_twilio_connection():
    """Test Twilio API connection."""
    try:
        from app.services.sms_service import SMSService

        print("🔄 Testing Twilio Connection...")
        print("-" * 30)

        sms_service = SMSService()
        status = sms_service.get_service_status()

        if status['sms_enabled']:
            print("✅ Twilio Connection: ACTIVE")
            print(f"   📱 From Number: {status['twilio_from_number']}")
            print(f"   🏢 Account SID: {status['twilio_account_sid'][:8]}...{status['twilio_account_sid'][-4:]}")
        else:
            print("❌ Twilio Connection: DISABLED (Simulation Mode)")
            print("   💡 Check your credentials and SMS_ENABLED setting")

        return status['sms_enabled']

    except Exception as e:
        print(f"❌ Connection Test Failed: {str(e)}")
        return False

def prompt_phone_number():
    """Prompt user for test phone number."""
    print("📞 Test Phone Number Setup")
    print("-" * 30)

    while True:
        print("Enter your phone number for testing:")
        print("  US format: +17371234567")
        print("  Colombia format: +573001234567")

        phone = input("Phone number: ").strip()

        if phone.startswith('+1') and len(phone) == 12:
            return phone, 'US'
        elif phone.startswith('+57') and len(phone) == 13:
            return phone, 'CO'
        else:
            print("❌ Invalid format. Please use +1XXXXXXXXXX or +57XXXXXXXXXX")
            continue

async def send_test_sms():
    """Send a test SMS."""
    try:
        from app.services.sms_service import SMSService

        phone, country = prompt_phone_number()

        print(f"📤 Sending test SMS to {phone}...")
        print("-" * 30)

        sms_service = SMSService()
        success, message = await sms_service.send_otp_sms(
            phone_number=phone,
            otp_code="123456"  # Test code
        )

        if success:
            print("✅ SMS Sent Successfully!")
            print(f"   📱 To: {phone}")
            print(f"   💬 Message: {message}")
            print()
            print("📋 Check your phone for the test message")
            return True
        else:
            print(f"❌ SMS Failed: {message}")
            return False

    except Exception as e:
        print(f"❌ SMS Test Failed: {str(e)}")
        return False

def print_security_tips():
    """Print security best practices."""
    print("🔒 Security Best Practices")
    print("-" * 30)
    print("1. Never commit .env.local to git")
    print("2. Use different credentials for dev/production")
    print("3. Rotate your Auth Token periodically")
    print("4. Monitor your Twilio usage dashboard")
    print("5. Set up spending alerts in Twilio console")
    print("6. Use Twilio Verify Service for production")
    print()

def print_next_steps():
    """Print next steps for the user."""
    print("🎯 Next Steps")
    print("-" * 30)
    print("1. Test the registration flow:")
    print("   - Go to http://192.168.1.137:5173/register")
    print("   - Use your real email: jairo.colina.co@gmail.com")
    print("   - Select your country code (US +1)")
    print("   - Enter your phone number")
    print()
    print("2. For development testing:")
    print("   - Use bypass code: 123456")
    print("   - Works with any email ending in @gmail.com")
    print()
    print("3. Production deployment:")
    print("   - Set ENVIRONMENT=production")
    print("   - Update TWILIO_FROM_NUMBER if needed")
    print("   - Consider using Twilio Verify Service")
    print()

async def main():
    """Main setup function."""
    print_banner()

    # Step 1: Check environment
    env_ok = check_environment()
    if not env_ok:
        return 1

    print()

    # Step 2: Test connection
    connection_ok = await test_twilio_connection()
    print()

    if connection_ok:
        # Step 3: Offer to send test SMS
        print("🧪 Would you like to send a test SMS? (y/n)")
        if input().strip().lower() == 'y':
            await send_test_sms()
            print()

    # Step 4: Print security tips and next steps
    print_security_tips()
    print_next_steps()

    return 0

if __name__ == "__main__":
    # Load environment variables
    try:
        from app.core.config import settings
        print(f"📍 Environment: {settings.ENVIRONMENT}")
        print()
    except Exception as e:
        print(f"⚠️  Could not load settings: {e}")
        print("Make sure you're running from the project root")
        print()

    # Run the setup
    exit_code = asyncio.run(main())
    sys.exit(exit_code)