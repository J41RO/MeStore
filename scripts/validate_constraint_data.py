#!/usr/bin/env python3
"""
Database Constraint Validation Script
=====================================

Validates existing data before applying new database constraints.
Identifies violations that would prevent constraint addition.

Usage:
    python scripts/validate_constraint_data.py --report-only
    python scripts/validate_constraint_data.py --fix-violations
    python scripts/validate_constraint_data.py --detailed

Author: Database Architect AI
Date: 2025-10-02
Status: PRE-MIGRATION VALIDATION
"""

import sys
import os
from decimal import Decimal
from typing import List, Dict, Tuple
from datetime import datetime
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.database import get_db

# Validation Results Storage
validation_results = {
    "orders": [],
    "order_items": [],
    "payments": [],
    "products": [],
    "users": [],
    "foreign_keys": [],
    "summary": {}
}

def print_header(message: str):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {message}")
    print(f"{'='*80}\n")

def print_result(check_name: str, violations: int, severity: str = "HIGH"):
    """Print validation result"""
    status = "✅ PASS" if violations == 0 else f"❌ FAIL ({violations} violations)"
    severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
    print(f"{severity_icon.get(severity, '⚪')} {check_name:50s} {status}")

# =============================================================================
# ORDERS TABLE VALIDATION
# =============================================================================

def validate_orders_table(session: Session) -> Dict:
    """Validate orders table data for constraint compliance"""
    print_header("ORDERS TABLE VALIDATION")

    results = {
        "negative_subtotal": 0,
        "negative_tax": 0,
        "negative_shipping": 0,
        "negative_discount": 0,
        "zero_or_negative_total": 0,
        "calculation_mismatch": 0,
        "invalid_status": 0
    }

    # Check for negative subtotals
    query = text("SELECT COUNT(*) FROM orders WHERE subtotal < 0")
    results["negative_subtotal"] = session.execute(query).scalar()
    print_result("Negative subtotals", results["negative_subtotal"], "CRITICAL")

    # Check for negative tax amounts
    query = text("SELECT COUNT(*) FROM orders WHERE tax_amount < 0")
    results["negative_tax"] = session.execute(query).scalar()
    print_result("Negative tax amounts", results["negative_tax"], "CRITICAL")

    # Check for negative shipping costs
    query = text("SELECT COUNT(*) FROM orders WHERE shipping_cost < 0")
    results["negative_shipping"] = session.execute(query).scalar()
    print_result("Negative shipping costs", results["negative_shipping"], "CRITICAL")

    # Check for negative discounts
    query = text("SELECT COUNT(*) FROM orders WHERE discount_amount < 0")
    results["negative_discount"] = session.execute(query).scalar()
    print_result("Negative discounts", results["negative_discount"], "HIGH")

    # Check for zero or negative totals
    query = text("SELECT COUNT(*) FROM orders WHERE total_amount <= 0")
    results["zero_or_negative_total"] = session.execute(query).scalar()
    print_result("Zero/negative order totals", results["zero_or_negative_total"], "CRITICAL")

    # Check for calculation mismatches (tolerance 0.01 for float precision)
    query = text("""
        SELECT COUNT(*) FROM orders
        WHERE ABS(total_amount - (subtotal + tax_amount + shipping_cost - discount_amount)) > 0.01
    """)
    results["calculation_mismatch"] = session.execute(query).scalar()
    print_result("Order total calculation mismatches", results["calculation_mismatch"], "HIGH")

    # Check for invalid status values (should be enum)
    valid_statuses = ['PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'REFUNDED']
    query = text("""
        SELECT COUNT(*) FROM orders
        WHERE status NOT IN :statuses
    """)
    results["invalid_status"] = session.execute(query, {"statuses": tuple(valid_statuses)}).scalar()
    print_result("Invalid order statuses", results["invalid_status"], "MEDIUM")

    # Get sample violations if any
    if results["calculation_mismatch"] > 0:
        query = text("""
            SELECT id, order_number, subtotal, tax_amount, shipping_cost, discount_amount, total_amount,
                   (subtotal + tax_amount + shipping_cost - discount_amount) as calculated_total
            FROM orders
            WHERE ABS(total_amount - (subtotal + tax_amount + shipping_cost - discount_amount)) > 0.01
            LIMIT 5
        """)
        violations = session.execute(query).fetchall()
        print("\n📋 Sample calculation mismatches:")
        for v in violations:
            print(f"   Order {v.order_number}: Total={v.total_amount}, Should be={v.calculated_total}")

    validation_results["orders"] = results
    return results

# =============================================================================
# ORDER_ITEMS TABLE VALIDATION
# =============================================================================

def validate_order_items_table(session: Session) -> Dict:
    """Validate order_items table data for constraint compliance"""
    print_header("ORDER_ITEMS TABLE VALIDATION")

    results = {
        "zero_or_negative_quantity": 0,
        "zero_or_negative_price": 0,
        "calculation_mismatch": 0,
        "orphaned_items": 0
    }

    # Check for zero or negative quantities
    query = text("SELECT COUNT(*) FROM order_items WHERE quantity <= 0")
    results["zero_or_negative_quantity"] = session.execute(query).scalar()
    print_result("Zero/negative quantities", results["zero_or_negative_quantity"], "CRITICAL")

    # Check for zero or negative unit prices
    query = text("SELECT COUNT(*) FROM order_items WHERE unit_price <= 0")
    results["zero_or_negative_price"] = session.execute(query).scalar()
    print_result("Zero/negative unit prices", results["zero_or_negative_price"], "CRITICAL")

    # Check for calculation mismatches
    query = text("""
        SELECT COUNT(*) FROM order_items
        WHERE ABS(total_price - (unit_price * quantity)) > 0.01
    """)
    results["calculation_mismatch"] = session.execute(query).scalar()
    print_result("Item total calculation mismatches", results["calculation_mismatch"], "HIGH")

    # Check for orphaned order items (order doesn't exist)
    query = text("""
        SELECT COUNT(*) FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.id
        WHERE o.id IS NULL
    """)
    results["orphaned_items"] = session.execute(query).scalar()
    print_result("Orphaned order items", results["orphaned_items"], "HIGH")

    # Get sample violations
    if results["calculation_mismatch"] > 0:
        query = text("""
            SELECT id, product_name, quantity, unit_price, total_price,
                   (unit_price * quantity) as calculated_total
            FROM order_items
            WHERE ABS(total_price - (unit_price * quantity)) > 0.01
            LIMIT 5
        """)
        violations = session.execute(query).fetchall()
        print("\n📋 Sample calculation mismatches:")
        for v in violations:
            print(f"   Item {v.product_name}: Total={v.total_price}, Should be={v.calculated_total}")

    validation_results["order_items"] = results
    return results

# =============================================================================
# PAYMENTS TABLE VALIDATION
# =============================================================================

def validate_payments_table(session: Session) -> Dict:
    """Validate payments table data for constraint compliance"""
    print_header("PAYMENTS TABLE VALIDATION")

    results = {
        "zero_or_negative_amount": 0,
        "invalid_status": 0,
        "orphaned_payments": 0,
        "duplicate_references": 0
    }

    # Check for zero or negative payment amounts
    query = text("SELECT COUNT(*) FROM payments WHERE amount_in_cents <= 0")
    results["zero_or_negative_amount"] = session.execute(query).scalar()
    print_result("Zero/negative payment amounts", results["zero_or_negative_amount"], "CRITICAL")

    # Check for invalid payment statuses
    query = text("""
        SELECT DISTINCT status FROM payments
    """)
    all_statuses = [row[0] for row in session.execute(query).fetchall()]
    # Just report unusual statuses, don't fail (payment status is String, not Enum)
    print(f"   Payment statuses found: {', '.join(all_statuses)}")

    # Check for orphaned payments (transaction doesn't exist)
    query = text("""
        SELECT COUNT(*) FROM payments p
        LEFT JOIN order_transactions ot ON p.transaction_id = ot.id
        WHERE ot.id IS NULL
    """)
    results["orphaned_payments"] = session.execute(query).scalar()
    print_result("Orphaned payments", results["orphaned_payments"], "HIGH")

    # Check for duplicate payment references
    query = text("""
        SELECT payment_reference, COUNT(*) as count
        FROM payments
        GROUP BY payment_reference
        HAVING COUNT(*) > 1
    """)
    duplicates = session.execute(query).fetchall()
    results["duplicate_references"] = len(duplicates)
    print_result("Duplicate payment references", results["duplicate_references"], "CRITICAL")

    if duplicates:
        print("\n📋 Duplicate payment references:")
        for dup in duplicates[:5]:
            print(f"   Reference {dup.payment_reference}: {dup.count} occurrences")

    validation_results["payments"] = results
    return results

# =============================================================================
# PRODUCTS TABLE VALIDATION
# =============================================================================

def validate_products_table(session: Session) -> Dict:
    """Validate products table data for constraint compliance"""
    print_header("PRODUCTS TABLE VALIDATION")

    results = {
        "negative_precio_venta": 0,
        "negative_precio_costo": 0,
        "negative_comision": 0,
        "negative_peso": 0,
        "invalid_status": 0
    }

    # Check for negative precio_venta
    query = text("SELECT COUNT(*) FROM products WHERE precio_venta < 0")
    results["negative_precio_venta"] = session.execute(query).scalar()
    print_result("Negative precio_venta", results["negative_precio_venta"], "HIGH")

    # Check for negative precio_costo
    query = text("SELECT COUNT(*) FROM products WHERE precio_costo < 0")
    results["negative_precio_costo"] = session.execute(query).scalar()
    print_result("Negative precio_costo", results["negative_precio_costo"], "HIGH")

    # Check for negative comision
    query = text("SELECT COUNT(*) FROM products WHERE comision_mestocker < 0")
    results["negative_comision"] = session.execute(query).scalar()
    print_result("Negative commission", results["negative_comision"], "HIGH")

    # Check for negative peso
    query = text("SELECT COUNT(*) FROM products WHERE peso < 0")
    results["negative_peso"] = session.execute(query).scalar()
    print_result("Negative weight", results["negative_peso"], "MEDIUM")

    # Check for invalid product statuses
    valid_statuses = ['DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'TRANSITO', 'VERIFICADO', 'DISPONIBLE', 'VENDIDO', 'INACTIVE']
    query = text("""
        SELECT COUNT(*) FROM products
        WHERE status NOT IN :statuses
    """)
    results["invalid_status"] = session.execute(query, {"statuses": tuple(valid_statuses)}).scalar()
    print_result("Invalid product statuses", results["invalid_status"], "MEDIUM")

    validation_results["products"] = results
    return results

# =============================================================================
# USERS TABLE VALIDATION
# =============================================================================

def validate_users_table(session: Session) -> Dict:
    """Validate users table data for constraint compliance"""
    print_header("USERS TABLE VALIDATION")

    results = {
        "invalid_email_format": 0,
        "duplicate_emails": 0,
        "duplicate_cedulas": 0,
        "invalid_security_clearance": 0,
        "invalid_performance_score": 0,
        "invalid_user_type": 0
    }

    # Basic email format validation (simple check)
    query = text("""
        SELECT COUNT(*) FROM users
        WHERE email NOT LIKE '%@%' OR email NOT LIKE '%.%'
    """)
    results["invalid_email_format"] = session.execute(query).scalar()
    print_result("Invalid email format", results["invalid_email_format"], "HIGH")

    # Check for duplicate emails (should be caught by UNIQUE constraint)
    query = text("""
        SELECT email, COUNT(*) as count
        FROM users
        GROUP BY email
        HAVING COUNT(*) > 1
    """)
    duplicates = session.execute(query).fetchall()
    results["duplicate_emails"] = len(duplicates)
    print_result("Duplicate emails", results["duplicate_emails"], "CRITICAL")

    # Check for duplicate cedulas
    query = text("""
        SELECT cedula, COUNT(*) as count
        FROM users
        WHERE cedula IS NOT NULL
        GROUP BY cedula
        HAVING COUNT(*) > 1
    """)
    duplicates = session.execute(query).fetchall()
    results["duplicate_cedulas"] = len(duplicates)
    print_result("Duplicate cedulas", results["duplicate_cedulas"], "HIGH")

    # Check security clearance range (1-5)
    query = text("""
        SELECT COUNT(*) FROM users
        WHERE security_clearance_level IS NOT NULL
        AND (security_clearance_level < 1 OR security_clearance_level > 5)
    """)
    results["invalid_security_clearance"] = session.execute(query).scalar()
    print_result("Invalid security clearance", results["invalid_security_clearance"], "MEDIUM")

    # Check performance score range (0-100)
    query = text("""
        SELECT COUNT(*) FROM users
        WHERE performance_score IS NOT NULL
        AND (performance_score < 0 OR performance_score > 100)
    """)
    results["invalid_performance_score"] = session.execute(query).scalar()
    print_result("Invalid performance score", results["invalid_performance_score"], "MEDIUM")

    # Check for invalid user types
    valid_types = ['BUYER', 'VENDOR', 'ADMIN', 'SUPERUSER', 'SYSTEM']
    query = text("""
        SELECT COUNT(*) FROM users
        WHERE user_type NOT IN :types
    """)
    results["invalid_user_type"] = session.execute(query, {"types": tuple(valid_types)}).scalar()
    print_result("Invalid user types", results["invalid_user_type"], "HIGH")

    validation_results["users"] = results
    return results

# =============================================================================
# FOREIGN KEY INTEGRITY VALIDATION
# =============================================================================

def validate_foreign_key_integrity(session: Session) -> Dict:
    """Validate foreign key relationships"""
    print_header("FOREIGN KEY INTEGRITY VALIDATION")

    results = {
        "orders_missing_buyers": 0,
        "order_items_missing_orders": 0,
        "order_items_missing_products": 0,
        "payments_missing_transactions": 0,
        "order_transactions_missing_orders": 0
    }

    # Orders with missing buyers
    query = text("""
        SELECT COUNT(*) FROM orders o
        LEFT JOIN users u ON o.buyer_id = u.id
        WHERE u.id IS NULL
    """)
    results["orders_missing_buyers"] = session.execute(query).scalar()
    print_result("Orders with missing buyers", results["orders_missing_buyers"], "CRITICAL")

    # Order items with missing orders (already checked above, but good to verify)
    query = text("""
        SELECT COUNT(*) FROM order_items oi
        LEFT JOIN orders o ON oi.order_id = o.id
        WHERE o.id IS NULL
    """)
    results["order_items_missing_orders"] = session.execute(query).scalar()
    print_result("Order items with missing orders", results["order_items_missing_orders"], "CRITICAL")

    # Order items with missing products
    query = text("""
        SELECT COUNT(*) FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE p.id IS NULL
    """)
    results["order_items_missing_products"] = session.execute(query).scalar()
    print_result("Order items with missing products", results["order_items_missing_products"], "HIGH")

    # Payments with missing transactions
    query = text("""
        SELECT COUNT(*) FROM payments p
        LEFT JOIN order_transactions ot ON p.transaction_id = ot.id
        WHERE ot.id IS NULL
    """)
    results["payments_missing_transactions"] = session.execute(query).scalar()
    print_result("Payments with missing transactions", results["payments_missing_transactions"], "CRITICAL")

    # Order transactions with missing orders
    query = text("""
        SELECT COUNT(*) FROM order_transactions ot
        LEFT JOIN orders o ON ot.order_id = o.id
        WHERE o.id IS NULL
    """)
    results["order_transactions_missing_orders"] = session.execute(query).scalar()
    print_result("Transactions with missing orders", results["order_transactions_missing_orders"], "CRITICAL")

    validation_results["foreign_keys"] = results
    return results

# =============================================================================
# SUMMARY AND REPORTING
# =============================================================================

def generate_summary():
    """Generate validation summary"""
    print_header("VALIDATION SUMMARY")

    total_violations = 0
    critical_violations = 0
    high_violations = 0

    for table, results in validation_results.items():
        if table == "summary":
            continue
        for check, count in results.items():
            total_violations += count
            # Categorize by severity (approximation)
            if "negative" in check or "zero" in check or "orphaned" in check or "missing" in check:
                critical_violations += count
            elif "calculation" in check or "duplicate" in check:
                high_violations += count

    validation_results["summary"] = {
        "total_violations": total_violations,
        "critical_violations": critical_violations,
        "high_violations": high_violations,
        "timestamp": datetime.now().isoformat()
    }

    print(f"Total Violations Found: {total_violations}")
    print(f"  🔴 Critical: {critical_violations}")
    print(f"  🟠 High: {high_violations}")
    print(f"  🟡 Medium/Low: {total_violations - critical_violations - high_violations}")

    if total_violations == 0:
        print("\n✅ DATABASE IS READY FOR CONSTRAINT MIGRATION")
    else:
        print("\n❌ DATABASE HAS VIOLATIONS - MUST BE FIXED BEFORE MIGRATION")
        print("\nRecommendations:")
        if critical_violations > 0:
            print("  1. Fix critical violations immediately (data corruption risk)")
        if high_violations > 0:
            print("  2. Review and fix high-priority violations")
        print("  3. Run validation again after fixes")
        print("  4. Consider data backup before applying constraints")

    return validation_results

def save_report(results: Dict, filename: str = "constraint_validation_report.json"):
    """Save validation report to JSON file"""
    filepath = os.path.join("scripts", filename)
    with open(filepath, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {filepath}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main execution function"""
    print_header("DATABASE CONSTRAINT VALIDATION")
    print(f"Database: {settings.DATABASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        # Run all validations
        validate_orders_table(session)
        validate_order_items_table(session)
        validate_payments_table(session)
        validate_products_table(session)
        validate_users_table(session)
        validate_foreign_key_integrity(session)

        # Generate summary
        summary = generate_summary()

        # Save report
        save_report(summary)

        # Return exit code based on violations
        if summary["summary"]["critical_violations"] > 0:
            print("\n❌ VALIDATION FAILED - Critical violations found")
            sys.exit(1)
        elif summary["summary"]["total_violations"] > 0:
            print("\n⚠️ VALIDATION WARNING - Some violations found")
            sys.exit(2)
        else:
            print("\n✅ VALIDATION PASSED - No violations found")
            sys.exit(0)

    except Exception as e:
        print(f"\n❌ ERROR during validation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
    finally:
        session.close()

if __name__ == "__main__":
    main()
