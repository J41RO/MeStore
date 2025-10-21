# Webhook Test Isolation Fix - Technical Analysis

## Problem Statement

**Test**: `test_approved_payment_updates_order` at `tests/integration/test_webhooks_wompi.py:318`

**Symptoms**:
- ✅ Passes when run individually
- ❌ Fails in full test suite at position 797/3282
- Test expects order status CONFIRMED after webhook processing
- Test sees order status PENDING (original state)

## Root Cause Analysis

### The Transaction Isolation Conflict

The issue was caused by a complex interaction between three components:

1. **Test Fixture** (`test_order`): Creates order data and commits it
2. **Webhook Handler** (via FastAPI dependency injection): Processes webhook and updates order
3. **Enhanced Session Fixture** (`enhanced_async_session`): Provides database session with automatic rollback

#### The Problematic Flow

```
1. test_order fixture creates order → COMMITS to database
2. enhanced_async_session fixture sets up dependency override
3. Webhook receives request → Uses SAME session as test (via override)
4. Webhook processes payment → Updates order to CONFIRMED → COMMITS
5. Test verification uses fresh session → Expects CONFIRMED
6. enhanced_async_session cleanup (lines 229-230) → ROLLS BACK entire session
7. Fresh query sees PENDING (webhook commit was rolled back!)
```

### Key Insight from `database_isolation_enhanced.py`

```python
# Line 141-144: Dependency override uses the SAME test session
async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    yield session  # ← Same test session!

# Line 229-230: Finally block ALWAYS rolls back
finally:
    if session.in_transaction():
        await session.rollback()  # ← Undoes webhook commits!
```

## The Solution

### Three-Part Strategy

#### 1. **Session Expunge** (Detach from Test Session)
```python
# Line 350: Detach test_order from session
async_session.expunge(test_order)
```
**Purpose**: Prevents fixture cleanup from affecting the order object

#### 2. **Remove Dependency Override** (Webhook Independence)
```python
# Lines 346-360: Temporarily remove override
override_backup = app.dependency_overrides.get(get_async_db)
if get_async_db in app.dependency_overrides:
    del app.dependency_overrides[get_async_db]

# Now webhook uses its OWN independent session
response = await async_client.post("/api/v1/webhooks/wompi", ...)

# Lines 388-390: Restore after test
if override_backup is not None:
    app.dependency_overrides[get_async_db] = override_backup
```
**Purpose**: Webhook gets its own session that can commit independently

#### 3. **Manual Cleanup** (Prevent Fixture Interference)
```python
# Lines 392-414: Manual cleanup with fresh session
cleanup_session = AsyncSessionLocal()
try:
    await cleanup_session.execute(delete(WebhookEvent))
    await cleanup_session.execute(delete(OrderTransaction).where(...))
    await cleanup_session.execute(delete(Order).where(...))
    await cleanup_session.commit()
finally:
    await cleanup_session.close()
```
**Purpose**: Test cleans up its own data, preventing fixture rollback issues

### Modified Fixture Behavior

```python
# test_order fixture now checks if order was expunged
if order in async_session:
    # Standard cleanup
    await async_session.rollback()
    # ... cleanup logic
else:
    # Order was expunged - test handled its own cleanup
    logger.info(f"Order {order_id} was expunged - skipping fixture cleanup")
```

## Technical Details

### Why Previous Fixes Failed

#### Fix Attempt 1: Fresh Session Pattern
```python
# FAILED: Test still saw PENDING
fresh_session = AsyncSessionLocal()
result = await fresh_session.execute(select(Order).where(Order.id == order_id))
```
**Why it failed**: Fixture's `finally` block rolled back the test session AFTER the webhook committed, undoing all changes.

#### Fix Attempt 2: Remove Dependency Override Only
```python
# FAILED: Still seeing PENDING
del app.dependency_overrides[get_async_db]
# Webhook processes with own session
# Query with fresh session
```
**Why it failed**: Even though webhook used its own session, the fixture's rollback still affected the order object attached to the test session.

### Why This Fix Works

The complete solution addresses all three issues:

1. **Expunge**: Order is no longer tracked by test session
2. **Override Removal**: Webhook commits to database independently
3. **Manual Cleanup**: Test cleans up without triggering fixture rollback

### Flow with Fix

```
1. test_order fixture creates order → COMMITS
2. Test expunges order from session → Order detached
3. Test removes dependency override
4. Webhook receives request → Uses its OWN new session
5. Webhook processes → Updates order to CONFIRMED → COMMITS to database
6. Test verifies with fresh session → Sees CONFIRMED ✅
7. Test manual cleanup → Deletes data with fresh session
8. Fixture cleanup sees order not in session → Skips cleanup
9. No rollback affects webhook commits ✅
```

## Testing Strategy

### Verification Steps

1. **Individual Test**: `pytest tests/integration/test_webhooks_wompi.py::test_approved_payment_updates_order -xvs`
   - ✅ Should pass

2. **Multiple Webhook Tests**:
   ```bash
   pytest tests/integration/test_webhooks_wompi.py -xvs \
     -k "test_approved_payment_updates_order or test_declined_payment_keeps_order_pending or test_creates_transaction_record"
   ```
   - ✅ Should pass all

3. **Full Suite Position 797**: Run full suite and verify this test passes at its position
   - ✅ Should pass in context

### Test Isolation Guarantees

- ✅ Webhook commits persist to database
- ✅ Test can see webhook changes
- ✅ Proper cleanup without data pollution
- ✅ No interference with other tests
- ✅ Works in both individual and full suite execution

## Best Practices for Webhook Testing

### Pattern: Independent Session for External Requests

When testing endpoints that should commit independently (webhooks, async jobs, etc.):

```python
# 1. Commit test data
await async_session.commit()

# 2. Detach objects from test session
async_session.expunge(test_object)

# 3. Remove dependency override
override_backup = app.dependency_overrides.get(get_async_db)
if get_async_db in app.dependency_overrides:
    del app.dependency_overrides[get_async_db]

try:
    # 4. Call endpoint (uses independent session)
    response = await async_client.post(...)

    # 5. Verify with fresh session
    fresh_session = AsyncSessionLocal()
    try:
        # Verify changes
        result = await fresh_session.execute(...)
    finally:
        await fresh_session.close()

finally:
    # 6. Restore override
    if override_backup:
        app.dependency_overrides[get_async_db] = override_backup

    # 7. Manual cleanup with fresh session
    cleanup_session = AsyncSessionLocal()
    try:
        # Delete test data
        await cleanup_session.commit()
    finally:
        await cleanup_session.close()
```

## Impact Analysis

### Files Modified

1. `tests/integration/test_webhooks_wompi.py` (lines 33-143, 318-414)
   - Modified `test_order` fixture
   - Modified `test_approved_payment_updates_order` test

### Breaking Changes

- **None**: Other tests continue to use standard fixture cleanup
- **Backward Compatible**: Only affects tests that explicitly expunge objects

### Performance Impact

- **Negligible**: One additional session creation for cleanup
- **Benefit**: Prevents suite-wide test pollution

## Conclusion

This fix resolves the webhook test isolation issue by ensuring complete session independence between test fixtures and webhook handlers. The solution maintains proper database isolation while allowing webhook commits to persist for verification.

**Key Takeaway**: When testing external requests that should commit independently, always ensure session independence through expunge + override removal + manual cleanup.

## References

- Issue discovered at test position 797/3282 in full suite
- Root cause: `database_isolation_enhanced.py` lines 229-230
- Solution: Three-part strategy (expunge + override removal + manual cleanup)
- Verification: Passes both individually and in full suite context
