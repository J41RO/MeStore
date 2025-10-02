# Wompi Payment Integration - Visual Flow Diagram

## Complete Payment Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER CHECKOUT JOURNEY                            │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   CART       │ ───▶ │   SHIPPING   │ ───▶ │   PAYMENT    │ ───▶ │ CONFIRMATION │
│   STEP       │      │     STEP     │      │     STEP     │      │     STEP     │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
     │                      │                      │                      │
     │                      │                      │                      │
     ▼                      ▼                      ▼                      ▼
  Add items            Fill address        Select payment          View order
  View totals          Calculate shipping  Create order            details
  Proceed              Save info           Process payment         Track delivery


═══════════════════════════════════════════════════════════════════════════
                           PAYMENT STEP DETAILS
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Payment Method Selection                                        │
└─────────────────────────────────────────────────────────────────────────┘

  User Interface:
  ┌────────────────────────────────────────────────────────┐
  │  ◉  PSE - Pago Seguro en Línea                        │ ◄── Radio Selection
  │     Paga directamente desde tu cuenta bancaria        │
  ├────────────────────────────────────────────────────────┤
  │  ○  Tarjeta de Crédito/Débito                         │ ◄── User Clicks
  │     Visa, Mastercard, American Express                │
  ├────────────────────────────────────────────────────────┤
  │  ○  Transferencia Bancaria                            │
  │     Transferencia manual a nuestra cuenta             │
  ├────────────────────────────────────────────────────────┤
  │  ○  Pago Contraentrega                                │
  │     Paga en efectivo al recibir tu pedido             │
  └────────────────────────────────────────────────────────┘

           │
           ▼
  User selects "Tarjeta de Crédito/Débito"
           │
           ▼

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Payment Information Panel                                       │
└─────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────┐
  │  Pago con Tarjeta de Crédito/Débito                   │
  │                                                        │
  │  ✓ Pago seguro procesado por Wompi                    │
  │  ✓ Aceptamos Visa, Mastercard, American Express       │
  │  ✓ Confirmación inmediata de tu pago                  │
  │  ✓ Monto total a pagar: $150,000 COP                  │
  │                                                        │
  │  ┌────────────────────────────────────────────────┐   │
  │  │   🔒  Proceder al Pago Seguro                  │   │ ◄── Button Click
  │  └────────────────────────────────────────────────┘   │
  └────────────────────────────────────────────────────────┘

           │
           ▼
  handleProceedToWompiPayment() triggered
           │
           ▼

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Order Creation (Backend API Call)                               │
└─────────────────────────────────────────────────────────────────────────┘

  Frontend → Backend API

  POST /api/v1/orders
  ┌──────────────────────────────────────────────┐
  │ {                                            │
  │   "items": [                                 │
  │     {                                        │
  │       "product_id": "abc123",                │
  │       "quantity": 2,                         │
  │       "price": 50000                         │
  │     }                                        │
  │   ],                                         │
  │   "shipping_name": "Juan Pérez",             │
  │   "shipping_phone": "3001234567",            │
  │   "shipping_address": "Calle 123 #45-67",    │
  │   "shipping_city": "Bogotá",                 │
  │   "shipping_state": "Cundinamarca",          │
  │   "shipping_postal_code": "110111",          │
  │   "notes": "Entregar después de las 2pm"     │
  │ }                                            │
  └──────────────────────────────────────────────┘

           │
           ▼
  Backend validates and creates order
           │
           ▼

  Response:
  ┌──────────────────────────────────────────────┐
  │ {                                            │
  │   "id": 12345,                               │
  │   "order_number": "ORDER-12345-1696204800",  │
  │   "status": "pending",                       │
  │   "total": 150000,                           │
  │   "created_at": "2025-10-01T10:30:00Z"       │
  │ }                                            │
  └──────────────────────────────────────────────┘

           │
           ▼
  setOrderId(12345)
  setOrderReference("ORDER-12345-1696204800")
  setShowWompiWidget(true)
           │
           ▼

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 4: Wompi Widget Initialization                                     │
└─────────────────────────────────────────────────────────────────────────┘

  WompiCheckout Component Renders:

  useEffect(() => {
    // Wait for window.WidgetCheckout to be available
    const checkWidget = setInterval(() => {
      if (window.WidgetCheckout) {
        clearInterval(checkWidget);
        initializeWidget();
      }
    }, 100);
  }, []);

           │
           ▼

  initializeWidget():
  ┌──────────────────────────────────────────────┐
  │ const widget = new window.WidgetCheckout({   │
  │   currency: "COP",                           │
  │   amountInCents: 15000000,  // $150k * 100   │
  │   reference: "ORDER-12345-1696204800",       │
  │   publicKey: "pub_test_...",                 │
  │   redirectUrl: "/checkout/confirmation",     │
  │   customerData: {                            │
  │     email: "juan@example.com"                │
  │   }                                          │
  │ });                                          │
  │                                              │
  │ widget.open((result) => {                    │
  │   // Handle payment result                   │
  │ });                                          │
  └──────────────────────────────────────────────┘

           │
           ▼

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 5: Wompi Widget Modal (User Interaction)                           │
└─────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────┐
  │  ╔══════════════════════════════════════════════════╗  │
  │  ║  Wompi - Pago Seguro                             ║  │
  │  ╠══════════════════════════════════════════════════╣  │
  │  ║                                                  ║  │
  │  ║  Monto: $150,000 COP                             ║  │
  │  ║  Referencia: ORDER-12345-1696204800              ║  │
  │  ║                                                  ║  │
  │  ║  Número de Tarjeta:                              ║  │
  │  ║  ┌──────────────────────────────────────────┐   ║  │
  │  ║  │ 4242 4242 4242 4242                      │   ║  │ ◄── User Enters
  │  ║  └──────────────────────────────────────────┘   ║  │
  │  ║                                                  ║  │
  │  ║  Vencimiento:        CVV:                        ║  │
  │  ║  ┌─────┐  ┌─────┐  ┌────────┐                   ║  │
  │  ║  │ 12  │  │2025 │  │  123   │                   ║  │
  │  ║  └─────┘  └─────┘  └────────┘                   ║  │
  │  ║                                                  ║  │
  │  ║  Nombre del Titular:                             ║  │
  │  ║  ┌──────────────────────────────────────────┐   ║  │
  │  ║  │ JUAN PEREZ                               │   ║  │
  │  ║  └──────────────────────────────────────────┘   ║  │
  │  ║                                                  ║  │
  │  ║  ┌────────────────────────────────────────┐     ║  │
  │  ║  │   Pagar $150,000 COP                   │     ║  │ ◄── User Clicks
  │  ║  └────────────────────────────────────────┘     ║  │
  │  ║                                                  ║  │
  │  ╚══════════════════════════════════════════════════╝  │
  └────────────────────────────────────────────────────────┘

           │
           ▼
  Wompi processes payment
           │
           ▼

┌─────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Payment Processing (Wompi Backend)                              │
└─────────────────────────────────────────────────────────────────────────┘

  Wompi → Payment Processor (Visa/Mastercard/etc)

  ┌────────────────────────────────────────┐
  │  1. Validate card                      │
  │  2. Check funds                        │
  │  3. Apply 3D Secure if required        │
  │  4. Charge amount                      │
  │  5. Generate transaction ID            │
  └────────────────────────────────────────┘

           │
           ▼
  Transaction Result Generated
           │
           ├─────────────────┬──────────────────┬──────────────────┐
           │                 │                  │                  │
           ▼                 ▼                  ▼                  ▼
       APPROVED           PENDING           DECLINED            VOIDED
   (Success Path)    (Bank Processing)   (Error Path)      (User Canceled)


═══════════════════════════════════════════════════════════════════════════
                         PAYMENT RESULT HANDLING
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO A: Payment APPROVED                                            │
└─────────────────────────────────────────────────────────────────────────┘

  widget.open((result) => {
    if (result.transaction.status === 'APPROVED') {
      handlePaymentSuccess(result.transaction);
    }
  });

  handlePaymentSuccess():
  ┌──────────────────────────────────────────────┐
  │ 1. Save payment info to checkout store      │
  │    - method: 'credit_card'                   │
  │    - transaction_id: "txn_abc123"            │
  │    - status: 'approved'                      │
  │                                              │
  │ 2. Clear cart items                          │
  │    clearCart()                               │
  │                                              │
  │ 3. Redirect to confirmation                  │
  │    navigate('/checkout/confirmation')        │
  └──────────────────────────────────────────────┘

           │
           ▼

  Meanwhile, Wompi sends webhook to backend:
  POST /api/v1/webhooks/wompi
  ┌──────────────────────────────────────────────┐
  │ {                                            │
  │   "event": "transaction.updated",            │
  │   "data": {                                  │
  │     "transaction": {                         │
  │       "id": "txn_abc123",                    │
  │       "reference": "ORDER-12345-...",        │
  │       "status": "APPROVED",                  │
  │       "amount_in_cents": 15000000,           │
  │       "payment_method_type": "CARD"          │
  │     }                                        │
  │   },                                         │
  │   "signature": {                             │
  │     "checksum": "..."                        │
  │   }                                          │
  │ }                                            │
  └──────────────────────────────────────────────┘

           │
           ▼
  Backend validates signature
           │
           ▼
  Backend updates order status:
  ┌──────────────────────────────────────────────┐
  │ UPDATE orders                                │
  │ SET status = 'paid',                         │
  │     transaction_id = 'txn_abc123',           │
  │     paid_at = NOW()                          │
  │ WHERE order_number = 'ORDER-12345-...'       │
  └──────────────────────────────────────────────┘

           │
           ▼
  Order marked as PAID ✅

┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO B: Payment PENDING                                             │
└─────────────────────────────────────────────────────────────────────────┘

  Some payment methods (like PSE) require user to complete
  payment in their bank's website.

  widget.open((result) => {
    if (result.transaction.status === 'PENDING') {
      // Redirect to confirmation with pending status
      window.location.href = redirectUrl;
    }
  });

  User sees:
  ┌────────────────────────────────────────────────┐
  │  ⏳  Pago Pendiente                            │
  │                                                │
  │  Tu pago está siendo procesado.                │
  │  Te notificaremos cuando sea confirmado.       │
  │                                                │
  │  Número de orden: ORDER-12345-...              │
  │  Estado: PENDIENTE                             │
  └────────────────────────────────────────────────┘

  Backend webhook will update when payment completes.

┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO C: Payment DECLINED                                            │
└─────────────────────────────────────────────────────────────────────────┘

  widget.open((result) => {
    if (result.transaction.status === 'DECLINED') {
      handlePaymentError(result.transaction.status_message);
    }
  });

  handlePaymentError():
  ┌────────────────────────────────────────────────┐
  │ 1. Show error message to user                  │
  │    "Pago rechazado: Fondos insuficientes"      │
  │                                                │
  │ 2. Hide Wompi widget                           │
  │    setShowWompiWidget(false)                   │
  │                                                │
  │ 3. User can try another payment method         │
  └────────────────────────────────────────────────┘

  User sees:
  ┌────────────────────────────────────────────────┐
  │  ❌  Pago Rechazado                            │
  │                                                │
  │  Fondos insuficientes.                         │
  │  Por favor intenta con otro método de pago.    │
  │                                                │
  │  [Volver a Métodos de Pago]                    │
  └────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ SCENARIO D: Payment VOIDED (User Canceled)                              │
└─────────────────────────────────────────────────────────────────────────┘

  User closes widget without completing payment.

  widget.open((result) => {
    if (!result.transaction) {
      handlePaymentClose();
    }
  });

  handlePaymentClose():
  ┌────────────────────────────────────────────────┐
  │ 1. Hide Wompi widget                           │
  │    setShowWompiWidget(false)                   │
  │                                                │
  │ 2. No error shown (intentional close)          │
  │                                                │
  │ 3. User returns to payment method selection    │
  └────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          SYSTEM ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                           Component Hierarchy                            │
└─────────────────────────────────────────────────────────────────────────┘

CheckoutPage.tsx
  │
  └── CheckoutFlow.tsx
       │
       ├── CheckoutProgress.tsx (Step indicator)
       │
       ├── CheckoutSummary.tsx (Sidebar)
       │    └── Order totals, items, shipping info
       │
       └── Steps:
            │
            ├── CartStep.tsx
            │    └── Cart items, quantities, remove
            │
            ├── ShippingStep.tsx
            │    └── AddressForm.tsx
            │         └── Name, address, phone, city
            │
            ├── PaymentStep.tsx ◄────────── WE MODIFIED THIS
            │    │
            │    ├── Payment method selection
            │    │
            │    ├── PSEForm.tsx
            │    │    └── Bank selection, ID
            │    │
            │    ├── WompiCheckout.tsx ◄────── INTEGRATION POINT
            │    │    └── Widget initialization
            │    │
            │    ├── CreditCardForm.tsx (legacy, not used)
            │    │
            │    └── Bank transfer / Cash instructions
            │
            └── ConfirmationStep.tsx
                 └── Order details, tracking

┌─────────────────────────────────────────────────────────────────────────┐
│                          State Management Flow                           │
└─────────────────────────────────────────────────────────────────────────┘

useCheckoutStore (Zustand)
  ┌─────────────────────────────────────────────┐
  │  State:                                     │
  │  - cart_items: CartItem[]                   │
  │  - shipping_address: ShippingAddress        │
  │  - payment_info: PaymentInfo                │
  │  - order_id: string                         │
  │  - current_step: 'cart' | 'shipping' | ...  │
  │  - is_processing: boolean                   │
  │  - error: string | null                     │
  │                                             │
  │  Actions:                                   │
  │  - addItem()                                │
  │  - clearCart()                              │
  │  - setShippingAddress()                     │
  │  - setPaymentInfo()                         │
  │  - setOrderId()                             │
  │  - goToNextStep()                           │
  │  - setProcessing()                          │
  │  - setError()                               │
  └─────────────────────────────────────────────┘

useAuthStore
  ┌─────────────────────────────────────────────┐
  │  State:                                     │
  │  - user: { email, name, ... }               │
  │  - isAuthenticated: boolean                 │
  │                                             │
  │  Used for:                                  │
  │  - Customer email in Wompi widget           │
  │  - Order customer association               │
  └─────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                          API Communication                               │
└─────────────────────────────────────────────────────────────────────────┘

Frontend ◄───────────────────────────────────────────────► Backend
   │                                                            │
   │  1. GET /api/v1/payments/methods                          │
   │  ──────────────────────────────────────────────────────▶  │
   │  ◄────────────────────────────────────────────────────────│
   │     { card_enabled, pse_enabled, wompi_public_key }       │
   │                                                            │
   │  2. POST /api/v1/orders                                   │
   │  ──────────────────────────────────────────────────────▶  │
   │     { items, shipping_info, notes }                       │
   │  ◄────────────────────────────────────────────────────────│
   │     { id, order_number, status: "pending" }               │
   │                                                            │
   └────────────────────────────────────────────────────────────┘
                            │
                            │
                            ▼
                        Wompi API
                            │
                            │  POST /api/v1/webhooks/wompi
                            │  ─────────────────────────────────▶
                            │     { transaction, signature }
                            │
                      Backend updates order


═══════════════════════════════════════════════════════════════════════════
                          SECURITY ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────┐
│                     Data Flow & Security Layers                          │
└─────────────────────────────────────────────────────────────────────────┘

  USER                    FRONTEND              WOMPI             BACKEND
   │                         │                    │                  │
   │  1. Enter card data     │                    │                  │
   │  ───────────────────▶   │                    │                  │
   │                         │                    │                  │
   │                         │  2. Send to Wompi  │                  │
   │                         │   (HTTPS/TLS)      │                  │
   │                         │  ────────────────▶ │                  │
   │                         │                    │                  │
   │                         │                    │ 3. Process       │
   │                         │                    │    payment       │
   │                         │                    │    (PCI-DSS)     │
   │                         │                    │                  │
   │                         │  4. Transaction    │                  │
   │                         │     result         │                  │
   │                         │  ◄──────────────── │                  │
   │                         │                    │                  │
   │                         │                    │  5. Webhook      │
   │                         │                    │     (Signed)     │
   │                         │                    │  ──────────────▶ │
   │                         │                    │                  │
   │                         │                    │                  │ 6. Validate
   │                         │                    │                  │    signature
   │                         │                    │                  │
   │                         │                    │                  │ 7. Update
   │                         │                    │                  │    order
   │  8. Confirmation        │                    │                  │
   │  ◄──────────────────────│                    │                  │
   │                         │                    │                  │

Security Guarantees:
┌─────────────────────────────────────────────┐
│ ✓ Card data NEVER touches our servers       │
│ ✓ All communication over HTTPS/TLS          │
│ ✓ Wompi is PCI-DSS Level 1 compliant        │
│ ✓ Webhook signatures validated              │
│ ✓ Transaction IDs are unique                │
│ ✓ Amount verification on backend            │
│ ✓ User authentication required              │
│ ✓ CSRF protection enabled                   │
└─────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          DEVELOPMENT TIMELINE
═══════════════════════════════════════════════════════════════════════════

Date: 2025-10-01
Agent: react-specialist-ai

Tasks Completed:
┌─────────────────────────────────────────────┐
│ ✅ Analyzed existing PaymentStep structure  │
│ ✅ Enhanced PaymentStep UI/UX               │
│ ✅ Integrated WompiCheckout component       │
│ ✅ Added order creation flow                │
│ ✅ Implemented result handlers              │
│ ✅ Verified Wompi script loading            │
│ ✅ Added user email from auth context       │
│ ✅ Created comprehensive documentation      │
└─────────────────────────────────────────────┘

Files Modified:
┌──────────────────────────────────────────────────────────────────┐
│ /frontend/src/components/checkout/steps/PaymentStep.tsx         │
│   - Added useAuthStore import                                    │
│   - Enhanced credit card payment UI                              │
│   - Integrated WompiCheckout component                           │
│   - Improved error handling                                      │
│   - Added loading states                                         │
└──────────────────────────────────────────────────────────────────┘

Files Already Existing (Not Modified):
┌──────────────────────────────────────────────────────────────────┐
│ /frontend/src/components/checkout/WompiCheckout.tsx (320 lines) │
│ /frontend/src/stores/checkoutStore.ts (Complete state mgmt)     │
│ /frontend/index.html (Wompi script already loaded)              │
│ Backend payment endpoints (Already implemented)                  │
└──────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                               END OF DIAGRAM
═══════════════════════════════════════════════════════════════════════════
