# MESTORE API ARCHITECTURE DIAGRAM
**Visual Overview of Backend API Structure**

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MESTORE BACKEND API                         │
│                        FastAPI + SQLAlchemy                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  • React Frontend (port 5173)                                       │
│  • Mobile App (future)                                              │
│  • External Integrations                                            │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│  • CORS Middleware                                                  │
│  • JWT Authentication                                               │
│  • Rate Limiting (TODO)                                             │
│  • Request Validation                                               │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        ENDPOINT LAYER (42+)                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │   PRODUCTS    │  │    ORDERS     │  │   PAYMENTS    │          │
│  │  (12 endpoints)  │  (4 endpoints)│  │ (14 endpoints)│          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │     AUTH      │  │    VENDORS    │  │     CART      │          │
│  │ (12 endpoints)│  │  (1 endpoint) │  │  (0 endpoints)│          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      VALIDATION LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  • Pydantic Schemas (33 schemas)                                    │
│  • Business Rule Validation                                         │
│  • UUID Normalization                                               │
│  • File Upload Validation                                           │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      BUSINESS LOGIC LAYER                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │   AuthService       │  │  PaymentService     │                  │
│  │   - Login/Register  │  │  - Multi-gateway    │                  │
│  │   - OTP Verification│  │  - Wompi/PayU/Efecty│                  │
│  │   - Brute Force Prot│  │  - Fraud Detection  │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │  ProductService     │  │  OrderStateService  │                  │
│  │  - CRUD Operations  │  │  - Workflow Management                 │
│  │  - Semantic Search  │  │  - Status Transitions                  │
│  │  - Image Processing │  │  - Commission Calc  │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
│  ┌─────────────────────┐  ┌─────────────────────┐                  │
│  │  VendorService      │  │  EmailService       │                  │
│  │  - Registration     │  │  - OTP Emails       │                  │
│  │  - Auto-approval    │  │  - Notifications    │                  │
│  └─────────────────────┘  └─────────────────────┘                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       DATA ACCESS LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│  • SQLAlchemy ORM (Async)                                           │
│  • Repository Pattern                                               │
│  • Transaction Management                                           │
│  • Connection Pooling                                               │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         DATABASE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │   PostgreSQL  │  │     Redis     │  │   ChromaDB    │          │
│  │   - Products  │  │   - Sessions  │  │  - Embeddings │          │
│  │   - Orders    │  │   - Cache     │  │  - Semantic   │          │
│  │   - Payments  │  │   - Rate Limit│  │    Search     │          │
│  │   - Users     │  │               │  │               │          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL INTEGRATIONS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │     Wompi     │  │     PayU      │  │    Efecty     │          │
│  │   Gateway     │  │   Gateway     │  │   Cash Pymnt  │          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
│                                                                     │
│  ┌───────────────┐  ┌───────────────┐                              │
│  │  Email (SMTP) │  │   SMS Service │                              │
│  │   Delivery    │  │   (Twilio)    │                              │
│  └───────────────┘  └───────────────┘                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 REQUEST FLOW DIAGRAM

### Example: Create Order with Payment

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ 1. POST /api/v1/orders/
     │    Body: { items, shipping_info }
     │    Headers: { Authorization: Bearer <JWT> }
     ↓
┌─────────────────┐
│ Auth Middleware │  ← Validate JWT, extract user
└────┬────────────┘
     │
     │ 2. user_id extracted
     ↓
┌──────────────────┐
│ Orders Endpoint  │  ← Validate request schema (Pydantic)
└────┬─────────────┘
     │
     │ 3. Validated order data
     ↓
┌─────────────────┐
│ Stock Validation│  ← Check product.get_stock_disponible()
└────┬────────────┘
     │
     │ 4. Stock sufficient
     ↓
┌─────────────────┐
│ Calculate Totals│  ← subtotal + IVA(19%) + shipping
└────┬────────────┘
     │
     │ 5. total_amount = 250,000 COP
     ↓
┌─────────────────┐
│ Create Order DB │  ← Order + OrderItems (atomic transaction)
└────┬────────────┘
     │
     │ 6. order_id = 123
     ↓
┌──────────────┐
│ Return Order │  ← 201 Created + order details
└────┬─────────┘
     │
     │ 7. Client receives order_id
     ↓
┌─────────────────────┐
│ Client initiates    │
│ payment flow        │
└────┬────────────────┘
     │
     │ 8. POST /api/v1/payments/process
     │    Body: { order_id: 123, payment_method: "PSE", ... }
     ↓
┌─────────────────────┐
│ Payment Endpoint    │  ← Validate ownership (buyer_id == user_id)
└────┬────────────────┘
     │
     │ 9. Ownership validated
     ↓
┌─────────────────────┐
│ Integrated Payment  │  ← Fraud detection + Gateway selection
│ Service             │
└────┬────────────────┘
     │
     │ 10. fraud_score < threshold, gateway = Wompi
     ↓
┌─────────────────────┐
│ Wompi Gateway       │  ← Create PSE transaction
└────┬────────────────┘
     │
     │ 11. Redirect URL returned
     ↓
┌─────────────────────┐
│ Return Payment URL  │  ← 200 OK + { payment_url, transaction_id }
└────┬────────────────┘
     │
     │ 12. Client redirects to bank
     ↓
┌─────────────────────┐
│ User completes PSE  │  ← Bank authorization
│ on bank website     │
└────┬────────────────┘
     │
     │ 13. Bank approves payment
     ↓
┌─────────────────────┐
│ Wompi Webhook       │  ← POST /api/v1/payments/webhook
└────┬────────────────┘
     │
     │ 14. { event: "transaction.updated", status: "APPROVED" }
     ↓
┌─────────────────────┐
│ Signature Validation│  ← Verify webhook authenticity
└────┬────────────────┘
     │
     │ 15. Signature valid
     ↓
┌─────────────────────┐
│ Update Order Status │  ← order.status = CONFIRMED
└────┬────────────────┘
     │
     │ 16. Commission calculation triggered
     ↓
┌─────────────────────┐
│ Commission Service  │  ← Create commission record for vendor
└────┬────────────────┘
     │
     │ 17. Commission: 5% of total
     ↓
┌─────────────────────┐
│ Email Notification  │  ← Send confirmation to buyer + vendor
└─────────────────────┘
```

---

## 🔐 AUTHENTICATION FLOW

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ 1. POST /api/v1/auth/login
     │    { email, password }
     ↓
┌──────────────────────┐
│ Brute Force Check    │  ← Check Redis for failed attempts
└────┬─────────────────┘
     │
     │ 2. < 5 failed attempts, proceed
     ↓
┌──────────────────────┐
│ Validate Credentials │  ← Hash password, compare with DB
└────┬─────────────────┘
     │
     │ 3. Password matches
     ↓
┌──────────────────────┐
│ Fetch User from DB   │  ← Get full user object
└────┬─────────────────┘
     │
     │ 4. User: { id, email, user_type: BUYER }
     ↓
┌──────────────────────┐
│ Create JWT Tokens    │  ← Access (1h) + Refresh (7d)
└────┬─────────────────┘
     │
     │ 5. Tokens signed with SECRET_KEY
     ↓
┌──────────────────────┐
│ Store Session Redis  │  ← session:{user_id} = { ip, user_agent }
└────┬─────────────────┘
     │
     │ 6. Session created
     ↓
┌──────────────────────┐
│ Return Tokens        │  ← 200 OK + { access_token, refresh_token }
└────┬─────────────────┘
     │
     │ 7. Client stores tokens
     ↓
┌──────────────────────┐
│ Subsequent Requests  │  ← Authorization: Bearer <access_token>
└────┬─────────────────┘
     │
     │ 8. Middleware extracts token
     ↓
┌──────────────────────┐
│ Decode JWT           │  ← Verify signature, check expiration
└────┬─────────────────┘
     │
     │ 9. Token valid, extract user_id
     ↓
┌──────────────────────┐
│ Fetch User from DB   │  ← Ensure user still exists
└────┬─────────────────┘
     │
     │ 10. User object injected into endpoint
     ↓
┌──────────────────────┐
│ Endpoint Executes    │  ← current_user available
└──────────────────────┘
```

---

## 💳 PAYMENT GATEWAY INTEGRATION

```
┌─────────────────────────────────────────────────────────────────┐
│                 INTEGRATED PAYMENT SERVICE                      │
│                  (Multi-Gateway Orchestrator)                   │
└────┬────────────────────────────┬─────────────────┬────────────┘
     │                            │                 │
     │ Card Payment               │ PSE Payment     │ Cash Payment
     ↓                            ↓                 ↓
┌─────────────┐            ┌─────────────┐   ┌─────────────┐
│   Wompi     │            │    PayU     │   │   Efecty    │
│   Service   │            │   Service   │   │   Service   │
└────┬────────┘            └────┬────────┘   └────┬────────┘
     │                          │                 │
     │ POST /transactions       │ POST /payments  │ Generate Code
     ↓                          ↓                 ↓
┌─────────────┐            ┌─────────────┐   ┌─────────────┐
│   Wompi     │            │    PayU     │   │   Efecty    │
│   Gateway   │            │   Gateway   │   │  20k Points │
└────┬────────┘            └────┬────────┘   └────┬────────┘
     │                          │                 │
     │ Response                 │ Response        │ Code
     ↓                          ↓                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Payment Response                        │
│  { transaction_id, status, payment_url, fraud_score }           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 DATABASE SCHEMA (Simplified)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    users    │         │  products   │         │   orders    │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ id (UUID)   │◄────┐   │ id (UUID)   │         │ id (INT)    │
│ email       │     │   │ sku         │         │ order_number│
│ password    │     │   │ name        │◄────┐   │ buyer_id    │──┐
│ user_type   │     │   │ precio_venta│     │   │ total_amount│  │
│ phone       │     │   │ vendedor_id │─────┘   │ status      │  │
│ email_verif │     │   │ status      │         │ created_at  │  │
│ phone_verif │     │   │ stock       │         └─────────────┘  │
└─────────────┘     │   │ created_at  │                          │
                    │   └─────────────┘                          │
                    │                                            │
                    │   ┌─────────────┐         ┌─────────────┐ │
                    │   │ order_items │         │  payments   │ │
                    │   ├─────────────┤         ├─────────────┤ │
                    │   │ id          │         │ id          │ │
                    └───│ order_id    │         │ order_id    │─┘
                        │ product_id  │───┐     │ amount      │
                        │ quantity    │   │     │ status      │
                        │ unit_price  │   │     │ gateway     │
                        │ total_price │   │     │ wompi_id    │
                        └─────────────┘   │     └─────────────┘
                                          │
                        ┌─────────────┐   │
                        │ commissions │   │
                        ├─────────────┤   │
                        │ id          │   │
                        │ order_id    │───┘
                        │ vendor_id   │
                        │ amount      │
                        │ status      │
                        │ created_at  │
                        └─────────────┘
```

---

## 🔄 DATA FLOW PATTERNS

### 1. **Read Pattern** (Get Products)
```
Client → Endpoint → Validation → Service → Repository → Database
                                                            ↓
Client ← Response ← Serialization ← DTO ← Model ← Query Result
```

### 2. **Write Pattern** (Create Order)
```
Client → Endpoint → Validation → Service → Transaction Start
                                                    ↓
                            Database ← Create Order
                            Database ← Create OrderItems
                            Database ← Reserve Stock
                                                    ↓
                                            Transaction Commit
                                                    ↓
Client ← Response ← Serialization ← Created Order
```

### 3. **Background Task Pattern** (Send Email)
```
Endpoint → Background Task Queue → Email Service → SMTP Server
                                                        ↓
                                                   Email Sent
                                                        ↓
                                                Log Success
```

---

## 🎯 KEY ARCHITECTURAL DECISIONS

### ✅ **What We Did Right**

1. **Async/Await**: All I/O operations async for scalability
2. **Service Layer**: Business logic separated from endpoints
3. **Transaction Management**: Atomic operations for critical flows
4. **Multi-Gateway**: Payment gateway abstraction layer
5. **Soft Delete**: Data preservation (deleted_at)
6. **UUID for Products**: Better scalability + security
7. **Decimal for Money**: Precise financial calculations
8. **Enum for Status**: Type safety for state machines
9. **Relationships**: Proper ORM relationships with cascade
10. **Validation**: Pydantic at entry point

### ⚠️ **What Needs Improvement**

1. **Rate Limiting**: Missing global API rate limiting
2. **Caching**: No Redis caching for hot data
3. **Circuit Breaker**: No fallback for gateway failures
4. **API Docs**: Missing comprehensive OpenAPI examples
5. **Monitoring**: No Sentry/CloudWatch integration yet

---

**Generated**: 2025-10-03
**Architecture**: FastAPI + PostgreSQL + Redis + ChromaDB
**Status**: Production-Ready for MVP
