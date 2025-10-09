"""
Regression Test Suite

Purpose:
--------
Tests that prevent historical bugs from reappearing.
Each test documents a specific fix and validates it stays working.

Test Organization:
------------------
- test_orders_stock_fix.py: Orders endpoint stock calculation (commit 5f263687)

Running Regression Tests:
-------------------------
```bash
# Run all regression tests
python -m pytest tests/regression/ -v -m regression

# Run specific regression suite
python -m pytest tests/regression/test_orders_stock_fix.py -v

# Run with coverage
python -m pytest tests/regression/ --cov=app/api/v1/endpoints/orders --cov-report=term
```

Test Markers:
-------------
- @pytest.mark.regression: All regression tests
- @pytest.mark.orders: Order-related functionality
- @pytest.mark.async_safety: Async/await pattern safety

When to Add Regression Tests:
------------------------------
1. After fixing production bugs
2. After applying emergency hotfixes
3. For critical business logic
4. When fixing async/concurrency issues
"""

__version__ = "1.0.0"
__test_type__ = "regression"
