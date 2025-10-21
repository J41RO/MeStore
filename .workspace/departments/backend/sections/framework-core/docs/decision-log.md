
## 2025-10-16: Fixed MissingGreenlet Error in Shipping Endpoints

**Issue**: Shipping endpoints experiencing `MissingGreenlet` errors when accessing Order model deferred columns in async context.

**Root Cause**: Order model uses `deferred()` for shipping columns (tracking_number, courier, estimated_delivery, shipping_events). Accessing these in async context triggered lazy loading, causing synchronous IO in async context.

**Solution**:
1. Added `undefer()` to all shipping endpoint queries to explicitly load deferred columns
2. Used local variables to store deferred values before commit/refresh
3. Updated tests to use `undefer()` when querying orders with deferred columns

**Files Modified**:
- `app/api/v1/endpoints/shipping.py` - Added `undefer()` to all 4 endpoints
- `tests/api/test_shipping_endpoints.py` - Fixed all 8 tests to properly handle deferred columns

**Pattern Established**:
```python
# Always undefer deferred columns in async queries
result = await db.execute(
    select(Order)
    .where(Order.id == order_id)
    .options(
        undefer(Order.tracking_number),
        undefer(Order.courier),
        undefer(Order.estimated_delivery),
        undefer(Order.shipping_events)
    )
)
```

**Test Results**: All 8 shipping endpoint tests passing
**Performance Impact**: Minimal - eliminates N+1 lazy loading queries
**Documentation**: Created comprehensive guide in `async-sqlalchemy-deferred-columns-fix.md`

**Key Learnings**:
- `db.refresh()` does NOT reload deferred columns
- Always use explicit `undefer()` for deferred columns in async context
- Store values before commit if needed in response
- Async SQLAlchemy requires deliberate eager loading strategy

**Decision**: Adopt `undefer()` pattern as standard practice for all async endpoints accessing deferred columns across the codebase.

