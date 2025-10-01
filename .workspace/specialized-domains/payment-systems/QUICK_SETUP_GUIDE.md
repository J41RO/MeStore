# Wompi Quick Setup Guide - Get Started in 10 Minutes

**For Developers**: Follow this guide to complete the Wompi integration and start accepting payments.

---

## Step 1: Get Wompi Sandbox Credentials (5 minutes)

### 1.1 Create Wompi Sandbox Account

1. Go to https://sandbox.wompi.co
2. Click "Registrarse" (Sign up)
3. Fill in:
   - Email
   - Password
   - Business name: "MeStore Test"
   - Business type: "Marketplace"
4. Verify email (check inbox)

### 1.2 Get API Keys

1. Log in to https://sandbox.wompi.co
2. Navigate to **Settings** → **API Keys**
3. Copy the following:
   - **Public Key**: `pub_test_...`
   - **Private Key**: `prv_test_...`
4. Generate webhook secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### 1.3 Configure Environment Variables

**Edit**: `/home/admin-jairo/MeStore/.env.development`

**Replace placeholders** with your actual credentials:

```bash
# Find these lines:
WOMPI_PUBLIC_KEY=pub_test_your_sandbox_public_key_here
WOMPI_PRIVATE_KEY=prv_test_your_sandbox_private_key_here
WOMPI_WEBHOOK_SECRET=test_webhook_secret_min_32_characters_here_for_hmac_validation

# Replace with:
WOMPI_PUBLIC_KEY=pub_test_YOUR_ACTUAL_KEY_FROM_WOMPI
WOMPI_PRIVATE_KEY=prv_test_YOUR_ACTUAL_KEY_FROM_WOMPI
WOMPI_WEBHOOK_SECRET=YOUR_GENERATED_SECRET_FROM_STEP_2
```

**Save the file** ✅

---

## Step 2: Configure Webhook (2 minutes)

### 2.1 Set Up ngrok for Local Testing

**Install ngrok** (if not already installed):
```bash
# Ubuntu/Debian
sudo snap install ngrok

# macOS
brew install ngrok

# Or download from https://ngrok.com/download
```

**Start ngrok tunnel**:
```bash
ngrok http 8000
```

**Output**:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### 2.2 Configure Webhook in Wompi Dashboard

1. Go to https://sandbox.wompi.co
2. Navigate to **Settings** → **Webhooks**
3. Click "Add Webhook"
4. Enter:
   - **URL**: `https://YOUR_NGROK_URL.ngrok.io/api/v1/payments/webhook`
   - **Events**: Select `transaction.updated`
5. Click "Save"

**Important**: Keep ngrok running while testing! ⚠️

---

## Step 3: Start Backend Server (1 minute)

**Terminal 1** (Backend):
```bash
cd /home/admin-jairo/MeStore
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify backend running**:
```bash
curl http://localhost:8000/api/v1/payments/config
```

**Expected response**:
```json
{
  "wompi_public_key": "pub_test_YOUR_KEY",
  "environment": "test",
  "accepted_methods": ["CARD", "PSE", "NEQUI"],
  "currency": "COP",
  "test_mode": true
}
```

If you see your actual public key → ✅ **Backend configured correctly**

---

## Step 4: Start Frontend Server (1 minute)

**Terminal 2** (Frontend):
```bash
cd /home/admin-jairo/MeStore/frontend
npm run dev
```

**Expected output**:
```
VITE v7.1.4  ready in 423 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.137:5173/
```

**Open browser**: http://localhost:5173

---

## Step 5: Test Payment Flow (1 minute)

### 5.1 Open Browser Console

1. Open http://localhost:5173
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Type: `WidgetCheckout`
5. Press Enter

**Expected**: You should see the WidgetCheckout object definition

If you see `undefined` → **Check Step 4**, widget didn't load

---

### 5.2 Test Payment Widget

**Option A - Quick Test** (using browser console):

```javascript
// Paste this in browser console
const widget = new WidgetCheckout({
  currency: 'COP',
  amountInCents: 50000, // $500 COP
  reference: 'TEST-ORDER-123',
  publicKey: 'YOUR_PUBLIC_KEY', // Replace with your key
  redirectUrl: 'http://localhost:5173/checkout/confirmation'
});

widget.open((result) => {
  console.log('Payment result:', result);
});
```

**Option B - Through Checkout Flow**:

1. Navigate to products page
2. Add product to cart
3. Go to checkout
4. Fill shipping address
5. Select payment method (PSE or Credit Card)
6. Widget should open automatically

---

## Step 6: Test with Sandbox Cards (2 minutes)

### Credit Card - APPROVED
```
Card Number:  4242 4242 4242 4242
Expiry:       12/25 (any future date)
CVV:          123
Name:         Test User
```

### Credit Card - DECLINED
```
Card Number:  4000 0000 0000 0002
Expiry:       12/25
CVV:          123
Name:         Test User
```

### Credit Card - 3D SECURE
```
Card Number:  4000 0027 6000 3184
Expiry:       12/25
CVV:          123
Name:         Test User
```

**Follow 3D Secure prompts in the modal**

---

### PSE Bank Transfer

1. Select "PSE" payment method
2. Choose any bank from the list
3. Enter:
   - User type: Natural person (0)
   - ID: 12345678901
   - Email: test@example.com
4. Click "Pagar"
5. In Wompi sandbox, simulate:
   - ✅ **Success**: Click "Aprobar"
   - ❌ **Failure**: Click "Rechazar"

---

## Troubleshooting

### Widget doesn't load
**Problem**: Console shows `WidgetCheckout is undefined`

**Solution**:
```bash
# Check index.html has the script
grep -n "checkout.wompi.co/widget.js" /home/admin-jairo/MeStore/frontend/index.html

# Should show: <script src="https://checkout.wompi.co/widget.js"></script>

# If missing, add it to index.html
```

---

### "Invalid public key" error
**Problem**: Widget shows "Invalid public key"

**Solution**:
```bash
# Verify .env.development has correct key
cat .env.development | grep WOMPI_PUBLIC_KEY

# Key should start with pub_test_ for sandbox
# Example: pub_test_abc123xyz789

# Restart backend after changing .env
```

---

### Webhook not received
**Problem**: Payment completes but order status doesn't update

**Solution**:
```bash
# 1. Check ngrok is running
curl https://YOUR_NGROK_URL.ngrok.io/api/v1/payments/health

# 2. Check Wompi dashboard for webhook errors
# Go to Settings → Webhooks → View Logs

# 3. Check backend logs
tail -f logs/development/mestocker.log

# 4. Verify webhook signature secret matches
cat .env.development | grep WOMPI_WEBHOOK_SECRET
```

---

### Backend config endpoint returns empty
**Problem**: `/api/v1/payments/config` returns empty public key

**Solution**:
```bash
# 1. Verify environment variable is set
cd /home/admin-jairo/MeStore
source .venv/bin/activate
python -c "from app.core.config import settings; print(settings.WOMPI_PUBLIC_KEY)"

# Should print: pub_test_YOUR_KEY

# 2. If empty, check .env.development is being loaded
python -c "import os; print(os.getenv('WOMPI_PUBLIC_KEY'))"

# 3. Restart backend server
```

---

## Next Steps After Successful Test

### 1. Complete Integration (if not done)

**If PaymentStep.tsx hasn't been updated**:

1. Edit `/home/admin-jairo/MeStore/frontend/src/components/checkout/steps/PaymentStep.tsx`
2. Import WompiCheckout:
   ```typescript
   import WompiCheckout from '../WompiCheckout';
   ```
3. Replace payment form submission with:
   ```typescript
   <WompiCheckout
     orderId={orderId}
     amount={getTotalWithShipping()}
     customerEmail={user?.email}
     reference={`ORDER-${orderId}-${Date.now()}`}
     publicKey={paymentMethods?.wompi_public_key || ''}
     onSuccess={(transaction) => {
       // Handle success
       goToNextStep();
     }}
     onError={(error) => {
       setError(error);
     }}
   />
   ```

---

### 2. Create Confirmation Page

**File**: `/home/admin-jairo/MeStore/frontend/src/pages/PaymentConfirmation.tsx`

**Template**:
```typescript
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { paymentService } from '../services/paymentService';

export default function PaymentConfirmation() {
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get('order_id');
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    if (orderId) {
      // Poll payment status
      paymentService.pollPaymentStatus(
        parseInt(orderId),
        (statusUpdate) => {
          setStatus(statusUpdate.payment_status);
        }
      );
    }
  }, [orderId]);

  // Render UI based on status
  return (
    <div>
      {status === 'APPROVED' && <SuccessMessage />}
      {status === 'PENDING' && <PendingMessage />}
      {status === 'DECLINED' && <FailureMessage />}
    </div>
  );
}
```

---

### 3. Production Deployment

**When ready for production**:

1. **Get production credentials**:
   - Go to https://wompi.co
   - Complete KYC verification
   - Get production keys

2. **Configure `.env.production`**:
   ```bash
   WOMPI_ENVIRONMENT=production
   WOMPI_BASE_URL=https://production.wompi.co/v1
   WOMPI_PUBLIC_KEY=pub_prod_YOUR_PRODUCTION_KEY
   WOMPI_PRIVATE_KEY=prv_prod_YOUR_PRODUCTION_KEY
   WOMPI_WEBHOOK_SECRET=production_secret_64_chars_min
   ```

3. **Update webhook URL in Wompi dashboard**:
   - URL: `https://mestore.com/api/v1/payments/webhook`
   - Ensure HTTPS and valid SSL certificate

4. **Test with small amount**:
   - Make $1 COP test transaction
   - Verify webhook received
   - Confirm order status updates

5. **Go live** 🚀

---

## Quick Reference

### Useful Commands

```bash
# Check Wompi config
curl http://localhost:8000/api/v1/payments/config | jq

# Test webhook endpoint
curl -X POST http://localhost:8000/api/v1/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{"event": "transaction.updated", "data": {}}'

# View backend logs
tail -f logs/development/mestocker.log

# Check ngrok tunnel
curl https://YOUR_NGROK_URL.ngrok.io/api/v1/payments/health
```

---

### Important URLs

- **Wompi Sandbox**: https://sandbox.wompi.co
- **Wompi Docs**: https://docs.wompi.co
- **Wompi Widget Docs**: https://docs.wompi.co/widget
- **Wompi API Docs**: https://docs.wompi.co/api
- **ngrok Download**: https://ngrok.com/download

---

### Test Credentials Summary

**Cards**:
- APPROVED: `4242 4242 4242 4242`
- DECLINED: `4000 0000 0000 0002`
- 3D SECURE: `4000 0027 6000 3184`

**PSE**:
- Any bank, ID: `12345678901`

**CVV**: `123` (any)
**Expiry**: Any future date (e.g., `12/25`)

---

## Support

**Need help?**

1. **Wompi Support**: soporte@wompi.co
2. **Documentation**: `.workspace/specialized-domains/payment-systems/`
3. **Integration Report**: `WOMPI_INTEGRATION_REPORT.md`
4. **Integration Plan**: `WOMPI_INTEGRATION_PLAN.md`

**Agent**: payment-systems-ai
**Status**: Ready for testing ✅
**Last Updated**: 2025-10-01
