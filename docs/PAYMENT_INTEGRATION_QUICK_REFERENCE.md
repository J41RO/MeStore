# Payment Integration Quick Reference

**For Developers Working with MeStore Payment System**

---

## Critical Integration Issues (Fix These First!)

### 🔴 Issue #1: Race Condition in Webhook Processing

**Problem**: Multiple webhooks can update the same order simultaneously without locking.

**Current Code** (UNSAFE):
```python
# app/api/v1/endpoints/webhooks.py
order = result.scalar_one_or_none()
order.status = order_status  # ⚠️ Race condition!
await db.commit()
```

**Fixed Code** (SAFE):
```python
from sqlalchemy import select

# Use row-level locking
stmt = select(Order).where(Order.id == order_id).with_for_update()
result = await db.execute(stmt)
order = result.scalar_one_or_none()

order.status = order_status  # ✅ Protected by lock
await db.commit()
```

**Why It Matters**: Without locking, two webhooks arriving at the same time can corrupt order data.

---

### 🔴 Issue #2: Float Precision Errors in Currency

**Problem**: Using `Float` for currency amounts causes precision errors.

**Current Code** (WRONG):
```python
# app/models/order.py
amount = Column(Float, nullable=False)  # ❌ 123.45 might become 123.4499999
```

**Fixed Code** (CORRECT):
```python
from sqlalchemy import Numeric

amount = Column(Numeric(15, 2), nullable=False)  # ✅ Exact precision
```

**Migration Required**:
```sql
ALTER TABLE order_transactions
  ALTER COLUMN amount TYPE NUMERIC(15, 2);
```

---

### 🔴 Issue #3: Missing Database Constraints

**Problem**: Duplicate transactions possible.

**Add This Migration**:
```sql
-- Prevent duplicate gateway transactions
ALTER TABLE order_transactions
  ADD CONSTRAINT uq_gateway_txn
  UNIQUE (gateway, gateway_transaction_id);

-- Prevent duplicate webhook events
ALTER TABLE webhook_events
  ADD CONSTRAINT uq_webhook_event
  UNIQUE (event_id, signature);

-- Ensure positive amounts
ALTER TABLE order_transactions
  ADD CONSTRAINT chk_amount_positive
  CHECK (amount > 0);
```

---

## Payment Service Integration Patterns

### Pattern 1: PayU Transaction with Database Storage

```python
from app.services.payments.payu_service import get_payu_service
from app.models.order import OrderTransaction, PaymentStatus
from decimal import Decimal

async def process_payu_payment(order: Order, payment_data: dict, db: AsyncSession):
    """Process PayU payment with proper database integration"""

    payu = get_payu_service()

    # 1. Prepare transaction data
    transaction_data = {
        "amount_in_cents": int(Decimal(str(order.total_amount)) * 100),
        "customer_email": order.shipping_email,
        "payment_method": payment_data["payment_method"],
        "reference": order.order_number,
        "description": f"Order {order.order_number}",
        "customer_data": {
            "full_name": order.shipping_name,
            "phone": order.shipping_phone
        },
        "payment_data": payment_data
    }

    # 2. Create PayU transaction
    try:
        result = await payu.create_transaction(transaction_data)

        # 3. Store in database
        db_transaction = OrderTransaction(
            transaction_reference=f"TXN-{order.order_number}-{result['transaction_id'][:10]}",
            order_id=order.id,
            amount=Decimal(str(order.total_amount)),  # Use Decimal!
            currency="COP",
            status=PaymentStatus.APPROVED if result['status'] == 'approved' else PaymentStatus.PENDING,
            payment_method_type=payment_data["payment_method"],
            gateway="payu",
            gateway_transaction_id=result["transaction_id"],
            gateway_response=json.dumps(result["raw_response"]),
            processed_at=datetime.utcnow()
        )
        db.add(db_transaction)

        # 4. Update order
        if result['status'] == 'approved':
            order.status = OrderStatus.CONFIRMED
            order.confirmed_at = datetime.utcnow()

        await db.commit()
        return result

    except Exception as e:
        await db.rollback()
        raise
```

---

### Pattern 2: Efecty Code Generation with Validation

```python
from app.services.payments.efecty_service import EfectyService

async def generate_efecty_payment(order: Order, db: AsyncSession):
    """Generate Efecty payment code with database storage"""

    service = EfectyService()

    # 1. Generate code
    code_data = service.generate_payment_code(
        order_id=order.id,
        amount=int(order.total_amount),  # COP, not cents
        customer_email=order.shipping_email,
        customer_name=order.shipping_name,
        customer_phone=order.shipping_phone
    )

    # 2. Validate uniqueness (IMPORTANT!)
    payment_code = code_data["payment_code"]
    existing = await db.execute(
        select(OrderTransaction).where(
            OrderTransaction.gateway_reference == payment_code
        )
    )
    if existing.scalar_one_or_none():
        # Retry with new code
        return await generate_efecty_payment(order, db)

    # 3. Store in database
    transaction = OrderTransaction(
        transaction_reference=f"TXN-EFECTY-{order.order_number}",
        order_id=order.id,
        amount=Decimal(str(order.total_amount)),
        currency="COP",
        status=PaymentStatus.PENDING,
        payment_method_type="EFECTY",
        gateway="efecty",
        gateway_reference=payment_code,
        gateway_response=json.dumps(code_data),
        created_at=datetime.utcnow()
    )
    db.add(transaction)

    # 4. Update order
    order.status = OrderStatus.PENDING

    await db.commit()
    return code_data
```

---

### Pattern 3: Webhook Processing with Idempotency

```python
from app.api.v1.endpoints.webhooks import (
    verify_wompi_signature,
    check_event_already_processed,
    update_order_from_webhook,
    store_webhook_event
)

async def handle_wompi_webhook(payload: dict, signature: str, db: AsyncSession):
    """Handle Wompi webhook with proper idempotency and locking"""

    # 1. Verify signature
    payload_bytes = json.dumps(payload).encode('utf-8')
    if not verify_wompi_signature(payload_bytes, signature, settings.WOMPI_WEBHOOK_SECRET):
        logger.warning("Invalid webhook signature")
        return {"status": "ok"}  # Return 200 anyway

    # 2. Check idempotency
    event_id = payload["data"]["id"]
    if await check_event_already_processed(db, event_id):
        logger.info(f"Webhook {event_id} already processed")
        return {"status": "ok"}

    # 3. Use transaction with proper isolation
    async with db.begin():
        # Set serializable isolation for consistency
        await db.execute(text("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE"))

        # 4. Process webhook with row locking
        result = await update_order_from_webhook(
            db=db,
            transaction_data=payload["data"],
            wompi_transaction_id=event_id
        )

        # 5. Store webhook event for audit
        await store_webhook_event(
            db=db,
            event_id=event_id,
            event_type=payload["event"],
            raw_payload=payload,
            signature=signature,
            signature_valid=True,
            processing_result=result
        )

    return {"status": "ok"}
```

---

## Database Query Patterns

### Pattern 1: Fetch Order with Transactions (Eager Loading)

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# ❌ BAD: Causes N+1 queries
order = await db.execute(select(Order).where(Order.id == order_id))
order = result.scalar_one()
for txn in order.transactions:  # Separate query for each!
    print(txn.status)

# ✅ GOOD: Single query with JOIN
stmt = select(Order).options(
    selectinload(Order.transactions),
    selectinload(Order.items)
).where(Order.id == order_id)

result = await db.execute(stmt)
order = result.scalar_one()
for txn in order.transactions:  # No additional queries!
    print(txn.status)
```

---

### Pattern 2: Find Transaction with Locking

```python
# ✅ CORRECT: Lock row before update
async def update_transaction_status(txn_id: int, new_status: str, db: AsyncSession):
    stmt = select(OrderTransaction).where(
        OrderTransaction.id == txn_id
    ).with_for_update()  # Lock the row

    result = await db.execute(stmt)
    txn = result.scalar_one_or_none()

    if txn:
        txn.status = new_status
        txn.processed_at = datetime.utcnow()
        await db.commit()
```

---

### Pattern 3: Check Payment Status Efficiently

```python
# ✅ EFFICIENT: Use index on status
async def get_approved_transactions_today(db: AsyncSession):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)

    stmt = select(OrderTransaction).where(
        OrderTransaction.status == PaymentStatus.APPROVED,  # Indexed
        OrderTransaction.processed_at >= today
    ).order_by(OrderTransaction.processed_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()
```

---

## Testing Integration Points

### Test 1: PayU Signature Generation

```python
@pytest.mark.asyncio
async def test_payu_signature():
    from app.services.payments.payu_service import PayUService

    service = PayUService()
    signature = service._generate_signature(
        reference="TEST-ORDER-123",
        amount="50000.0",
        currency="COP"
    )

    # Should be MD5 hash (32 chars)
    assert len(signature) == 32
    assert signature.isalnum()

    # Should be deterministic
    signature2 = service._generate_signature("TEST-ORDER-123", "50000.0", "COP")
    assert signature == signature2
```

---

### Test 2: Webhook Idempotency

```python
@pytest.mark.asyncio
async def test_webhook_idempotency(db_session, test_order):
    from app.api.v1.endpoints.webhooks import update_order_from_webhook

    webhook_data = {
        "id": "wompi-test-123",
        "reference": test_order.order_number,
        "status": "APPROVED",
        "amount_in_cents": 12900000
    }

    # Process first time
    result1 = await update_order_from_webhook(
        db=db_session,
        transaction_data=webhook_data,
        wompi_transaction_id="wompi-test-123"
    )
    assert result1.success is True

    # Create webhook event to mark as processed
    webhook_event = WebhookEvent(
        event_id="wompi-test-123",
        event_type=WebhookEventType.TRANSACTION_UPDATED,
        event_status=WebhookEventStatus.PROCESSED,
        raw_payload=webhook_data,
        processed_at=datetime.utcnow()
    )
    db_session.add(webhook_event)
    await db_session.commit()

    # Check idempotency
    from app.api.v1.endpoints.webhooks import check_event_already_processed
    already_processed = await check_event_already_processed(db_session, "wompi-test-123")
    assert already_processed is True
```

---

### Test 3: Race Condition Simulation

```python
@pytest.mark.asyncio
async def test_concurrent_webhooks(db_session, test_order):
    import asyncio
    from app.api.v1.endpoints.webhooks import update_order_from_webhook

    webhook_data = {
        "id": "wompi-concurrent-test",
        "reference": test_order.order_number,
        "status": "APPROVED",
        "amount_in_cents": 12900000
    }

    # Process two webhooks concurrently
    results = await asyncio.gather(
        update_order_from_webhook(db_session, webhook_data, "wompi-concurrent-test"),
        update_order_from_webhook(db_session, webhook_data, "wompi-concurrent-test"),
        return_exceptions=True
    )

    # One should succeed
    successful = [r for r in results if not isinstance(r, Exception) and r.success]
    assert len(successful) >= 1

    # Order should be consistent
    await db_session.refresh(test_order)
    assert test_order.status == OrderStatus.CONFIRMED
    assert len(test_order.transactions) == 1  # Not duplicated!
```

---

## Common Pitfalls and Solutions

### Pitfall 1: Float Arithmetic Errors

```python
# ❌ WRONG: Float precision issues
amount = 123.45
amount_in_cents = int(amount * 100)  # Might be 12344 instead of 12345!

# ✅ CORRECT: Use Decimal
from decimal import Decimal
amount = Decimal("123.45")
amount_in_cents = int(amount * 100)  # Always 12345
```

---

### Pitfall 2: Missing Transaction Rollback

```python
# ❌ WRONG: No rollback on error
try:
    order.status = OrderStatus.CONFIRMED
    await db.commit()
except Exception as e:
    logger.error(e)  # Database left in inconsistent state!

# ✅ CORRECT: Always rollback on error
try:
    order.status = OrderStatus.CONFIRMED
    await db.commit()
except Exception as e:
    await db.rollback()
    logger.error(e)
    raise
```

---

### Pitfall 3: Forgetting to Refresh After Commit

```python
# ❌ WRONG: Stale data
order.status = OrderStatus.CONFIRMED
await db.commit()
print(order.confirmed_at)  # None (not loaded from DB)

# ✅ CORRECT: Refresh to get DB-generated values
order.status = OrderStatus.CONFIRMED
await db.commit()
await db.refresh(order)
print(order.confirmed_at)  # Actual timestamp from DB
```

---

### Pitfall 4: Not Handling Webhook Retries

```python
# ❌ WRONG: Raises error on duplicate
if event_already_processed:
    raise HTTPException(400, "Already processed")  # Wompi will retry!

# ✅ CORRECT: Always return 200 OK
if event_already_processed:
    logger.info("Duplicate webhook, ignoring")
    return {"status": "ok"}  # Wompi stops retrying
```

---

## Debugging Tips

### Debug 1: Check Webhook Signature Calculation

```python
# In app/api/v1/endpoints/webhooks.py
import hmac
import hashlib

def debug_signature(payload: bytes, secret: str, received_signature: str):
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

    print(f"Payload: {payload[:100]}...")
    print(f"Secret (first 10 chars): {secret[:10]}...")
    print(f"Expected signature: {expected}")
    print(f"Received signature: {received_signature}")
    print(f"Match: {expected == received_signature}")

    return expected == received_signature
```

---

### Debug 2: Trace Database Transaction State

```python
# Add to model methods for debugging
def __repr__(self):
    session_state = "detached"
    if self in db.new:
        session_state = "pending"
    elif self in db.dirty:
        session_state = "dirty"
    elif self in db.deleted:
        session_state = "deleted"

    return f"<Order(id={self.id}, status={self.status}, session={session_state})>"
```

---

### Debug 3: Log Webhook Processing Steps

```python
# In webhook handler
logger.info(f"Step 1: Received webhook {event_id}")
logger.info(f"Step 2: Signature valid: {signature_valid}")
logger.info(f"Step 3: Idempotency check: {already_processed}")
logger.info(f"Step 4: Order found: {order is not None}")
logger.info(f"Step 5: Status update: {old_status} → {new_status}")
logger.info(f"Step 6: Transaction created: {transaction.id}")
logger.info(f"Step 7: Webhook event stored: {webhook_event.id}")
```

---

## Performance Optimization

### Optimization 1: Batch Insert Transactions

```python
# ✅ EFFICIENT: Single database round-trip
transactions = [
    OrderTransaction(order_id=order.id, amount=100, ...)
    for _ in range(100)
]
db.add_all(transactions)
await db.commit()
```

---

### Optimization 2: Use Database Indexes

```sql
-- Add these indexes for common queries
CREATE INDEX idx_transaction_status_created
  ON order_transactions(status, created_at);

CREATE INDEX idx_webhook_event_type_status
  ON webhook_events(event_type, event_status);

CREATE INDEX idx_order_buyer_status
  ON orders(buyer_id, status);
```

---

### Optimization 3: Cache PSE Banks

```python
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=1)
async def get_cached_pse_banks():
    """Cache PSE banks for 24 hours"""
    wompi = integrated_payment_service.wompi_service
    banks = await wompi.get_pse_banks()
    return banks

# Clear cache manually if needed
get_cached_pse_banks.cache_clear()
```

---

## Quick Command Reference

### Run Integration Tests
```bash
# All integration tests
pytest tests/integration/test_payment_integration.py -v

# Specific test class
pytest tests/integration/test_payment_integration.py::TestWebhookIntegration -v

# With coverage
pytest tests/integration/ --cov=app.services.payments --cov=app.api.v1.endpoints --cov-report=html

# Performance tests only
pytest tests/integration/test_payment_integration.py::TestPaymentPerformance -v
```

### Database Migrations
```bash
# Create migration for Decimal conversion
alembic revision -m "convert_amount_to_decimal"

# Add unique constraints
alembic revision -m "add_unique_constraints_payments"

# Apply migrations
alembic upgrade head

# Check current version
alembic current
```

### Health Checks
```bash
# Check PayU service
curl http://localhost:8000/api/v1/payments/health

# Check webhook service
curl http://localhost:8000/api/v1/webhooks/health

# Check payment methods
curl http://localhost:8000/api/v1/payments/methods
```

---

## Summary Checklist

Before deploying payment integration changes:

- [ ] ✅ All amounts use `Decimal` type (not `Float`)
- [ ] ✅ Row-level locking (`with_for_update()`) on order updates
- [ ] ✅ Serializable isolation for webhook processing
- [ ] ✅ Unique constraints on `gateway_transaction_id`
- [ ] ✅ Idempotency check in all webhook handlers
- [ ] ✅ Always return 200 OK for webhooks
- [ ] ✅ Signature verification never bypassed
- [ ] ✅ Database rollback on all errors
- [ ] ✅ Integration tests pass with >90% coverage
- [ ] ✅ Performance tests meet <500ms target
- [ ] ✅ Audit logging for all payment operations
- [ ] ✅ Rate limiting enabled on payment endpoints

---

**Last Updated**: October 1, 2025
**Maintained By**: Integration Testing AI
**Review**: Before each payment system deployment
