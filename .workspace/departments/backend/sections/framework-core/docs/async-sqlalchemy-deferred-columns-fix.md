# Async SQLAlchemy Deferred Columns Fix

## Problem
The shipping endpoints were experiencing `MissingGreenlet` errors when accessing deferred columns in async context:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
Was IO attempted in an unexpected place?
```

## Root Cause
The Order model uses `deferred()` for shipping-related columns:
- `tracking_number`
- `courier`
- `estimated_delivery`
- `shipping_events`

When accessing these columns in an async context without explicitly loading them, SQLAlchemy attempts lazy loading, which triggers synchronous IO in an async context, causing the MissingGreenlet error.

## Solution Implemented

### 1. Endpoint Changes (`app/api/v1/endpoints/shipping.py`)

**Added `undefer()` to all query operations:**
```python
from sqlalchemy.orm import undefer

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
order = result.scalar_one_or_none()
```

**Used local variables to avoid post-commit attribute access:**
```python
# Store values before commit to avoid lazy loading
tracking_num = order.tracking_number

await db.commit()

# Use stored values instead of accessing order attributes
return {
    "tracking_number": tracking_num,
    "order_status": order_status.value
}
```

### 2. Test Changes (`tests/api/test_shipping_endpoints.py`)

**Added `undefer()` to all test queries:**
```python
from sqlalchemy.orm import undefer

result = await async_db_session.execute(
    select(Order)
    .where(Order.id == test_confirmed_order.id)
    .options(
        undefer(Order.tracking_number),
        undefer(Order.courier),
        undefer(Order.estimated_delivery),
        undefer(Order.shipping_events)
    )
)
order = result.scalar_one()
```

**Reload orders with deferred columns before accessing properties:**
```python
# Reload order with deferred columns to avoid lazy loading
result = await async_db_session.execute(
    select(Order)
    .where(Order.id == test_shipped_order.id)
    .options(
        undefer(Order.tracking_number),
        undefer(Order.courier),
        undefer(Order.estimated_delivery),
        undefer(Order.shipping_events)
    )
)
order = result.scalar_one()

# Now safe to access deferred properties
assert order.tracking_number is not None
```

## Key Patterns for Async SQLAlchemy with Deferred Columns

### Pattern 1: Query with Explicit Undefer
Always undefer columns you'll need to access:
```python
result = await db.execute(
    select(Model)
    .where(Model.id == id)
    .options(
        undefer(Model.deferred_col1),
        undefer(Model.deferred_col2)
    )
)
```

### Pattern 2: Store Before Commit
Store deferred values before commit if you'll need them in the response:
```python
value = model.deferred_column
await db.commit()
# Use 'value' instead of 'model.deferred_column'
```

### Pattern 3: Don't Rely on refresh()
After `await db.refresh(model)`, deferred columns are NOT automatically loaded. Either:
- Use stored variables (preferred for performance)
- Re-query with undefer()

## Testing Results
All 8 shipping endpoint tests now pass:
- ✅ test_generate_tracking_number
- ✅ test_assign_shipping_success
- ✅ test_assign_shipping_already_assigned
- ✅ test_update_shipping_location_success
- ✅ test_update_shipping_delivered
- ✅ test_get_shipping_tracking_authenticated
- ✅ test_get_shipping_tracking_forbidden
- ✅ test_track_by_tracking_number_public

## Performance Impact
- **Minimal**: `undefer()` adds explicit column loading to SELECT queries
- **Benefit**: Eliminates N+1 queries from lazy loading
- **Best Practice**: Explicitly loading required columns is better than lazy loading

## Files Modified
1. `/home/admin-jairo/MeStore/app/api/v1/endpoints/shipping.py`
   - Added import for `undefer`
   - Updated all 4 endpoints to use `undefer()` in queries
   - Used local variables to avoid post-commit attribute access

2. `/home/admin-jairo/MeStore/tests/api/test_shipping_endpoints.py`
   - Added `undefer()` to all test database queries
   - Reload orders with deferred columns before accessing properties

## Best Practices for Future Development

1. **Always use `undefer()`** when querying models with deferred columns in async context
2. **Store values before commit** if you'll need them in responses
3. **Don't trust `refresh()`** to load deferred columns
4. **Document deferred columns** in model docstrings
5. **Use explicit loading** over lazy loading in async code

## Related Documentation
- SQLAlchemy Async Documentation: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Deferred Column Loading: https://docs.sqlalchemy.org/en/20/orm/loading_columns.html#deferred-column-loading
- MissingGreenlet Error: https://sqlalche.me/e/20/xd2s
